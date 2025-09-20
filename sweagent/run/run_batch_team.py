"""Run a team of agents on a batch of instances.

This module extends run_batch.py to support running a team of agents where each agent's configuration
comes from a separate YAML file.
"""

import logging
import random
import time
import traceback
from pathlib import Path
from typing import List, Self

import yaml
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from swerex.deployment.hooks.status import SetStatusDeploymentHook

from sweagent.agent.agents import AgentConfig, DefaultAgentConfig, get_agent_from_config
from sweagent.agent.hooks.status import SetStatusAgentHook
from sweagent.agent.team_agents import Team, TeamConfig
from sweagent.environment.hooks.status import SetStatusEnvironmentHook
from sweagent.environment.swe_env import SWEEnv
from sweagent.exceptions import ModelConfigurationError, TotalCostLimitExceededError
from sweagent.run._progress import RunBatchProgressManager
from sweagent.run.batch_instances import BatchInstance, BatchInstanceSourceConfig
from sweagent.run.common import BasicCLI, ConfigHelper, save_predictions
from sweagent.run.hooks.abstract import CombinedRunHooks, RunHook
from sweagent.run.hooks.apply_patch import SaveApplyPatchHook
from sweagent.run.run_batch import RunBatch, RunBatchConfig, _BreakLoop
from sweagent.run.run_single import RunSingleConfig
from sweagent.types import AgentRunResult
from sweagent.utils.config import load_environment_variables
from sweagent.utils.log import (
    add_file_handler,
    get_logger,
    register_thread_name,
    remove_file_handler,
)


class RunBatchTeamConfig(BaseSettings, cli_implicit_flags=False):
    """Configuration for running a team of agents on a batch of instances.
    
    This extends RunBatchConfig to support multiple agent config files.
    """
    instances: BatchInstanceSourceConfig = Field(description="Instances to run.")
    agent_config_paths: List[Path] = Field(description="Paths to agent configuration YAML files.")
    team_name: str = Field(default="team", description="Name for the team.")
    max_consecutive_turns: int = Field(default=3, description="Maximum consecutive turns an agent can take before rotation.")
    output_dir: Path = Field(default=Path("DEFAULT"), description="Output directory.")
    suffix: str = ""
    """Suffix to add to the output directory. Only used if `output_dir` is `DEFAULT`."""
    raise_exceptions: bool = False
    """Raise exceptions instead of skipping instances."""
    redo_existing: bool = False
    """Do not skip instances that already have a trajectory."""
    env_var_path: Path | None = None
    """Path to a .env file to load environment variables from."""
    num_workers: int = Field(default=1)
    """Number of parallel workers to use."""
    random_delay_multiplier: float = 0.3
    """We will wait for a random amount of time between 0 and `random_delay_multiplier`
    times the number of workers at the start of each instance. This is to avoid any
    potential race condition or issues with bottlenecks.
    """
    progress_bar: bool = True
    """Whether to show a progress bar. Progress bar is never shown for human models.
    Progress bar is always shown for multi-worker runs.
    """

    # pydantic config
    model_config = SettingsConfigDict(extra="forbid", env_prefix="SWE_AGENT_")
    
    @model_validator(mode="after")
    def evaluate_and_redo_existing(self) -> Self:
        """Validate that evaluate and redo_existing are not both True."""
        from sweagent.run.batch_instances import SWEBenchInstances
        
        if not isinstance(self.instances, SWEBenchInstances):
            return self
        if hasattr(self.instances, "evaluate") and self.instances.evaluate and self.redo_existing:
            msg = (
                "Cannot evaluate and redo existing at the same time. This would cause invalid results, because "
                "after the first merge_preds gives you a preds.json, this file would be submitted to SB-CLI, causing"
                "evaluation of old instances, which could then not be overwritten by the new ones."
            )
            raise ValueError(msg)
        return self

    # @classmethod
    # def from_dict(cls, config_dict: dict) -> Self:
    #     """Create a RunBatchTeamConfig from a dictionary."""
    #     return cls(**config_dict)


