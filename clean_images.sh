#!/bin/bash
# cleanup_swebench.sh
# Usage: nohup ./cleanup_swebench.sh <PID_TO_WATCH> &

TARGET_PID=$1

if [ -z "$TARGET_PID" ]; then
  echo "Usage: $0 <PID_TO_WATCH>"
  exit 1
fi

echo "Starting cleanup loop. Watching PID: $TARGET_PID"

while kill -0 "$TARGET_PID" 2>/dev/null; do
  echo "[$(date)] Cleaning up unused swebench images and dangling images..."

  # Remove unused swebench images
  docker images "swebench*" --format "{{.Repository}}:{{.Tag}}" \
    | xargs -r docker rmi 2>/dev/null

  # Remove dangling images (<none>)
  docker images -f "dangling=true" -q \
    | xargs -r docker rmi 2>/dev/null

  echo "Cleanup done. Sleeping 5 minutes..."
  sleep 300
done

echo "Target process $TARGET_PID has terminated. Exiting cleanup script."