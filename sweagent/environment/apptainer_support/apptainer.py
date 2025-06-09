import logging
import os
import pathlib
import shlex
import subprocess
import time
import uuid
from typing import Any

from typing_extensions import Self

from swerex import PACKAGE_NAME, REMOTE_EXECUTABLE_NAME
from swerex.deployment.abstract import AbstractDeployment
from swerex.deployment.hooks.abstract import CombinedDeploymentHook, DeploymentHook
from swerex.exceptions import DeploymentNotStartedError
from swerex.runtime.abstract import IsAliveResponse
from swerex.runtime.config import RemoteRuntimeConfig
from swerex.runtime.remote import RemoteRuntime
from swerex.utils.free_port import find_free_port
from swerex.utils.log import get_logger
from swerex.utils.wait import _wait_until_alive

from .config import ApptainerDeploymentConfig

__all__ = ["ApptainerDeployment", "ApptainerDeploymentConfig"]


def _get_image_sif_path(image: str) -> pathlib.Path:
    """Convert Docker image name to Apptainer SIF file path."""
    # Replace special characters in image name to create a valid filename
    safe_name = image.replace('/', '_').replace(':', '_')
    return pathlib.Path(f"~/.apptainer/cache/{safe_name}.sif").expanduser()


def _is_image_available(image: str) -> bool:
    """Check if an Apptainer SIF file for the image exists."""
    sif_path = _get_image_sif_path(image)
    return sif_path.exists()

