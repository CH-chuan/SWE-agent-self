"""SweBench evaluation hook.

Will be automatically added to `run_batch` if `SWEBenchInstances.evaluate` is set to true
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from threading import Lock
from time import time
import traceback

from sweagent.run.hooks.abstract import RunHook
from sweagent.run.merge_predictions import merge_predictions
from sweagent.types import AgentRunResult
from sweagent.utils.log import get_logger

# new import for SWE-Bench
from swebench.harness.run_evaluation import run_instances
from swebench.harness.reporting import make_run_report
from json import loads
from swebench.harness.constants import KEY_PREDICTION, RUN_EVALUATION_LOG_DIR, LOG_REPORT

class SweBenchEvaluate(RunHook):
    _SUBSET_MAP = {"lite": "swe-bench_lite", "verified": "swe-bench_verified"}

    def __init__(self, output_dir: Path, subset: str, split: str, continuous_submission_every: int = 0) -> None:
        super().__init__()
        self.output_dir = output_dir
        self.subset = subset
        self.split = split
        self.continuous_submission_every = continuous_submission_every
        self.logger = get_logger("SB-evaluate", emoji="😬")
        self.merge_lock = Lock()
        self.last_evaluation_time = time()
        self.evaluation_interval = continuous_submission_every
        self._running_calls = []
        # We need to add a suffix to the run_id to avoid collisions when you reuse the name of your run
        self._time_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")

    @property
    def run_id(self) -> str:
        return f"{self.output_dir.name}_{self._time_suffix}"

    def _get_sb_call(self, preds_path: Path, submit_only: bool = False) -> list[str]:
        args = [
            "sb-cli",
            "submit",
            self._SUBSET_MAP[self.subset],
            self.split,
            "--predictions_path",
            str(preds_path),
            "--run_id",
            self.run_id,
            "--output_dir",
            str(self.output_dir / "sb-cli-reports"),
        ]
        if submit_only:
            args.extend(["--wait_for_evaluation", "0", "--gen_report", "0", "--verify_submission", "0"])
        return args

    def check_running_calls(self) -> None:
        """Warn if one of the running calls failed."""
        for call in self._running_calls:
            if call.poll() is not None:
                if call.returncode != 0:
                    self.logger.error("Failed to submit results to SweBench eval: %s", call.stderr.read())
                self._running_calls.remove(call)

    # used for continuous submission, i.e. continuously evaluate predictions
    def on_instance_completed(self, *, result: AgentRunResult):
        if self.evaluation_interval == 0:
            return
        print("function on_instance_completed at swe_bench_evaluate.py triggered")
        current_time = time()
        if current_time - self.last_evaluation_time < self.evaluation_interval:
            return

        with self.merge_lock:
            merge_predictions([self.output_dir], self.output_dir / "tmppreds.json")
            self.last_evaluation_time = current_time
        
        # Run local evaluation on the temporary predictions file
        tmp_preds_path = self.output_dir / "tmppreds.json"
        print(f"Evaluating predictions with file {tmp_preds_path}")
        self.run_local_evaluation(tmp_preds_path)
        
        # Remove temporary predictions file after evaluation
        if tmp_preds_path.exists():
            tmp_preds_path.unlink()

    def move_sb_cli_report(self) -> None:
        """Move report from `sb-cli-reports` to `results.json`."""
        output_dir = self.output_dir / "sb-cli-reports"
        if not output_dir.exists():
            self.logger.warning("No SweBench report found at %s", output_dir)
            return
        (self.output_dir / "results.json").unlink(missing_ok=True)
        reports = list(output_dir.glob("*.json"))
        if len(reports) != 1:
            self.logger.warning("Expected 1 SweBench report at %s, found %d. Cannot rename.", output_dir, len(reports))
            return
        reports[0].rename(self.output_dir / "results.json")

    def move_reports_to_results(self, report_dir: Path) -> None:
        """Move reports from the report directory to results.json."""
        if not report_dir.exists():
            self.logger.warning(f"No SweBench reports found at {report_dir}")
            return
            
        # Remove existing results.json if it exists
        results_path = self.output_dir / "results.json"
        results_path.unlink(missing_ok=True)
        
        # Find all JSON reports in the report directory
        reports = list(report_dir.glob("**/*.json"))
        
        if not reports:
            self.logger.warning(f"No SweBench reports found in {report_dir}")
            return
            
        # Combine all reports into a single results file
        combined_results = {}
        for report_path in reports:
            try:
                with open(report_path, 'r') as f:
                    report_data = loads(f.read())
                    combined_results.update(report_data)
            except Exception as e:
                self.logger.warning(f"Failed to read report {report_path}: {e}")
                
        # Write combined results to results.json
        with open(results_path, 'w') as f:
            import json
            json.dump(combined_results, f, indent=2)
            
        self.logger.info(f"Combined {len(reports)} reports into {results_path}")

    # run evaluation after finishing all instances
    def on_end(self) -> None:
        self.logger.info("Submitting results to SWE-Bench for evaluation")
        print("function on_end at swe_bench_evaluate.py triggered") 
        
        # Ensure predictions file exists
        preds_path = self.output_dir / "preds.json"
        if not preds_path.exists():
            self.logger.error(f"Predictions file not found at {preds_path}")
            return
            
        self.run_local_evaluation(preds_path)

    def run_local_evaluation(self, preds_path: Path) -> None:
        """Run local evaluation on the predictions file.
        
        This method can be called from both on_end and on_instance_completed.
        
        Args:
            preds_path: Path to the predictions file
        """
        try:
            # Load predictions from file
            with open(preds_path, 'r') as f:
                predictions_data = loads(f.read())
            
            # The format in preds.json is different from what run_instances expects
            # Convert the nested dictionary format to the expected format
            predictions = {}
            for instance_id, pred_data in predictions_data.items():
                # Ensure the prediction has the required keys
                if "model_patch" in pred_data:
                    # Some implementations use model_patch instead of model_prediction
                    pred_data[KEY_PREDICTION] = pred_data.pop("model_patch")
                elif "model_prediction" in pred_data:
                    pred_data[KEY_PREDICTION] = pred_data.pop("model_prediction")
                
                predictions[instance_id] = pred_data
            # print(predictions.keys())  # Debugging
            # Set up parameters for run_instances
            dataset_name = self._SUBSET_MAP[self.subset]
            split = self.split
            run_id = self.run_id
            
            # Import necessary functions from run_evaluation.py
            from swebench.harness.utils import load_swebench_dataset
            
            # Load dataset to get instances
            instances = load_swebench_dataset(dataset_name, split)
            # only keep the instances that have predictions
            instances = [instance for instance in instances if instance["instance_id"] in predictions.keys()]
            
            if not instances:
                self.logger.error("No matching instances found in the dataset for the predictions")
                return
                
            self.logger.info(f"Running evaluation for {len(instances)} instances")
            for instance in instances:
                self.logger.info(f"Instance: {instance['instance_id']}")
                
            # Run evaluation
            run_instances(
                predictions=predictions,
                instances=instances,
                cache_level="instance",  # Default cache level
                clean=True,            # Clean images above the cache level after evaluation
                force_rebuild=True,    # Force rebuild
                max_workers=2,          # Use 2 workers by default
                run_id=run_id,
                timeout=600,            # 10 minute timeout
                namespace="swebench",
                instance_image_tag="latest",
                rewrite_reports=False
            )
            
            # Find and move reports from the RUN_EVALUATION_LOG_DIR to results.json
            self.move_reports_from_log_dir(RUN_EVALUATION_LOG_DIR, run_id)
            
        except Exception as e:
            self.logger.error(f"Failed to run SWE-Bench evaluation: {e}")
            traceback_str = traceback.format_exc()
            self.logger.error(f"Traceback: {traceback_str}")

    def move_reports_from_log_dir(self, log_dir: Path, run_id: str) -> None:
        """Find and move reports from the log directory to results.json and create a summary report."""
        # The reports are stored in log_dir/run_id/model_name/instance_id/report.json
        run_dir = log_dir / run_id
        if not run_dir.exists():
            self.logger.warning(f"No SweBench reports found at {run_dir}")
            return
        
        # Find all report.json files in the run directory
        reports = list(run_dir.glob(f"**/{LOG_REPORT}"))
        
        if not reports:
            self.logger.warning(f"No SweBench reports found in {run_dir}")
            return
        
        total_instances = 0
        # Combine all reports into a single results file
        combined_results = {}
        for report_path in reports:
            try:
                with open(report_path, 'r') as f:
                    report_data = loads(f.read())
                    # Extract instance_id from the path
                    instance_id = report_path.parent.name
                    combined_results[instance_id] = report_data[instance_id]
                    total_instances += 1
            except Exception as e:
                self.logger.warning(f"Failed to read report {report_path}: {e}")
        
        # Create a summary report
        summary_report = {}
        submitted_instances = set()
        completed_instances = set()
        resolved_instances = set()
        unresolved_instances = set()
        empty_patch_instances = set()
        error_instances = set()
        unstopped_instances = set()  # This should always be 0 in our implementation
        
        for instance_id, report in combined_results.items():
            # All instances in combined_results were submitted
            submitted_instances.add(instance_id)
            
            if report["patch_is_None"] or not report["patch_exists"]:
                # Instances that do not successfully generate patch
                empty_patch_instances.add(instance_id)
            elif not report["patch_successfully_applied"]:
                # Instances that generated patch but cannot apply to codebase
                error_instances.add(instance_id)
            elif report["patch_successfully_applied"] and report["resolved"]:
                # Instances that successfully applied patch and resolved issues
                resolved_instances.add(instance_id)
                completed_instances.add(instance_id)  # These are also completed
            elif report["patch_successfully_applied"] and not report["resolved"]:
                # Instances that successfully applied patch but didn't resolve issues
                unresolved_instances.add(instance_id)
                completed_instances.add(instance_id)  # These are also completed
        
        summary_report["metrics"] = {
            "total_instances": total_instances,
            "submitted_instances": len(submitted_instances),
            "completed_instances": len(completed_instances),
            "resolved_instances": len(resolved_instances),
            "unresolved_instances": len(unresolved_instances),
            "empty_patch_instances": len(empty_patch_instances),
            "error_instances": len(error_instances),
            "unstopped_instances": len(unstopped_instances),
        }

        summary_report["submitted_instances"] = list(submitted_instances)
        summary_report["completed_instances"] = list(completed_instances)
        summary_report["resolved_instances"] = list(resolved_instances)
        summary_report["unresolved_instances"] = list(unresolved_instances)
        summary_report["empty_patch_instances"] = list(empty_patch_instances)
        summary_report["error_instances"] = list(error_instances)
        summary_report["unstopped_instances"] = list(unstopped_instances)
        
        # Write combined results to results.json
        results_path = self.output_dir / "results.json"
        with open(results_path, 'w') as f:
            import json
            json.dump(combined_results, f, indent=2)
        # log where the results are written
        self.logger.info(f"Combined {len(reports)} reports into {results_path}")

        # Write summary report to summary.json
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, 'w') as f:
            import json
            json.dump(summary_report, f, indent=2)
        # log where the summary is written
        self.logger.info(f"Summary report written to {summary_path}")
            
        # Log the results
        self.logger.info(f"Submitted {len(submitted_instances)} instances")
        self.logger.info(f"Completed {len(completed_instances)} instances")
        self.logger.info(f"Resolved {len(resolved_instances)} instances")
        self.logger.info(f"Unresolved {len(unresolved_instances)} instances")
        
        # Log the instance IDs for each category
        self.logger.info(f"Submitted instances: {', '.join(submitted_instances)}")
        self.logger.info(f"Completed instances: {', '.join(completed_instances)}")
        self.logger.info(f"Resolved instances: {', '.join(resolved_instances)}")
        self.logger.info(f"Unresolved instances: {', '.join(unresolved_instances)}")
