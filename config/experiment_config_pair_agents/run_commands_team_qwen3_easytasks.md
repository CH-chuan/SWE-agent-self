# Actual Run Commands for Experiment

## with personality
### E, E 
round 1 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_EE \
  > trajectories/experiment_qwen/qwen3coder_personality_EE.log 2>&1 &
```

round 2 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/qwen3coder_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_30easy_tasks.yaml \
    --output_dir trajectories/experiment_qwen/qwen3coder_personality_EE_round2 \
  > trajectories/experiment_qwen/qwen3coder_personality_EE_round2.log 2>&1 &
```

round 3 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_EE_round3 \
  > trajectories/experiment_qwen/4o_personality_EE_round3.log 2>&1 &
```

round 4 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_EE_round4 \
  > trajectories/experiment_qwen/4o_personality_EE_round4.log 2>&1 &
```


### I, I 
round 1 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_II \
  > trajectories/experiment_qwen/4o_personality_II.log 2>&1 &
```

round 2 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_II_round2 \
  > trajectories/experiment_qwen/4o_personality_II_round2.log 2>&1 &
```

round 3 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_II_round3 \
  > trajectories/experiment_qwen/4o_personality_II_round3.log 2>&1 &
```

round 4 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_II_round4 \
  > trajectories/experiment_qwen/4o_personality_II_round4.log 2>&1 &
```

### I, E 
round 1 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_IE \
  > trajectories/experiment_qwen/4o_personality_IE.log 2>&1 &
```

round 2 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_IE_round2 \
  > trajectories/experiment_qwen/4o_personality_IE_round2.log 2>&1 &
```

### E, I
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_qwen/4o_personality_EI \
  > trajectories/experiment_qwen/4o_personality_EI.log 2>&1 &
```

