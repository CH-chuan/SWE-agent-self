# Actual Run Commands for Experiment

## baseline (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_baseline \
  > trajectories/experiment_team/4o_baseline.log 2>&1 &
```
### round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_baseline_round2 \
  > trajectories/experiment_team/4o_baseline_round2.log 2>&1 &
```

## comprehensive role
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_comprehensive_role \
  > trajectories/experiment_team/4o_comprehensive_role.log 2>&1 &
```
### round 2
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/comprehensive_role/azure_4o_navigator.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_comprehensive_role_round2 \
  > trajectories/experiment_team/4o_comprehensive_role_round2.log 2>&1 &
```

## with personality
### E, E (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_EE \
  > trajectories/experiment_team/4o_personality_EE.log 2>&1 &
```

round 2 (running)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_EE_round2 \
  > trajectories/experiment_team/4o_personality_EE_round2.log 2>&1 &
```

round 3 (pending)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_EE_round3 \
  > trajectories/experiment_team/4o_personality_EE_round3.log 2>&1 &
```

### I, I (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_II \
  > trajectories/experiment_team/4o_personality_II.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_II_round2 \
  > trajectories/experiment_team/4o_personality_II_round2.log 2>&1 &
```

round 3 (pending)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_II_round3 \
  > trajectories/experiment_team/4o_personality_II_round3.log 2>&1 &
```

### I, E 
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_IE \
  > trajectories/experiment_team/4o_personality_IE.log 2>&1 &
```

round 2 (running)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_In.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_Ex.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_IE_round2 \
  > trajectories/experiment_team/4o_personality_IE_round2.log 2>&1 &
```

### E, I
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_EI \
  > trajectories/experiment_team/4o_personality_EI.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_driver_Ex.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Extraversion/azure_4o_navigator_In.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_EI_round2 \
  > trajectories/experiment_team/4o_personality_EI_round2.log 2>&1 &
```

### Con, Con
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Con.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Con.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_ConCon \
  > trajectories/experiment_team/4o_personality_ConCon.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Con.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Con.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_ConCon_round2 \
  > trajectories/experiment_team/4o_personality_ConCon_round2.log 2>&1 &
```

### Uncon, Uncon
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Uncon.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Uncon.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnconUncon \
  > trajectories/experiment_team/4o_personality_UnconUncon.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Uncon.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Uncon.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnconUncon_round2 \
  > trajectories/experiment_team/4o_personality_UnconUncon_round2.log 2>&1 &
```

### Con, Uncon
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Con.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Uncon.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_ConUncon \
  > trajectories/experiment_team/4o_personality_ConUncon.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Con.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Uncon.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_ConUncon_round2 \
  > trajectories/experiment_team/4o_personality_ConUncon_round2.log 2>&1 &
```

### Uncon, Con
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Uncon.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Con.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnconCon \
  > trajectories/experiment_team/4o_personality_UnconCon.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_driver_Uncon.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Conscientiousness/azure_4o_navigator_Con.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnconCon_round2 \
  > trajectories/experiment_team/4o_personality_UnconCon_round2.log 2>&1 &
```

### Open, Open
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Open.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Open.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_OpenOpen \
  > trajectories/experiment_team/4o_personality_OpenOpen.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Open.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Open.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_OpenOpen_round2 \
  > trajectories/experiment_team/4o_personality_OpenOpen_round2.log 2>&1 &
```

### Unopen, Unopen
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Unopen.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Unopen.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnopenUnopen \
  > trajectories/experiment_team/4o_personality_UnopenUnopen.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Unopen.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Unopen.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnopenUnopen_round2 \
  > trajectories/experiment_team/4o_personality_UnopenUnopen_round2.log 2>&1 &
```

### Open, Unopen
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Open.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Unopen.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_OpenUnopen \
  > trajectories/experiment_team/4o_personality_OpenUnopen.log 2>&1 &
```

round 2 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Open.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Unopen.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_OpenUnopen_round2 \
  > trajectories/experiment_team/4o_personality_OpenUnopen_round2.log 2>&1 &
```

### Unopen, Open
round 1 (finished)
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Unopen.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Open.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnopenOpen \
  > trajectories/experiment_team/4o_personality_UnopenOpen.log 2>&1 &
```

round 2
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_driver_Unopen.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Openness/azure_4o_navigator_Open.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnopenOpen_round2 \
  > trajectories/experiment_team/4o_personality_UnopenOpen_round2.log 2>&1 &
```


### Agr, Agr
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_driver_Agr.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_navigator_Agr.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_AgrAgr \
  > trajectories/experiment_team/4o_personality_AgrAgr.log 2>&1 &
```

### Unagr, Unagr
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_driver_Unagr.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_navigator_Unagr.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnagrUnagr \
  > trajectories/experiment_team/4o_personality_UnagrUnagr.log 2>&1 &
```

### Agr, Unagr
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_driver_Agr.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_navigator_Unagr.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_AgrUnagr \
  > trajectories/experiment_team/4o_personality_AgrUnagr.log 2>&1 &
```

### Unagr, Agr
```bash
nohup sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_driver_Unagr.yaml \
    --agent_config_paths config/experiment_config_pair_agents/personality_agents/Agreeableness/azure_4o_navigator_Agr.yaml \
    --config config/experiment_config_pair_agents/swebench_tasks_new.yaml \
    --output_dir trajectories/experiment_team/4o_personality_UnagrAgr \
  > trajectories/experiment_team/4o_personality_UnagrAgr.log 2>&1 &
```


# Test Running Single Task
```bash
sweagent run-batch-team \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_driver.yaml \
    --agent_config_paths config/experiment_config_pair_agents/azure_4o_baseline_navigator.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml \
    --output_dir trajectories/test_one_case
```

## Test with handoff tool
```bash
sweagent run-batch-team \
    --agent_config_paths config/handoff_tester.yaml \
    --agent_config_paths config/human.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml \
    --output_dir trajectories/experiment_team_test/handoff
```

## Test with question asking tool
```bash
sweagent run-batch-team \
    --agent_config_paths config/question_asking_tester.yaml \
    --agent_config_paths config/question_asking_respond.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml \
    --output_dir trajectories/experiment_team_test/handoff_question_asking
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
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_baseline
```
notice, find cost in debug log


Baseline no tips
```bash
sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Ex
```

```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
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
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_baseline_no_tips_round2 \
  > /dev/null 2>&1 &
```

## Extrovert
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Ex.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Ex_round2 \
  > /dev/null 2>&1 &
```

## Introvert
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_In.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_In \
  > /dev/null 2>&1 &
```

## Consentiousness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Con.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Con_round2 \
  > /dev/null 2>&1 &
```

## Unconsentiousness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Uncon.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Uncon \
  > /dev/null 2>&1 &
```

## Openness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Open.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Open \
  > /dev/null 2>&1 &
```

## Unopenness
```bash
nohup sweagent run-batch \
    --config config/experiment_config/personality_agents/azure_4o_no_tips_Unopen.yaml \
    --config config/experiment_config/swebench_tasks_new.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_no_tips_Unopen \
  > /dev/null 2>&1 &
```


*If some process being terminated and rerun, no log will be deleted for each instance. As a result, when analysis, remember to remove previous unfinished RUN!!!!!!!!*