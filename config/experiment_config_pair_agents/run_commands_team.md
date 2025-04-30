# Actual Run Commands for Experiment

## baseline
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks.yaml \
    --output_dir trajectories/experiment_team/4o_baseline \
  > trajectories/experiment_team/4o_baseline.log 2>&1 &
```
### round 2
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks.yaml \
    --output_dir trajectories/experiment_team/4o_baseline_round2 \
  > trajectories/experiment_team/4o_baseline_round2.log 2>&1 &
```

## comprehensive role
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks.yaml \
    --output_dir trajectories/experiment_team/4o_comprehensive_role_ \
  > trajectories/experiment_team/4o_comprehensive_role.log 2>&1 &
```
### round 2
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks.yaml \
    --output_dir trajectories/experiment_team/4o_comprehensive_role_round2 \
  > trajectories/experiment_team/4o_comprehensive_role_round2.log 2>&1 &
```

## no handoff tool
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/no_handoff_tool/azure_4o_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/no_handoff_tool/azure_4o_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks.yaml \
    --output_dir trajectories/experiment_team/4o_no_handoff_tool \
  > trajectories/experiment_team/4o_no_handoff_tool.log 2>&1 &
```


# Test Running Single Task
```bash
sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml \
    --output_dir trajectories/test_one_case
```

## Test with human as agent
```bash
sweagent run-batch-team \
    --agent_config_paths config/handoff_tester.yaml \
    --agent_config_paths config/human.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml \
    --output_dir trajectories/experiment_team/human
```


clear docker envs
```bash
docker stop $(docker ps -q)  # stop containers
docker rm $(docker ps -aq)  # remove containers
docker rmi -f $(docker images -q)  # remove images

# three actions in one line
docker stop $(docker ps -q) && docker rm $(docker ps -aq) && docker rmi -f $(docker images -q)
```

# run-batch commands
Baseline
```bash
sweagent run-batch \
    --config config/experiment_config/azure_4o_baseline.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_baseline
```
notice, find cost in debug log


Baseline no tips
```bash
sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Ex
```

```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Ex \
  > /dev/null 2>&1 &
```

# modify agent line and outputline!
*At most two batches run together!!!*
*If terminated, copy the previous one and rename, and re-run command directly*

## baseline
```bash
nohup sweagent run-batch \
    --config config/experiment_config/azure_4o_baseline_no_tips.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_baseline_no_tips_round2 \
  > /dev/null 2>&1 &
```

## Extrovert
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Ex_round2 \
  > /dev/null 2>&1 &
```

## Introvert
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_In.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_In \
  > /dev/null 2>&1 &
```

## Consentiousness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Con.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Con_round2 \
  > /dev/null 2>&1 &
```

## Unconsentiousness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Uncon.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Uncon \
  > /dev/null 2>&1 &
```

## Openness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Open.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Open \
  > /dev/null 2>&1 &
```

## Unopenness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Unopen.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Unopen \
  > /dev/null 2>&1 &
```


*If some process being terminated and rerun, no log will be deleted for each instance. As a result, when analysis, remember to remove previous unfinished RUN!!!!!!!!*