class RunBatchTeam(RunBatch):
    """Run a team of agents on a batch of instances.
    
    This class extends RunBatch to support teams where each agent's configuration
    comes from a separate YAML file.
    """
    
    def __init__(
        self,
        instances: list[BatchInstance],
        agent_config_paths: List[Path],
        team_name: str = "team",
        max_consecutive_turns: int = 3,
        *,
        output_dir: Path = Path("."),
        hooks: list[RunHook] | None = None,
        raise_exceptions: bool = False,
        redo_existing: bool = False,
        num_workers: int = 1,
        progress_bar: bool = True,
        random_delay_multiplier: float = 0.3,
    ):
        """Initialize a RunBatchTeam.
        
        Args:
            instances: List of problem instances to run
            agent_config_paths: Paths to YAML files containing agent configurations
            team_name: Name for the team
            max_consecutive_turns: Maximum consecutive turns an agent can take
            output_dir: Directory to save outputs
            hooks: Optional hooks to add
            raise_exceptions: Whether to raise exceptions or skip instances
            redo_existing: Whether to redo instances with existing trajectories
            num_workers: Number of parallel workers
            progress_bar: Whether to show a progress bar
            random_delay_multiplier: Random delay to avoid race conditions
        """
        self.logger = get_logger("swea-run-team", emoji="👥")
        add_file_handler(
            output_dir / "run_batch_team.log",
            id_="progress",
            filter=lambda name: "swea-run" in name or "config" in name,
        )
        
        # Load agent configurations from files
        self.agent_configs = self._load_agent_configs(agent_config_paths)
        if not self.agent_configs:
            raise ValueError("No valid agent configurations found")
            
        # Check for human models
        for config in self.agent_configs:
            if config.model.name in ["human", "human_thought"] and num_workers > 1:
                msg = "Cannot run with human model in parallel"
                raise ValueError(msg)
        
        # Initialize team properties
        self.team_name = team_name
        self.max_consecutive_turns = max_consecutive_turns
        
        # Store instance properties
        self.instances = instances
        self.output_dir = output_dir
        self._raise_exceptions = raise_exceptions
        self._chooks = CombinedRunHooks()
        self._redo_existing = redo_existing
        self._num_workers = min(num_workers, len(instances))
        
        # Add hooks
        for hook in hooks or [SaveApplyPatchHook(show_success_message=False)]:
            self.add_hook(hook)
            
        # Set up progress tracking
        self._progress_manager = RunBatchProgressManager(
            num_instances=len(instances), yaml_report_path=output_dir / "run_batch_team_exit_statuses.yaml"
        )
        self._show_progress_bar = progress_bar
        self._random_delay_multiplier = random_delay_multiplier
    
    def _load_agent_configs(self, config_paths: List[Path]) -> List[DefaultAgentConfig]:
        """Load agent configurations from YAML files.
        
        Args:
            config_paths: List of paths to YAML files
            
        Returns:
            List of DefaultAgentConfig objects
        """
        configs = []
        for path in config_paths:
            try:
                # Load YAML file
                with open(path, "r") as f:
                    config_dict = yaml.safe_load(f)
                
                # Extract agent configuration and convert to DefaultAgentConfig
                if "agent" in config_dict:
                    agent_config = DefaultAgentConfig.model_validate(config_dict["agent"])
                    configs.append(agent_config)
                    self.logger.info(f"Loaded agent configuration from {path}")
                else:
                    self.logger.warning(f"No 'agent' key found in {path}")
            except Exception as e:
                self.logger.error(f"Failed to load agent configuration from {path}: {e}")
        
        return configs
    
    @classmethod
    def from_config(cls, config: RunBatchTeamConfig) -> Self:
        """Create a RunBatchTeam from a RunBatchTeamConfig."""
        # Load environment variables if specified
        if config.env_var_path:
            load_environment_variables(config.env_var_path)
            
        # Handle DEFAULT output directory
        if config.output_dir == Path("DEFAULT"):
            from sweagent import TRAJECTORY_DIR
            date_str = time.strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = TRAJECTORY_DIR / f"{date_str}{config.suffix}"
        else:
            output_dir = config.output_dir
            
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get instances from config
        logger = get_logger("run-team", emoji="👥")
        logger.debug("Loading instances from %s", f"{config.instances!r}")
        instances = config.instances.get_instance_configs()
        logger.info("Loaded %d instances", len(instances))
        if not instances:
            msg = (
                "No instances to run. Here are a few things to check:\n"
                "- With huggingface data: Check that you have the right split (test or dev)\n"
                "- Check your filter does not exclude all instances (check the info log messages)"
            )
            raise ValueError(msg)
        logger.debug("The first instance is %s", f"{instances[0]!r}")
        
        # Create RunBatchTeam instance
        rb = cls(
            instances=instances,
            agent_config_paths=config.agent_config_paths,
            team_name=config.team_name,
            max_consecutive_turns=config.max_consecutive_turns,
            output_dir=output_dir,
            raise_exceptions=config.raise_exceptions,
            redo_existing=config.redo_existing,
            num_workers=config.num_workers,
            progress_bar=config.progress_bar,
            random_delay_multiplier=config.random_delay_multiplier,
        )
        
        # Add SWE-bench evaluation hook if needed
        from sweagent.run.batch_instances import SWEBenchInstances
        
        if isinstance(config.instances, SWEBenchInstances) and hasattr(config.instances, "evaluate") and config.instances.evaluate:
            from sweagent.run.hooks.swe_bench_evaluate import SweBenchEvaluate

            rb.add_hook(
                SweBenchEvaluate(
                    output_dir=output_dir,
                    subset=config.instances.subset,
                    split=config.instances.split,
                    continuous_submission_every=600,
                )
            )
            logger.info("Added SWE-bench evaluation hook")
            
        return rb
        
    def _run_instance(self, instance: BatchInstance) -> AgentRunResult:
        """Run a team of agents on a single instance.
        
        This method creates a Team with agents specified in the configuration files,
        and runs it on the given problem instance.
        
        Args:
            instance: The problem instance to run
            
        Returns:
            AgentRunResult containing the team's result
        """
        # Prepare output directory
        output_dir = Path(self.output_dir) / instance.problem_statement.id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Team instance
        # Clone the agent configs to avoid modifying the originals
        problem_agent_configs = [config.model_copy(deep=True) for config in self.agent_configs]
        
        # Keep the original agent names from the config files
        # We use a unique ID for each problem-agent combination but preserve the original names for logging
        for i, config in enumerate(problem_agent_configs):
            # Store the original agent name for display in logs
            self.logger.info(f"Agent '{config.name}' will run on problem {instance.problem_statement.id}")
            
        team_config = TeamConfig(
            name=f"{self.team_name}_{instance.problem_statement.id}",
            agent_configs=problem_agent_configs,
            max_consecutive_turns=self.max_consecutive_turns,
            type="team"
        )
        team = Team.from_config(team_config)
        
        # Create replay config
        # Note: We're using the first agent's config for the replay config, but this isn't
        # ideal. A better approach would be to create a proper TeamRunSingleConfig.
        single_run_replay_config = RunSingleConfig(
            agent=self.agent_configs[0],  # Using first agent as placeholder
            problem_statement=instance.problem_statement,
            env=instance.env,
        )
        
        # Save config
        config_yaml_path = output_dir / f"{instance.problem_statement.id}.config.yaml"
        config_yaml_path.write_text(yaml.dump(single_run_replay_config.model_dump_json(), indent=2))
        
        # Set replay config and add hook
        team.replay_config = single_run_replay_config
        team.add_hook(SetStatusAgentHook(instance.problem_statement.id, self._progress_manager.update_instance_status))
        
        # Set up environment
        self._progress_manager.update_instance_status(instance.problem_statement.id, "Starting environment")
        instance.env.name = f"{instance.problem_statement.id}"
        env = SWEEnv.from_config(instance.env)
        env.add_hook(
            SetStatusEnvironmentHook(instance.problem_statement.id, self._progress_manager.update_instance_status)
        )
        env.deployment.add_hook(
            SetStatusDeploymentHook(instance.problem_statement.id, self._progress_manager.update_instance_status)
        )
        
        # Run the team
        try:
            env.start()
            self._chooks.on_instance_start(index=0, env=env, problem_statement=instance.problem_statement)
            result = team.run(
                problem_statement=instance.problem_statement,
                env=env,
                output_dir=output_dir,
            )
        except Exception:
            # The actual handling is happening in `run_instance`, but we need to make sure that
            # we log it to the team's logger as well
            team.logger.error(traceback.format_exc())
            raise
        finally:
            env.close()
            
        # Save the results
        save_predictions(self.output_dir, instance.problem_statement.id, result)
        self._chooks.on_instance_completed(result=result)
        return result


def run_team_from_config(config: RunBatchTeamConfig):
    """Run a team of agents on a batch of instances using the given configuration."""
    batch = RunBatchTeam.from_config(config)
    return batch.main()


def run_team_from_cli(args: list[str] | None = None):
    """Run a team of agents on a batch of instances from the command line."""
    if args is None:
        args = sys.argv[1:]
    assert __doc__ is not None
    help_text = (  # type: ignore
        __doc__ + "\n[cyan][bold]=== ALL THE OPTIONS ===[/bold][/cyan]\n\n" + ConfigHelper().get_help(RunBatchTeamConfig)
    )
    run_team_from_config(BasicCLI(RunBatchTeamConfig, help_text=help_text).get_config(args))  # type: ignore


if __name__ == "__main__":
    run_team_from_cli()
