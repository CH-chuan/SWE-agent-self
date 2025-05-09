from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Self
from jinja2 import Template
import copy

from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated

from sweagent.agent.agents import DefaultAgent, AbstractAgent, StepOutput, AgentRunResult
from sweagent.agent.agents import DefaultAgentConfig, AgentInfo
from sweagent.agent.hooks.abstract import AbstractAgentHook, CombinedAgentHook
from sweagent.environment.swe_env import SWEEnv
from sweagent.agent.problem_statement import ProblemStatement, ProblemStatementConfig
from sweagent.utils.log import get_logger


class TeamConfig(BaseModel):
    """Configuration for Team of agents that work together in a round-robin fashion."""
    name: str = "team"
    agent_configs: List[DefaultAgentConfig] = Field(..., description="List of agent configurations")
    max_consecutive_turns: int = Field(default=3, description="Default maximum number of consecutive turns any agent can take before rotating (can be overridden per-agent)")
    type: str = "team"
    model_config = ConfigDict(extra="forbid")


class Team(AbstractAgent):
    """A team of agents that take turns handling steps in the main run loop.
    
    Each step in the run loop is handled by a different DefaultAgent in sequence.
    The agents can only act one after another, maintaining the same overall run loop
    structure as DefaultAgent.
    """
    
    def __init__(self, agent_configs: List[DefaultAgentConfig], name: str = "team", max_consecutive_turns: int = 3):
        """Initialize a Team with multiple DefaultAgents.
        
        Args:
            agent_configs: List of agent configurations for each team member
            name: Name of the team
            max_consecutive_turns: Maximum number of consecutive turns an agent can take before handoff
        """
        self.name = name
        self.agent_configs = agent_configs
        self.agents = [DefaultAgent.from_config(config) for config in agent_configs]
        self.current_agent_idx = 0
        self.logger = get_logger("swea-team-agent", emoji="👥")
        
        # Agent turn tracking
        self.max_consecutive_turns = max_consecutive_turns
        # Track consecutive turns for each agent individually
        self.agent_consecutive_turns = {agent.name: 0 for agent in self.agents}
        # Agent-specific max consecutive turns (default to team value if not specified)
        self.agent_max_consecutive_turns = {agent.name: max_consecutive_turns for agent in self.agents}
        
        # Shared trajectory and info across all agents
        self._trajectory = []
        self.info = AgentInfo()
        
        # Team-wide step counter for continuous step numbering
        self.team_step_count = 0
        
        # Run specific attributes
        self._env: Optional[SWEEnv] = None
        self._problem_statement: Optional[ProblemStatement | ProblemStatementConfig] = None
        self.traj_path: Optional[Path] = None
        self._output_dir: Optional[Path] = None
        
        # Hook system
        self._chook = CombinedAgentHook()
        self._replay_config: Optional[BaseModel] = None
    
    @classmethod
    def from_config(cls, config: TeamConfig) -> Self:
        """Create a Team from a TeamConfig.
        
        Args:
            config: TeamConfig object
            
        Returns:
            Team instance
        """
        # Get default max_consecutive_turns from team config if available
        max_consecutive_turns = getattr(config, "max_consecutive_turns", 3)
        
        # Create the Team instance
        team = cls(
            agent_configs=config.agent_configs,
            name=config.name,
            max_consecutive_turns=max_consecutive_turns
        )
        
        # Assign individual agent max consecutive turns if specified in agent_configs
        for i, agent_config in enumerate(config.agent_configs):
            if hasattr(agent_config, "max_consecutive_turns"):
                # Store the agent-specific max_consecutive_turns in our dictionary
                agent_name = team.agents[i].name
                team.agent_max_consecutive_turns[agent_name] = agent_config.max_consecutive_turns
                team.logger.info(f"Agent {agent_name} has custom max_consecutive_turns={agent_config.max_consecutive_turns}")
                
        return team
    
    def add_hook(self, hook: AbstractAgentHook) -> None:
        """Add hook to the team and all agents.
        
        Args:
            hook: Hook to add
        """
        hook.on_init(agent=self)
        self._chook.add_hook(hook)
        
        # Also add hook to all individual agents
        for agent in self.agents:
            agent.add_hook(hook)
    
    @property
    def trajectory(self):
        """Get the trajectory."""
        return self._trajectory
    
    @property
    def replay_config(self) -> Optional[BaseModel]:
        """Get the replay config."""
        return self._replay_config
    
    @replay_config.setter
    def replay_config(self, value: BaseModel):
        """Set the replay config."""
        self._replay_config = value
        
        # Also set for all individual agents
        for agent in self.agents:
            agent.replay_config = value
    
    def setup(self, env: SWEEnv, problem_statement: ProblemStatement | ProblemStatementConfig, 
              output_dir: Path = Path(".")) -> None:
        """Setup the team for a new problem instance.
        
        This sets up all agents with the same environment and problem statement.
        
        Args:
            env: The environment to run the agents on
            problem_statement: The problem statement
            output_dir: Directory to save the trajectory to
        """
        self._env = env
        self._problem_statement = problem_statement
        self._output_dir = output_dir
        
        # Include problem ID in trajectory filename to avoid conflicts
        problem_id = problem_statement.id if hasattr(problem_statement, 'id') else "unknown"
        
        # Initialize shared trajectory path
        output_dir.mkdir(parents=True, exist_ok=True)
        self.traj_path = output_dir / f"{problem_id}_{self.name}.traj.json"
        
        # Set up each agent
        for agent in self.agents:
            agent.setup(env=env, problem_statement=problem_statement, output_dir=output_dir)
        
        # Trajectory path is now set in the setup method with problem ID included
    
    def _share_tool_results_only(self, source_agent: DefaultAgent, target_agent: DefaultAgent, step_output: StepOutput) -> None:
        """Share only tool execution results with another agent, not the original messages.
        
        Instead of sharing the agent's messages that requested tool calls, this method only
        shares the resulting observations from tool executions.
        
        Args:
            source_agent: The agent that executed the step
            target_agent: The agent to share results with
            step_output: The step output containing tool results
        """
        # Skip sharing if source agent doesn't use tools
        if hasattr(source_agent, 'not_using_tools') and source_agent.not_using_tools:
            self.logger.debug(f"Skipping tool result sharing from {source_agent.name} (not_using_tools=True)")
            return
            
        # Always treat step_output as a StepOutput object with attributes
        observation = getattr(step_output, 'observation', '')
            
        # Skip if there's no observation to share
        if not observation or not observation.strip():
            return
            
        # Get tool_calls, tool_call_ids, and state from step_output as an object
        tool_calls = getattr(step_output, 'tool_calls', None)
        tool_call_ids = getattr(step_output, 'tool_call_ids', None)
        state = getattr(step_output, 'state', {})
        
        # Create observation message for tool results only
        if tool_calls and tool_call_ids:
            # For Azure OpenAI, we need to include both the tool call and the tool result
            # First add a dummy assistant message with or without tool calls based on agent type
            history_item = {
                "role": "assistant", 
                "content": f"driver used tool: {step_output.action}", 
                "agent": source_agent.name,  # Add the agent field
                "message_type": "action"  # Ensure message_type is present for history processors
            }
                
            target_agent.history.append(history_item)
            
            # Format the observation with the appropriate template
            elided_chars = 0
            if len(observation) > target_agent.templates.max_observation_length:
                templates = [target_agent.templates.next_step_truncated_observation_template]
                elided_chars = len(observation) - target_agent.templates.max_observation_length
                observation_truncated = observation[:target_agent.templates.max_observation_length]
            else:
                templates = [target_agent.templates.next_step_template]
                observation_truncated = observation
                
            # Add observation as a tool result, conditionally passing tool_call_ids
            # based on whether the agent uses tools or not
            kwargs = {
                "observation": observation_truncated,
                "elided_chars": elided_chars,
                "max_observation_length": target_agent.templates.max_observation_length,
            }
            
            # Add state if it exists and is not empty
            if state:
                kwargs.update(state)
                
            target_agent._add_templated_messages_to_history(
                templates,
                **kwargs
            )
            
            self.logger.debug(f"Shared tool results from {source_agent.name} to {target_agent.name}")
        else:
            # For non-tool observations, add as regular environment feedback
            # Format the message as coming from the environment, not from another agent
            elided_chars = 0
            if len(observation) > target_agent.templates.max_observation_length:
                templates = [target_agent.templates.next_step_truncated_observation_template]
                elided_chars = len(observation) - target_agent.templates.max_observation_length
                observation_truncated = observation[:target_agent.templates.max_observation_length]
            else:
                templates = [target_agent.templates.next_step_template]
                observation_truncated = observation
                
            # Add the observation as environmental feedback with agent name
            # Create a custom history entry to ensure the agent field is present
            formatted_messages = []
            
            # Create format_dict with safe access to state
            format_dict_args = {
                'observation': observation_truncated,
                'elided_chars': elided_chars,
                'max_observation_length': target_agent.templates.max_observation_length,
            }
            
            # Add state if it exists
            if state:
                format_dict_args.update(state)
                
            format_dict = target_agent._get_format_dict(**format_dict_args)
            
            for template in templates:
                formatted_messages.append(Template(template).render(**format_dict))
                
            message = "\n".join(formatted_messages)
            target_agent.history.append({
                "role": "user",
                "content": f"[{target_agent.name}]: {message}",
                "agent": target_agent.name,
                "message_type": "observation",
            })
            
            self.logger.debug(f"Shared environmental observation from {source_agent.name} to {target_agent.name}")
    
    def _check_for_handoff(self, step_output: StepOutput) -> bool:
        """Check if the agent has requested a handoff to the next agent.
        
        Args:
            step_output: The step output to check for handoff tool calls
            
        Returns:
            True if handoff was requested, False otherwise
        """
        # Get the current agent
        current_agent = self.agents[self.current_agent_idx]
        
        # Check if handoff is enabled for this agent
        handoff_enabled = True
        if hasattr(current_agent, 'config') and hasattr(current_agent.config, 'tools'):
            handoff_enabled = getattr(current_agent.config.tools, 'enable_handoff_tool', True)
            
        # If handoff is disabled for this agent, always return False
        if not handoff_enabled:
            self.logger.debug(f"Handoff tool is disabled for agent {current_agent.name}")
            return False
            
        # Check if the action contains our special tool marker
        action = None
        if isinstance(step_output, dict):
            action = step_output.get("action", "")
        else:  # Object attribute access
            action = getattr(step_output, "action", "")
        
        # Check if the action is our special tool format for handoff
        if action and isinstance(action, str) and action.startswith("__SPECIAL_TOOL__"):
            import json
            try:
                tool_call_json = action[len("__SPECIAL_TOOL__"):]
                tool_call = json.loads(tool_call_json)
                if tool_call.get("function", {}).get("name", "").lower() == "handoff":
                    # Extract the handoff message if provided
                    message = ""
                    try:
                        args = tool_call.get("function", {}).get("arguments", "{}")
                        if isinstance(args, str):
                            args = json.loads(args)
                        elif isinstance(args, dict):
                            pass  # Already a dict
                        else:
                            args = {}
                        message = args.get("message", "")
                    except Exception:
                        pass  # Ignore parsing errors
                        
                    if message:
                        self.logger.info(f"Agent {current_agent.name} requested handoff with message: {message}")
                    else:
                        self.logger.info(f"Agent {current_agent.name} requested handoff")
                    return True
            except Exception as e:
                self.logger.warning(f"Error parsing special tool format: {e}")
        
        # Check if there are any tool calls in the step_output
        # Handle both dictionary and object types for step_output
        tool_calls = None
        
        # Get tool_calls based on the type of step_output
        if isinstance(step_output, dict):
            tool_calls = step_output.get("tool_calls", None)
        else:  # Object attribute access
            tool_calls = getattr(step_output, "tool_calls", None)
            
        if not tool_calls:
            return False
            
        # Look for a handoff tool call - now the handoff tool is properly registered
        # so we just need to check if it was used
        for tool_call in tool_calls:
            if tool_call.get("name", "").lower() == "handoff":
                message = ""
                # Extract the handoff message if provided
                try:
                    if isinstance(tool_call.get("arguments"), dict):
                        message = tool_call.get("arguments", {}).get("message", "")
                    elif isinstance(tool_call.get("arguments"), str):
                        # Try to parse JSON string arguments
                        import json
                        args = json.loads(tool_call.get("arguments", "{}"))
                        message = args.get("message", "")
                except Exception:
                    pass  # Ignore parsing errors
                
                if message:
                    self.logger.info(f"Agent {current_agent.name} requested handoff with message: {message}")
                else:
                    self.logger.info(f"Agent {current_agent.name} requested handoff")
                return True
                
        return False
    
    def _get_next_agent(self) -> DefaultAgent:
        """Get the next agent in the rotation if needed, or return the current agent.
        
        The agent will only be rotated if:
        1. The previous agent requested a handoff via the handoff tool
        2. The previous agent has taken its agent-specific max_consecutive_turns consecutive turns
        
        Returns:
            The agent that should take the next step
        """
        current_agent = self.agents[self.current_agent_idx]
        
        # Check if we should continue with the current agent
        # 1. If this is the first step, we always use the first agent
        # 2. If current agent has taken fewer than max_consecutive_turns, keep using it
        agent_turns = self.agent_consecutive_turns.get(current_agent.name, 0)
        
        # Get the agent-specific max consecutive turns from our dictionary
        agent_max_consecutive_turns = self.agent_max_consecutive_turns.get(current_agent.name, self.max_consecutive_turns)
        
        if agent_turns == 0 or agent_turns < agent_max_consecutive_turns:
            # Increment the turn counter for this agent
            self.agent_consecutive_turns[current_agent.name] = agent_turns + 1
            return current_agent
            
        # Otherwise, rotate to the next agent
        self.current_agent_idx = (self.current_agent_idx + 1) % len(self.agents)
        next_agent = self.agents[self.current_agent_idx]
        
        # Reset the consecutive turns counter for the new agent
        self.agent_consecutive_turns[next_agent.name] = 1
        self.logger.info(f"Switching to agent {next_agent.name} after {agent_max_consecutive_turns} consecutive turns")
        
        return self.agents[self.current_agent_idx]
    
    def step(self) -> StepOutput:
        """Run a step with the current or next agent based on turn rules.
        
        An agent can take multiple consecutive turns until either:
        1. The agent explicitly requests a handoff using the handoff tool
        2. The agent reaches its maximum number of consecutive turns
        
        Returns:
            StepOutput from the agent's step
        """
        # Determine which agent should take this step
        agent = self._get_next_agent()
        agent_turns = self.agent_consecutive_turns.get(agent.name, 0)
        remaining_turns = self._get_remaining_turns(agent.name)

        # Set dynamic max_requeries based on remaining turns
        # Store original value to restore it later
        original_max_requeries = agent.max_requeries
        
        # Set dynamic max_requeries based on remaining turns
        # If this is the last turn, limit to 1 retry
        if remaining_turns < 1:
            agent.max_requeries = 1
            self.logger.info(f"Agent {agent.name} is on last turn, limiting max_requeries to 1")
        else:
            agent.max_requeries = min(original_max_requeries, remaining_turns)
        
        # Increment team step counter for continuous step numbering
        self.team_step_count += 1
        self.logger.info(f"Agent {agent.name} is taking a step (team step {self.team_step_count}, agent turn {agent_turns})")
        
        try:
            # Have the current agent take a step
            step_raw = agent.step()

            # Check if there were retries
            if hasattr(agent, 'current_step_retries') and agent.current_step_retries > 0:
                self.logger.info(f"Agent {agent.name} had {agent.current_step_retries} retries during this step")
                # update the team step count
                self.team_step_count += agent.current_step_retries
                self.logger.info(f"Updated team step count to {self.team_step_count} due to retries")
                # Count retries toward the turn limit (more aggressive handoff)
                self.agent_consecutive_turns[agent.name] += min(agent.current_step_retries, 1)  # Count at most 1 extra turn
            
            # Ensure we have a proper StepOutput object, not a dictionary
            if isinstance(step_raw, dict):
                step_output = StepOutput(**step_raw)
                self.logger.warning(f"Agent {agent.name} returned a dictionary instead of StepOutput object. Converting to StepOutput.")
            else:
                step_output = step_raw
            
            # Check if the agent requested a handoff
            handoff_requested = self._check_for_handoff(step_output)
            if handoff_requested:
                # Force rotation to the next agent on the next step by maxing out this agent's turns
                agent_max_turns = getattr(agent, "max_consecutive_turns", self.max_consecutive_turns)
                self.agent_consecutive_turns[agent.name] = agent_max_turns
                self.logger.info(f"Agent {agent.name} explicitly requested handoff to next agent")
            
            # Share step information with other agents based on the source agent's sharing preferences
            to_share_content = f"[{agent.name}]: {step_output.thought}"
            to_share_step = copy.deepcopy(step_output)
            to_share_step.output = to_share_content # change output because output is the thing that the agent will actually query about, while thought is just for showing.
            for other_agent in self.agents:
                if other_agent != agent:
                    # Check if handoff was requested - if so, always share full context
                    # Otherwise use the agent's default sharing preference
                    if handoff_requested:
                        # When handoff is used, share full context (not just tool results)
                        self.logger.debug(f"Agent {agent.name} used handoff, sharing full context with {other_agent.name}")
                        # Create a special history entry for handoff
                        other_agent.add_step_to_history(to_share_step, name=agent.name)
                    elif hasattr(agent, "share_only_tool_results") and agent.share_only_tool_results:
                        # Only share observation/tool results, not the agent's messages requesting the tools
                        self._share_tool_results_only(agent, other_agent, to_share_step)
                        self.logger.debug(f"Agent {agent.name} shared only tool results with {other_agent.name}")
                    else:
                        # For agents with not_using_tools=True (like navigator), don't share any context
                        # to avoid creating a mock tool execution result in the other agent's history
                        if hasattr(agent, 'not_using_tools') and agent.not_using_tools:
                            # Create a minimal history entry with just the thought
                            # This avoids the "Your command ran successfully..." log message
                            other_agent._append_history({
                                "role": "assistant",
                                "content": to_share_step.thought,
                                "thought": to_share_step.thought,
                                "action": "",
                                "agent": agent.name,  # Use the source agent's name
                                "message_type": "non_tool_thought",
                            })
                            self.logger.debug(f"Agent {agent.name} shared only thought with {other_agent.name} (no tool execution)")
                        else:
                            # Share full step output including agent reasoning for normal agents
                            # step_copy = copy.deepcopy(to_share_step)
                            
                            # If the source agent doesn't use tools but the target agent does,
                            # we need to ensure we don't pass empty tool_calls arrays to Azure OpenAI
                            if hasattr(agent, 'not_using_tools') and agent.not_using_tools:
                                # Remove tool_calls and tool_call_ids to prevent Azure API errors
                                if hasattr(to_share_step, 'tool_calls'):
                                    delattr(to_share_step, 'tool_calls')
                                if hasattr(to_share_step, 'tool_call_ids'):
                                    delattr(to_share_step, 'tool_call_ids')
                        
                            other_agent.add_step_to_history(to_share_step, name=agent.name)
                            self.logger.debug(f"Agent {agent.name} shared full context with {other_agent.name}")
            
            # Update shared trajectory
            # We only add the latest step to avoid duplication
            if agent.trajectory and len(agent.trajectory) > 0:
                # Add only the last step from the agent's trajectory
                self._trajectory.append(agent.trajectory[-1])
                
            # Update info with key fields from the current agent's step
            # AgentInfo is a Pydantic model, so we should use attribute access
            # StepOutput should always be handled as an object with attributes
            if hasattr(step_output, 'submission') and step_output.submission:
                self.info["submission"] = step_output.submission
            if hasattr(step_output, 'exit_status') and step_output.exit_status:
                self.info["exit_status"] = step_output.exit_status
            
            # Also update model stats if available from the agent
            if hasattr(agent.model, "stats"):
                self.info["model_stats"] = agent.model.stats.model_dump()
            
            # Trigger hook
            self._chook.on_step_done(step=step_output, info=self.info)
            
            return 
        finally:
            # Restore original max_requeries
            agent.max_requeries = original_max_requeries
    
    def _get_remaining_turns(self, agent_name: str) -> int:
        """Calculate how many more consecutive turns an agent can take.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Number of remaining turns before handoff
        """
        current_turns = self.agent_consecutive_turns.get(agent_name, 0)
        max_turns = self.agent_max_consecutive_turns.get(agent_name, self.max_consecutive_turns)
        return max(0, max_turns - current_turns)

    def get_trajectory_data(self) -> Dict[str, Any]:
        """Get all data that we save in .traj files.
        
        Returns:
            Dict containing trajectory data
        """
        # Convert AgentInfo to dict for serialization
        return {
            "info": self.info,
            "trajectory": self._trajectory,
        }
    
    def save_trajectory(self) -> None:
        """Save the trajectory to disk."""
        if self.traj_path is None:
            self.logger.warning("Cannot save trajectory: traj_path is None")
            return
        
        data = self.get_trajectory_data()
        self.traj_path.write_text(json.dumps(data, indent=2))
    
    def run(self, env: SWEEnv, problem_statement: ProblemStatement | ProblemStatementConfig, 
            output_dir: Path = Path(".")) -> AgentRunResult:
        """Run the team of agents on a problem instance.
        
        This method contains the main loop that repeatedly calls `self.step()`
        until the problem is solved, with each step being handled by a different agent.
        
        Args:
            env: The environment to run the agents on
            problem_statement: The problem statement
            output_dir: Directory to save the trajectory to
            
        Returns:
            AgentRunResult containing info and trajectory
        """
        self.setup(env=env, problem_statement=problem_statement, output_dir=output_dir)
        
        # Run action/observation loop similar to DefaultAgent.run but with rotating agents
        self._chook.on_run_start()
        step_output = StepOutput()
        while not step_output.done:
            step_output = self.step()  # This rotates through agents
            self.save_trajectory()
        self._chook.on_run_done(trajectory=self.trajectory, info=self.info)
        
        self.logger.info(f"Team trajectory saved to {self.traj_path}")
        
        # Return final result
        data = self.get_trajectory_data()
        return AgentRunResult(info=data["info"], trajectory=data["trajectory"])
