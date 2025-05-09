# Handoff Tool Documentation

## Overview

The handoff tool is a specialized mechanism in the SWE-agent framework that enables explicit control passing between agents in a team setting. It allows one agent to intentionally transfer control to another agent, facilitating more coordinated and intentional collaboration in multi-agent systems.

## How It Works

The handoff tool is implemented as a command that agents can invoke to explicitly request a transfer of control to the next agent in the team rotation. This is particularly useful when an agent determines that another agent would be better suited to handle the current task or when a natural transition point has been reached.

### Tool Definition

The handoff tool is defined in `sweagent/tools/commands.py` as a `Command` object:

```python
HANDOFF_COMMAND = Command(
    name="handoff",
    signature="<message>",
    docstring="Pass control to the next agent in the team rotation",
    arguments=[
        Argument(
            name="message",
            type="string",
            description="Optional message to pass to the next agent explaining the handoff reason.",
            required=False,
        )
    ],
)
```

## Activation and Configuration

### Enabling the Handoff Tool

The handoff tool is disabled by default and must be explicitly enabled in the tool configuration. In `sweagent/tools/tools.py`, the `ToolConfig` class includes a configuration parameter:

```python
enable_handoff_tool: bool = False
```

To enable the handoff tool, this parameter must be set to `True` in the configuration.

### Team Configuration

The team behavior regarding handoffs can be configured through several parameters:

1. **Team-wide maximum consecutive turns**: Controls how many consecutive turns any agent can take before automatic handoff occurs.

   ```python
   max_consecutive_turns: int = Field(default=3, description="Default maximum number of consecutive turns any agent can take before rotating")
   ```

2. **Agent-specific maximum consecutive turns**: Each agent can have its own limit that overrides the team-wide setting.

   ```python
   # In DefaultAgentConfig
   max_consecutive_turns: int = 3
   ```

## Implementation Details

### Tool Registration

When `enable_handoff_tool` is set to `True` in the configuration, the `HANDOFF_COMMAND` is added to the list of available commands:

```python
# Add handoff command if enabled
if self.enable_handoff_tool:
    commands.append(HANDOFF_COMMAND)
    tool_sources[HANDOFF_COMMAND.name] = Path("<builtin>")
```

### Handoff Detection

The `Team._check_for_handoff` method in `sweagent/agent/team_agents.py` checks if an agent has requested a handoff by looking for the handoff tool call in the step output. It handles two formats:

1. Special tool format marker: `__SPECIAL_TOOL__`
2. Regular tool call with the name "handoff"

### Agent Rotation Logic

When a handoff is detected, the system forces the current agent to reach its maximum consecutive turns, triggering rotation to the next agent:

```python
# Check if the agent requested a handoff
handoff_requested = self._check_for_handoff(step_output)
if handoff_requested:
    # Force rotation to the next agent on the next step by maxing out this agent's turns
    agent_max_turns = getattr(agent, "max_consecutive_turns", self.max_consecutive_turns)
    self.agent_consecutive_turns[agent.name] = agent_max_turns
    self.logger.info(f"Agent {agent.name} explicitly requested handoff to next agent")
```

### Context Sharing

When a handoff occurs, the system shares the full context with the next agent, not just tool results:

```python
# When handoff is used, share full context (not just tool results)
self.logger.debug(f"Agent {agent.name} used handoff, sharing full context with {other_agent.name}")
# Create a special history entry for handoff
other_agent.add_step_to_history(to_share_step, name=agent.name)
```

## Usage Examples

### Agent Invoking Handoff

An agent can invoke the handoff tool with an optional message explaining the reason for the handoff:

```
handoff(message="I've completed the initial setup. Handing off to you to implement the core functionality.")
```

or simply:

```
handoff()
```

### Automatic Rotation

Even without explicit handoff requests, agents will automatically rotate after reaching their maximum consecutive turns:

```python
# Otherwise, rotate to the next agent
self.current_agent_idx = (self.current_agent_idx + 1) % len(self.agents)
next_agent = self.agents[self.current_agent_idx]
```

## Best Practices

1. **Explicit Handoffs**: Encourage agents to use explicit handoffs at logical transition points rather than relying on automatic rotation.

2. **Informative Messages**: When using handoff, include a clear message explaining the current state and why the handoff is occurring.

3. **Specialized Agents**: Design teams with specialized agents that handle different aspects of a task, using handoffs to transition between these specializations.

4. **Context Preservation**: Remember that handoffs preserve full context, while normal agent transitions might only share tool results depending on configuration.

## Related Features

### Agent-Specific Turn Limits

Each agent can have its own maximum consecutive turns limit, set during team initialization:

```python
# Agent-specific max consecutive turns (default to team value if not specified)
self.agent_max_consecutive_turns = {agent.name: max_consecutive_turns for agent in self.agents}
```

### Context Sharing Preferences

Agents can be configured to share only tool results or full context with other agents:

```python
# In DefaultAgentConfig
share_only_tool_results: bool = False
```

When a handoff occurs, full context is always shared regardless of this setting.
