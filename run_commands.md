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