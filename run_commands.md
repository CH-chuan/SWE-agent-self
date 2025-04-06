# Test Running Single Task
```bash
sweagent run \
    --config config/agent_configs/claude_example.yaml \
    --config config/single_problem_configs/test_problem_config.yaml
```

# Test Running Benchmark
```bash
sweagent run-batch \
    --config config/agent_configs/claude_example.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml
```

```bash
sweagent run-batch \
    --config config/agent_configs/azure_4omini_example.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml
```

```bash
sweagent run-batch \
    --config config/agent_configs/azure_4o_example.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml
```

```bash
sweagent run-batch \
    --config config/agent_configs/human.yaml \
    --config config/swe_bench_problem_configs/swebench_example.yaml
```

clear docker envs
```bash
docker stop $(docker ps -q)  # stop containers
docker rm $(docker ps -aq)  # remove containers
docker rmi -f $(docker images -q)  # remove images

# three actions in one line
docker stop $(docker ps -q) && docker rm $(docker ps -aq) && docker rmi -f $(docker images -q)
```

# example run-batch commands
```bash
sweagent run-batch \
    --config config/experiment_config/azure_4o_baseline.yaml \
    --config config/experiment_config/swebench_tasks.yaml \
    --output_dir trajectories/swe_bench_experiment/4o_baseline
```