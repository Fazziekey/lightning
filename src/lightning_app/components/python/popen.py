import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

from lightning_app import LightningWork
from lightning_app.utilities.app_helpers import _collect_child_process_pids
from lightning_app.utilities.tracer import Tracer

logger = logging.getLogger(__name__)


class PopenPythonScript(LightningWork):
    def on_before_run(self):
        """Called before the python script is executed."""

    def on_after_run(self):
        """Called after the python script is executed."""

    def configure_tracer(self) -> Tracer:
        """Override this hook to customize your tracer when running PythonScript with ``mode=tracer``."""
        return Tracer()

    def __init__(
        self,
        script_path: Union[str, Path],
        script_args: Optional[Union[str, List[str]]] = None,
        env: Optional[Dict] = None,
        **kwargs,
    ):
        """The PopenPythonScript component enables to easily run a python script within a subprocess.

        Arguments:
            script_path: Path of the python script to run.
            script_path: The arguments to be passed to the script.
            env: Environment variables to be passed to the script.
            kwargs: LightningWork keyword arguments.

        Raises:
            FileNotFoundError: If the provided `script_path` doesn't exists.

        .. doctest::


            >>> from lightning_app.components.python import PopenPythonScript
            >>> f = open("a.py", "w")
            >>> f.write("print('Hello World !')")
            22
            >>> f.close()
            >>> python_script = PopenPythonScript("a.py")
            >>> python_script.run()
            >>> os.remove("a.py")

        In this example, the script will be launch with the :class:`~subprocess.Popen`.

        .. literalinclude:: ../../../examples/app_components/python/component_popen.py
            :language: python
        """
        super().__init__(**kwargs)
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"The provided `script_path` {script_path}` wasn't found.")
        self.script_path = str(script_path)
        if isinstance(script_args, str):
            script_args = script_args.split(" ")
        self.script_args = script_args if script_args else []
        self.env = env
        self.pid = None
        self.exit_code = None

    def run(self) -> None:
        self.on_before_run()
        self._run_with_subprocess_popen()
        self.on_after_run()
        return

    def _run_with_subprocess_popen(self) -> None:
        cmd = [sys.executable] + [self.script_path] + self.script_args

        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0, close_fds=True, env=self.env
        ) as proc:
            self.pid = proc.pid
            if proc.stdout:
                with proc.stdout:
                    for line in iter(proc.stdout.readline, b""):
                        logger.info("%s", line.decode().rstrip())

            self.exit_code = proc.wait()
            if self.exit_code != 0:
                raise Exception(self.exit_code)

    def on_exit(self):
        for child_pid in _collect_child_process_pids(os.getpid()):
            os.kill(child_pid, signal.SIGTERM)


__all__ = ["PopenPythonScript"]
