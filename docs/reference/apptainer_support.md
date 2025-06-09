# Apptainer Support

This document describes how Apptainer container support was added to the SWE-agent framework.

## Overview

Apptainer (formerly Singularity) is a container runtime designed for high-performance computing (HPC) environments and scientific computing workloads. It provides a more secure alternative to Docker for environments where privileged container execution is not permitted or desirable.

Key benefits of Apptainer:
- Runs without root/sudo privileges (unlike Docker)
- Designed for HPC, scientific computing, and multi-user environments
- Can directly convert and use Docker images
- Better security isolation model

## Implementation

Apptainer support was implemented by creating a parallel implementation to the existing Docker deployment system. The implementation consists of:

1. `ApptainerDeploymentConfig` - Configuration class for Apptainer deployments
2. `ApptainerDeployment` - Implementation of the deployment interface for Apptainer
3. Integration with the existing environment system

### Key Files

- `sweagent/environment/apptainer_support/config.py` - Contains the `ApptainerDeploymentConfig` class
- `sweagent/environment/apptainer_support/apptainer.py` - Contains the `ApptainerDeployment` class
- `sweagent/environment/swe_env.py` - Updated to support Apptainer deployments
- `sweagent/run/batch_instances.py` - Updated to use Apptainer deployments

### Key Differences from Docker

1. **Image Management:**
   - Docker uses local image repository with tags
   - Apptainer converts Docker images to SIF (Singularity Image Format) files
   - SIF files are stored in `~/.apptainer/cache/` with mangled filenames based on Docker image names

2. **Container Execution:**
   - Docker uses the daemon-based container management
   - Apptainer directly executes processes using the SIF image
   - Container lifecycle in Apptainer is managed through process management rather than container management

3. **Networking:**
   - Docker uses its own networking model with port mapping via `-p host:container`
   - Apptainer uses CNI plugins for networking with `--net --network-args=portmap=hostPort:containerPort/protocol` syntax

4. **File System Mounting:**
   - Docker uses volumes and bind mounts
   - Apptainer uses a different bind mount syntax

## Usage

### Configuration

Use the `ApptainerDeploymentConfig` class to configure Apptainer deployments:

```python
from sweagent.environment.apptainer_support.config import ApptainerDeploymentConfig

config = ApptainerDeploymentConfig(
    image="python:3.11",          # Docker image to pull
    port=8080,                    # Host port to map to container's port 8000
    apptainer_args=[],            # Additional Apptainer arguments
    pull="missing",               # Pull policy: "never", "always", or "missing"
    remove_images=False,          # Whether to remove SIF files after use
    python_standalone_dir=None,   # Directory for Python standalone
    platform="linux/amd64"        # Platform (mainly for compatibility)
)
```

### Integration with Environment System

The `DeploymentConfig` type was extended to include `ApptainerDeploymentConfig`, allowing it to be used anywhere the original deployment configurations could be used:

```python
# Import the extended DeploymentConfig that includes ApptainerDeploymentConfig
from sweagent.environment.apptainer_support.config import DeploymentConfig
```

### Using Apptainer in Batch Instances

```python
from sweagent.environment.apptainer_support.config import ApptainerDeploymentConfig

# In SWEBenchInstances configuration
if isinstance(self.deployment, ApptainerDeploymentConfig):
    self.deployment.platform = "linux/amd64"
```

## Implementation Details

### Image Management

The Apptainer implementation uses Docker Hub as the image source but converts Docker images to Apptainer SIF files:

1. Image paths are managed with `_get_image_sif_path(image)` which returns a path like `~/.apptainer/cache/image_tag.sif`
2. Image availability is checked using `_is_image_available(image)` which looks for the SIF file
3. Images are pulled using `apptainer pull --name=path docker://image`

### Container Execution

The container execution process:

1. The SIF file is located or pulled
2. A command is constructed using:
   ```
   apptainer run --contain --net --network-args=portmap={port}:8000/tcp {sif_path} {start_cmd}
   ```
3. Process management is used to track and control the container lifecycle

### Network Configuration

Networking is configured using:
- `--net` to enable networking
- `--network-args=portmap={port}:8000/tcp` to map ports

## Extending Further

For more advanced Apptainer features:

1. **Definition Files**: The implementation includes a basic Apptainer definition file generator that could be extended to support more complex container customizations.

2. **Filesystem Binds**: Additional filesystem binds could be added to support more complex use cases.

3. **Advanced Networking**: Additional CNI network configurations could be added.

## Troubleshooting

Common issues:

1. **Missing SIF Files**: Check if the SIF files exist in `~/.apptainer/cache/`
2. **Port Conflicts**: Ensure the specified port is not in use
3. **Permission Issues**: Apptainer may have different permission requirements than Docker
