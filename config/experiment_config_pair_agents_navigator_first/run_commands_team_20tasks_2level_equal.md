# Actual Run Commands for Experiment

## baseline 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/azure_4o_baseline_navigator.yaml \
    --config config/experiment_config_pair_agents_reproduce_notice/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_team_reproduce_notice/4o_baseline \
  > trajectories/experiment_team_reproduce_notice/4o_baseline.log 2>&1 &
```

## with personality
### E, E 
round 1 (running)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents_reproduce_notice/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_team_reproduce_notice/4o_personality_EE \
  > trajectories/experiment_team_reproduce_notice/4o_personality_EE.log 2>&1 &
```

### I, I 
round 1 (running)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents_reproduce_notice/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_team_reproduce_notice/4o_personality_II \
  > trajectories/experiment_team_reproduce_notice/4o_personality_II.log 2>&1 &
```

### I, E 
round 1 
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents_reproduce_notice/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_team_reproduce_notice/4o_personality_IE \
  > trajectories/experiment_team_reproduce_notice/4o_personality_IE.log 2>&1 &
```


### E, I
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents_reproduce_notice/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents_reproduce_notice/tasks/swebench_tasks_20tasks_2_level_equal.yaml \
    --output_dir trajectories/experiment_team_reproduce_notice/4o_personality_EI \
  > trajectories/experiment_team_reproduce_notice/4o_personality_EI.log 2>&1 &
```

