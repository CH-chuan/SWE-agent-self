from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Literal

from swerex.deployment.abstract import AbstractDeployment
from swerex.deployment.config import DeploymentConfig, DockerDeploymentConfig

class ApptainerDeploymentConfig(BaseModel):
    """Configuration for running locally in a Apptainer container."""

    image: str = "python:3.11"
    """The name of the Docker image to pull from Docker Hub."""
    port: int | None = None
    """The port that the docker container connects to. If None, a free port is found."""
    apptainer_args: list[str] = []
    """Additional arguments to pass to the apptainer run command."""
    startup_timeout: float = 180.0
    """The time to wait for the runtime to start."""
    pull: Literal["never", "always", "missing"] = "missing"
    """When to pull images from Docker Hub."""
    remove_images: bool = False
    """Whether to remove the Apptainer SIF file after it has stopped."""
    python_standalone_dir: str | None = None
    """The directory to use for the python standalone."""
    platform: str | None = None
    """The platform to use for the docker image."""

    type: Literal["apptainer"] = "apptainer"
    """Discriminator for (de)serialization/CLI. Do not change."""

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def validate_platform_args(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            return data

        apptainer_args = data.get("apptainer_args", [])
        platform = data.get("platform")

        # Apptainer doesn't use --platform directly, but we'll keep this logic for compatibility
        platform_arg_idx = next((i for i, arg in enumerate(apptainer_args) if arg.startswith("--platform")), -1)

        if platform_arg_idx != -1:
            if platform is not None:
                msg = "Cannot specify platform both via 'platform' field and '--platform' in apptainer_args"
                raise ValueError(msg)
            # Extract platform value from --platform argument
            if "=" in apptainer_args[platform_arg_idx]:
                # Handle case where platform is specified as --platform=value
                data["platform"] = apptainer_args[platform_arg_idx].split("=", 1)[1]
                data["apptainer_args"] = apptainer_args[:platform_arg_idx] + apptainer_args[platform_arg_idx + 1 :]
            elif platform_arg_idx + 1 < len(apptainer_args):
                data["platform"] = apptainer_args[platform_arg_idx + 1]
                # Remove the --platform and its value from apptainer_args
                data["apptainer_args"] = apptainer_args[:platform_arg_idx] + apptainer_args[platform_arg_idx + 2 :]
            else:
                msg = "--platform argument must be followed by a value"
                raise ValueError(msg)

        return data

    def get_deployment(self) -> AbstractDeployment:
        from .apptainer import ApptainerDeployment

        return ApptainerDeployment.from_config(self)


# Extend the original DeploymentConfig to include our new ApptainerDeploymentConfig
DeploymentConfig = ApptainerDeploymentConfig | DeploymentConfig | DockerDeploymentConfig
"""Union of all deployment configurations including ApptainerDeploymentConfig."""