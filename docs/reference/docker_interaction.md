# Docker Container Interaction

This document explains how SWE-agent interacts with Docker containers to execute commands and maintain a consistent shell environment.

## Architecture Overview

SWE-agent uses an HTTP-based communication approach to interact with Docker containers. This architecture consists of several key components:

1. **SWEEnv**: The high-level environment class that provides methods for interacting with the container
2. **DockerDeployment**: Manages the Docker container lifecycle
3. **RemoteRuntime**: Handles communication with the server running inside the container
4. **BashAction**: Encapsulates bash commands to be executed in the container

## Command Execution Flow

When a bash command (like `ls -a`) is executed, it follows this path:

```
SWEEnv.communicate() → RemoteRuntime.run_in_session() → HTTP Request → Container Server → Bash Shell → Response
```

### Detailed Flow

1. **High-level API**: The process begins in `SWEEnv.communicate()` method
   ```python
   def communicate(self, input: str, timeout: int | float = 25, *, check: Literal["warn", "ignore", "raise"] = "ignore"):
       rex_check = "silent" if check else "ignore"
       r = asyncio.run(
           self.deployment.runtime.run_in_session(BashAction(command=input, timeout=timeout, check=rex_check))
       )
       output = r.output
       # ... error handling ...
       return output
   ```

2. **BashAction Creation**: The command string is wrapped in a `BashAction` object with parameters

3. **Remote Execution**: The action is passed to the runtime's `run_in_session()` method

4. **HTTP Request**: The action is converted to JSON and sent to the server in the container
   ```python
   def _request(self, endpoint: str, request: BaseModel | None, output_class: Any):
       response = requests.post(
           f"{self._api_url}/{endpoint}", 
           json=request.model_dump() if request else None, 
           headers=self._headers
       )
       self._handle_response_errors(response)
       return output_class(**response.json())
   ```

5. **Container Server**: Inside the container, a server process receives the request and executes the command

6. **Command Execution**: The server executes the command in a bash shell and captures the output

7. **Response**: The output is returned as an HTTP response, which is then parsed and returned to the caller

## Docker Container Setup

The Docker container is set up by the `DockerDeployment` class:

```python
async def start(self):
    # Pull Docker image if needed
    self._pull_image()
    
    # Find a free port if none is specified
    if self._config.port is None:
        self._config.port = find_free_port()
    
    # Generate a unique container name and authentication token
    self._container_name = self._get_container_name()
    token = self._get_token()
    
    # Start the container with the server command
    cmds = [
        "docker",
        "run",
        "--rm",
        "-p",
        f"{self._config.port}:8000",
        # ... other arguments ...
        image_id,
        *self._get_swerex_start_cmd(token),
    ]
    
    # Start the container
    self._container_process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Create a RemoteRuntime to communicate with the container
    self._runtime = RemoteRuntime.from_config(
        RemoteRuntimeConfig(port=self._config.port, timeout=self._runtime_timeout, auth_token=token)
    )
```

## Server Inside the Container

The container runs a server process that:

1. Listens for HTTP requests on port 8000
2. Maintains bash sessions for executing commands
3. Executes commands and captures their output
4. Returns structured responses

This server is started with the command specified in `_get_swerex_start_cmd()`.

## Advantages of HTTP-based Communication

While not the standard approach for container interaction, HTTP-based communication offers several advantages:

1. **Stateful Sessions**: Maintains shell context between commands
2. **Structured Data**: Easy to pass complex data structures via JSON
3. **Authentication**: Simple token-based auth
4. **Flexibility**: Can implement custom endpoints for specific operations
5. **Cross-Language**: Can be accessed from any language that speaks HTTP

## Alternative Approaches

Alternative approaches for container interaction include:

1. **Docker SDK/API**:
   ```python
   import docker
   client = docker.from_env()
   container = client.containers.get('container_name')
   result = container.exec_run('ls -a')
   ```

2. **SSH-based Communication**:
   ```python
   import paramiko
   ssh = paramiko.SSHClient()
   ssh.connect('localhost', port=mapped_port, username='user', password='pass')
   stdin, stdout, stderr = ssh.exec_command('ls -a')
   ```

## Conclusion

The HTTP-based approach used in SWE-agent provides a flexible and powerful way to interact with Docker containers while maintaining shell state and handling structured data. While more complex than alternatives, it offers advantages for the specific requirements of the SWE-agent system.
