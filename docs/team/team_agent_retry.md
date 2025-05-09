# Team Agent Retry Mechanism

## Overview

This document explains how the retry mechanism works in the team agent setup, particularly focusing on how retries are tracked and how they affect agent switching.

## How Retries Work

When an agent encounters an error (such as a syntax error in an edit command), the system uses a retry mechanism to allow the agent to correct itself:

1. The error is caught in `DefaultAgent.forward_with_handling()`
2. The failed step is added to the agent's trajectory via `add_step_to_trajectory(step)`
3. The agent is given another chance to correct the error through requerying the model
4. This process can repeat up to `max_requeries` times (default: 3)

## Retry Tracking

Retries are tracked in several ways:

1. **Trajectory**: Each retry attempt is added to the agent's trajectory
2. **Retry Counter**: The `current_step_retries` counter in `DefaultAgent` tracks retries within a single step
3. **Team Step Count**: The team's step counter is incremented to account for retries

## Agent Switching with Retries

In a team setup with multiple agents (e.g., driver and navigator), agent switching is controlled by:

1. **Max Consecutive Turns**: Each agent has a maximum number of consecutive turns it can take
2. **Retry Counting**: Retries can optionally count toward an agent's turn limit
3. **Dynamic Max Retries**: The maximum number of retries can be set dynamically based on remaining turns

## Recent Improvements

We've made several improvements to the retry mechanism:

1. **Fixed Retry Counter**: Added proper incrementing of the retry counter for all error types, including `_RetryWithOutput`
2. **Dynamic Max Retries**: Set max retries based on the agent's remaining turns to avoid wasting turns on retries
3. **Team Step Counting**: Updated the team step counter to account for retries
4. **Turn Attribution**: Count retries toward the agent's turn limit to enable more efficient handoffs

## Implementation Details

### Retry Counter Fix

The original code had a bug where `_RetryWithOutput` exceptions didn't increment the retry counter:

```python
except _RetryWithOutput as e:
    # Missing: n_format_fails += 1
    history = handle_error_with_retry(...)
```

This was fixed by adding the increment:

```python
except _RetryWithOutput as e:
    n_format_fails += 1  # Added this line
    self.current_step_retries += 1  # Track retries
    history = handle_error_with_retry(...)
```

### Dynamic Max Retries

We implemented dynamic max retries based on remaining turns:

```python
# Calculate remaining turns for this agent
remaining_turns = self._get_remaining_turns(agent.name)

# Set dynamic max_requeries based on remaining turns
if remaining_turns < 1:
    agent.max_requeries = 1  # Last turn gets only 1 retry
else:
    agent.max_requeries = min(original_max_requeries, remaining_turns)
```

### Team Step Counting

The team step counter is updated to account for retries:

```python
# Check if there were retries
if hasattr(agent, 'current_step_retries') and agent.current_step_retries > 0:
    # update the team step count
    self.team_step_count += agent.current_step_retries
    # Count retries toward the turn limit
    self.agent_consecutive_turns[agent.name] += min(agent.current_step_retries, 1)
```

## Best Practices

When configuring team agents with retry mechanisms:

1. Set appropriate `max_consecutive_turns` for each agent type (e.g., 3 for driver, 1 for navigator)
2. Consider the balance between allowing retries and forcing handoffs
3. Monitor retry patterns to identify recurring issues
4. Use the dynamic max retries feature to optimize turn usage

## Future Improvements

Potential future improvements include:

1. More sophisticated retry strategies based on error types
2. Learning from past retries to avoid similar errors
3. Better error feedback between agents during handoffs
4. Automatic detection of retry loops and forced handoffs