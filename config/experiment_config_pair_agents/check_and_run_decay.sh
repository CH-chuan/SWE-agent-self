#!/bin/bash

# === CONFIGURATION ===

TARGET_PID=510025

INITIAL_SLEEP_SECONDS=$((120 * 60))  # Start with 10 minutes
MIN_SLEEP_SECONDS=$((2 * 60))                    # Don't go below 3 minutes
DECAY_FACTOR=0.3

# === FUNCTION TO CHECK IF PROCESS IS RUNNING ===
is_running() {
    ps -p "$1" > /dev/null 2>&1
    return $?
}

SLEEP_SECONDS=$INITIAL_SLEEP_SECONDS

# === LOOP UNTIL TARGET PID IS GONE ===
while true; do
    if is_running "$TARGET_PID"; then
        echo "[$(date)] Process $TARGET_PID is still running. Sleeping for $((SLEEP_SECONDS / 60)) minutes..."
        sleep "$SLEEP_SECONDS"
        # Decay the sleep time
        SLEEP_SECONDS=$(awk "BEGIN {print int($SLEEP_SECONDS * $DECAY_FACTOR)}")
        # Clamp to minimum
        if [ "$SLEEP_SECONDS" -lt "$MIN_SLEEP_SECONDS" ]; then
            SLEEP_SECONDS=$MIN_SLEEP_SECONDS
        fi
    else
        echo "[$(date)] Process $TARGET_PID has finished. Launching new command..."

        nohup sweagent run-batch-team \
            --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/sweagent_driver_In.yaml \
            --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/sweagent_navigator_In.yaml \
            --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
            --output_dir trajectories/experiment_team/sweagent32b_personality_II \
        > trajectories/experiment_team/sweagent32b_personality_II.log 2>&1 &

        NEW_PID=$!
        echo "New process started with PID $NEW_PID"
        echo "$NEW_PID"
        break
    fi
done
