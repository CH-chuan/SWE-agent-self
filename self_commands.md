```bash
sweagent run --config config/agent_configs/agent_config_litellmproxy.yaml --config config/test_single_run_config/env_problem_config.yaml

sweagent run --config config/agent_configs/agent_config_claude.yaml --config config/test_single_run_config/env_problem_config.yaml

sweagent traj-to-demo /Users/chuan/Desktop/projects/SWE-agent/trajectories/chuan/claude_agent_config__claude-3-7-sonnet-20250219__t-0.60__p-1.00__c-5.00___875358/875358/875358.traj 
#  INFO      Saved demo to demos/SWE-agent__test-repo-i1/SWE-agent__test-repo-i1.demo.yaml    
```


```bash
sweagent run-batch --config config/agent_config_litellmproxy.yaml --config config/test_batch_config/batch_config.yaml
```



```bash
sweagent run-batch --config config/agent_config_litellmproxy.yaml --config config/test_batch_config/swebatch_config.yaml
```

```bash
sweagent run-batch --config config/agent_configs/agent_config_claude.yaml --config config/test_batch_config/swebatch_config.yaml
```