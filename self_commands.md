```bash
sweagent run --config config/litellmproxy_agent_config.yaml --config config/test_env.yaml

sweagent run --config config/claude_agent_config.yaml --config config/test_env.yaml

sweagent traj-to-demo /Users/chuan/Desktop/projects/SWE-agent/trajectories/chuan/claude_agent_config__claude-3-7-sonnet-20250219__t-0.60__p-1.00__c-5.00___875358/875358/875358.traj 
#  INFO      Saved demo to demos/SWE-agent__test-repo-i1/SWE-agent__test-repo-i1.demo.yaml    
```