def _pull_image(image: str) -> bytes:
    """Pull a Docker image and convert it to Apptainer SIF format."""
    sif_path = _get_image_sif_path(image)
    # Create parent directory if it doesn't exist
    sif_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Pull from Docker Hub
        return subprocess.check_output(["apptainer", "pull", f"--name={str(sif_path)}", f"docker://{image}"], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # e.stderr contains the error message as bytes
        raise subprocess.CalledProcessError(e.returncode, e.cmd, e.output, e.stderr) from None


def _remove_image(image: str) -> None:
    """Remove Apptainer SIF file for the image."""
    sif_path = _get_image_sif_path(image)
    if sif_path.exists():
        sif_path.unlink()
    return None


class ApptainerDeployment(AbstractDeployment):
    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        """Deployment to local Apptainer container using Docker images.

        Args:
            **kwargs: Keyword arguments (see `ApptainerDeploymentConfig` for details).
        """
        self._config = ApptainerDeploymentConfig(**kwargs)
        self._runtime: RemoteRuntime | None = None
        self._container_process = None
        self._container_name = None
        self.logger = logger or get_logger("rex-deploy")
        self._runtime_timeout = 0.15
        self._hooks = CombinedDeploymentHook()

    def add_hook(self, hook: DeploymentHook):
        self._hooks.add_hook(hook)

    @classmethod
    def from_config(cls, config: ApptainerDeploymentConfig) -> Self:
        return cls(**config.model_dump())

    def _get_container_name(self) -> str:
        """Returns a unique instance name for the Apptainer container."""
        image_name_sanitized = "".join(c for c in self._config.image if c.isalnum() or c in "-_.")
        return f"{image_name_sanitized}-{uuid.uuid4()}"

    @property
    def container_name(self) -> str | None:
        return self._container_name

    async def is_alive(self, *, timeout: float | None = None) -> IsAliveResponse:
        """Checks if the runtime is alive. The return value can be
        tested with bool().

        Raises:
            DeploymentNotStartedError: If the deployment was not started.
        """
        if self._runtime is None:
            msg = "Runtime not started"
            raise RuntimeError(msg)
        if self._container_process is None:
            msg = "Container process not started"
            raise RuntimeError(msg)
        if self._container_process.poll() is not None:
            msg = "Container process terminated."
            output = "stdout:\n" + self._container_process.stdout.read().decode()  # type: ignore
            output += "\nstderr:\n" + self._container_process.stderr.read().decode()  # type: ignore
            msg += "\n" + output
            raise RuntimeError(msg)
        return await self._runtime.is_alive(timeout=timeout)

    async def _wait_until_alive(self, timeout: float = 10.0):
        try:
            return await _wait_until_alive(self.is_alive, timeout=timeout, function_timeout=self._runtime_timeout)
        except TimeoutError as e:
            self.logger.error("Runtime did not start within timeout. Here's the output from the container process.")
            self.logger.error(self._container_process.stdout.read().decode())  # type: ignore
            self.logger.error(self._container_process.stderr.read().decode())  # type: ignore
            assert self._container_process is not None
            await self.stop()
            raise e

    def _get_token(self) -> str:
        return str(uuid.uuid4())

    def _get_swerex_start_cmd(self, token: str) -> list[str]:
        rex_args = f"--auth-token {token}"
        pipx_install = "python3 -m pip install pipx && python3 -m pipx ensurepath"
        if self._config.python_standalone_dir:
            cmd = f"{self._config.python_standalone_dir}/python3.11/bin/{REMOTE_EXECUTABLE_NAME} {rex_args}"
        else:
            cmd = f"{REMOTE_EXECUTABLE_NAME} {rex_args} || ({pipx_install} && pipx run {PACKAGE_NAME} {rex_args})"
        # Need to wrap with /bin/sh -c to avoid having '&&' interpreted by the parent shell
        return [
            "/bin/sh",
            # "-l",
            "-c",
            cmd,
        ]

    def _pull_image(self) -> None:
        if self._config.pull == "never":
            return
        if self._config.pull == "missing" and _is_image_available(self._config.image):
            return
        self.logger.info(f"Pulling Docker image {self._config.image!r} to Apptainer SIF")
        self._hooks.on_custom_step("Pulling Docker image to Apptainer format")
        try:
            _pull_image(self._config.image)
        except subprocess.CalledProcessError as e:
            msg = f"Failed to pull image {self._config.image}. "
            msg += f"Error: {e.stderr.decode() if e.stderr else ''}"
            msg += f"Output: {e.output.decode() if e.output else ''}"
            raise RuntimeError(msg) from e

    @property
    def apptainer_def_file_content(self) -> str:
        """Generate an Apptainer definition file content for the container."""
        return (
            f"Bootstrap: docker\n"
            f"From: {self._config.image}\n\n"
            "%%post\n"
            "    apt-get update && apt-get install -y \
"
            "        python3 \
"
            "        python3-pip \
"
            "        && rm -rf /var/lib/apt/lists/*\n"
            f"    python3 -m pip install {PACKAGE_NAME}\n"
            f"    ln -sf $(which {REMOTE_EXECUTABLE_NAME}) /usr/local/bin/{REMOTE_EXECUTABLE_NAME}\n\n"
            "%%environment\n"
            "    export LC_ALL=C\n"
            "    export PYTHONUNBUFFERED=1\n\n"
            "%%startscript\n"
            f"    {REMOTE_EXECUTABLE_NAME} $@\n"
        )

    def _build_definition_file(self) -> pathlib.Path:
        """Creates an Apptainer definition file and returns its path."""
        self.logger.info(
            f"Creating Apptainer definition file for {self._config.image}."
        )
        
        # Create a temporary definition file
        def_file = pathlib.Path(f"/tmp/{self._container_name}.def")
        def_file.write_text(self.apptainer_def_file_content)
        
        return def_file

    async def start(self):
        """Starts the runtime using Apptainer."""
        self._pull_image()
        if self._config.port is None:
            self._config.port = find_free_port()
        assert self._container_name is None
        self._container_name = self._get_container_name()
        token = self._get_token()
        
        # Get path to the SIF file
        sif_path = _get_image_sif_path(self._config.image)
        
        # Build arguments for apptainer run
        cmds = [
            "apptainer",
            "run",
            "--contain",  # Isolate container from host
            "--net",     # Enable networking
            # Network port forwarding (format: hostPort:containerPort/protocol)
            f"--network-args=portmap={self._config.port}:8000/tcp",
            *self._config.apptainer_args,
            str(sif_path),  # Use the SIF file from Docker image
            *self._get_swerex_start_cmd(token),
        ]
        
        cmd_str = shlex.join(cmds)
        self.logger.info(
            f"Starting Apptainer instance {self._container_name} with image {self._config.image} serving on port {self._config.port}"
        )
        self.logger.debug(f"Command: {cmd_str!r}")
        
        # Start the Apptainer process
        self._container_process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self._hooks.on_custom_step("Starting runtime")
        self.logger.info(f"Starting runtime at {self._config.port}")
        
        # Configure the runtime
        self._runtime = RemoteRuntime.from_config(
            RemoteRuntimeConfig(port=self._config.port, timeout=self._runtime_timeout, auth_token=token)
        )
        
        # Wait for the runtime to be ready
        t0 = time.time()
        await self._wait_until_alive(timeout=self._config.startup_timeout)
        self.logger.info(f"Runtime started in {time.time() - t0:.2f}s")

    async def stop(self):
        """Stops the Apptainer runtime."""
        if self._runtime is not None:
            await self._runtime.close()
            self._runtime = None

        if self._container_process is not None:
            # Apptainer doesn't have a separate 'kill' command like Docker
            # Just terminate the process directly
            try:
                self._container_process.terminate()
                try:
                    self._container_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # If termination didn't work, try killing
                    self.logger.warning(
                        f"Failed to terminate Apptainer process for {self._container_name}. Trying SIGKILL."
                    )
                    for _ in range(3):
                        self._container_process.kill()
                        try:
                            self._container_process.wait(timeout=5)
                            break
                        except subprocess.TimeoutExpired:
                            continue
                    else:
                        self.logger.warning(f"Failed to kill Apptainer process {self._container_name} with SIGKILL")
            except Exception as e:
                self.logger.warning(f"Error stopping Apptainer container {self._container_name}: {e}", exc_info=True)

            self._container_process = None
            self._container_name = None

        # Remove the SIF file if configured
        if self._config.remove_images:
            if _is_image_available(self._config.image):
                self.logger.info(f"Removing Apptainer SIF file for {self._config.image}")
                try:
                    _remove_image(self._config.image)
                except Exception as e:
                    self.logger.error(f"Failed to remove Apptainer SIF file for {self._config.image}: {e}", exc_info=True)

    @property
    def runtime(self) -> RemoteRuntime:
        """Returns the runtime if running.

        Raises:
            DeploymentNotStartedError: If the deployment was not started.
        """
        if self._runtime is None:
            raise DeploymentNotStartedError()
        return self._runtime
