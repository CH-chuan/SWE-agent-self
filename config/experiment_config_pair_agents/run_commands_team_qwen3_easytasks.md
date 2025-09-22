# Actual Run Commands for Experiment

## with personality
### E, E 
round 1 - round 5 (fini)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_EE \
  > trajectories/experiment_qwen/qwen3coder_personality_EE.log 2>&1 &
```

round 6,7 (running)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_EE_round6 \
  > trajectories/experiment_qwen/qwen3coder_personality_EE_round6.log 2>&1 &
```


### I, I 
round 1 -5 (fini)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_II \
  > trajectories/experiment_qwen/qwen3coder_personality_II.log 2>&1 &
```

round 6
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_II_round9 \
  > trajectories/experiment_qwen/qwen3coder_personality_II_round9.log 2>&1 &
```

## Con
### Con Con
round 1 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/qwen3coder_driver_Con.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/qwen3coder_navigator_Con.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_ConCon \
  > trajectories/experiment_qwen/qwen3coder_personality_ConCon.log 2>&1 &
```
