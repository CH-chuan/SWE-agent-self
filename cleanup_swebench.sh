#!/bin/bash

# Cleanup script for SWE-Bench components
# Keeps only essential files needed for evaluation

echo "Cleaning up SWE-Bench components..."

# Create backup directory
BACKUP_DIR="/home/chuan/Projects/SWE-agent/swebench_backup_$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup original swebench directory
cp -r /home/chuan/Projects/SWE-agent/swebench "$BACKUP_DIR"
echo "Backed up original swebench directory to $BACKUP_DIR"

# Essential components to keep
ESSENTIAL_FILES=(
  "/home/chuan/Projects/SWE-agent/swebench/__init__.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/__init__.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/constants/__init__.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/constants/javascript.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/constants/python.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/run_evaluation.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/utils.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/docker_utils.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/docker_build.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/grading.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/reporting.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/test_spec/test_spec.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/test_spec/__init__.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/log_parsers/__init__.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/log_parsers/javascript.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/log_parsers/python.py"
  "/home/chuan/Projects/SWE-agent/swebench/harness/modal_eval/__init__.py"
)

# Essential directories to keep
ESSENTIAL_DIRS=(
  "/home/chuan/Projects/SWE-agent/swebench/harness/dockerfiles"
  "/home/chuan/Projects/SWE-agent/swebench/harness/test_spec"
  "/home/chuan/Projects/SWE-agent/swebench/harness/constants"
  "/home/chuan/Projects/SWE-agent/swebench/harness/log_parsers"
  "/home/chuan/Projects/SWE-agent/swebench/harness/modal_eval"
)

# Create temporary directory for essential files
TEMP_DIR="/home/chuan/Projects/SWE-agent/swebench_temp"
mkdir -p "$TEMP_DIR"

# Copy essential files to temporary directory
for file in "${ESSENTIAL_FILES[@]}"; do
  if [ -f "$file" ]; then
    # Create directory structure in temp dir
    target_dir="$TEMP_DIR/$(dirname "${file#/home/chuan/Projects/SWE-agent/}")"
    mkdir -p "$target_dir"
    cp "$file" "$target_dir/"
    echo "Preserved: $file"
  else
    echo "Warning: Essential file not found: $file"
  fi
done

# Copy essential directories to temporary directory
for dir in "${ESSENTIAL_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    target_dir="$TEMP_DIR/$(dirname "${dir#/home/chuan/Projects/SWE-agent/}")"
    mkdir -p "$target_dir"
    cp -r "$dir" "$target_dir/"
    echo "Preserved directory: $dir"
  else
    echo "Warning: Essential directory not found: $dir"
  fi
done

# Create simplified modal_eval/__init__.py if it doesn't exist
MODAL_INIT="$TEMP_DIR/swebench/harness/modal_eval/__init__.py"
mkdir -p "$(dirname "$MODAL_INIT")"
if [ ! -f "$MODAL_INIT" ]; then
  echo '# Simplified modal_eval module for SWE-Bench evaluation' > "$MODAL_INIT"
  echo "Created simplified modal_eval/__init__.py"
fi

# Update run_evaluation.py to remove modal_eval dependency
RUN_EVAL_FILE="$TEMP_DIR/swebench/harness/run_evaluation.py"
if [ -f "$RUN_EVAL_FILE" ]; then
  # Remove modal_eval imports
  sed -i '/from swebench.harness.modal_eval import/d' "$RUN_EVAL_FILE"
  
  # Update main function to handle modal parameter without using modal_eval
  sed -i 's/modal: bool,/modal: bool = False,/' "$RUN_EVAL_FILE"
  
  # Replace modal evaluation section with a simple message
  sed -i '/if modal:/,/return/c\    if modal:\n        # Modal evaluation is not supported in this simplified version\n        print("Modal evaluation is not supported in this simplified version.")\n        return' "$RUN_EVAL_FILE"
  
  echo "Updated run_evaluation.py to remove modal_eval dependency"
fi

# Update __init__.py to remove unnecessary imports
INIT_FILE="$TEMP_DIR/swebench/__init__.py"
if [ -f "$INIT_FILE" ]; then
  # Add run_instances to exports
  sed -i '/from swebench.harness.run_evaluation import/,/)/c\from swebench.harness.run_evaluation import (\n    run_instances,  # Export run_instances directly\n    main as run_evaluation,\n    clean_images,  # Import clean_images from run_evaluation\n)' "$INIT_FILE"
  
  # Remove versioning imports
  sed -i '/from swebench.versioning/,/)/d' "$INIT_FILE"
  
  echo "Updated __init__.py to remove unnecessary imports"
fi

# Remove original swebench directory
rm -rf /home/chuan/Projects/SWE-agent/swebench

# Move temporary directory to original location
mv "$TEMP_DIR/swebench" /home/chuan/Projects/SWE-agent/

# Remove temporary directory
rm -rf "$TEMP_DIR"

# Remove SWE-bench-docs if it exists
if [ -d "/home/chuan/Projects/SWE-agent/SWE-bench-docs" ]; then
  rm -rf /home/chuan/Projects/SWE-agent/SWE-bench-docs
  echo "Removed SWE-bench-docs directory"
fi

echo "Cleanup complete. Only essential SWE-Bench evaluation components remain."
echo "A backup of the original swebench directory is available at $BACKUP_DIR"
