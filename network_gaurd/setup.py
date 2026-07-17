from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        super().run()
        self._copy_bootstrap_pth()

    def _copy_bootstrap_pth(self):
        destination = Path(self.build_lib) / "network_guard_bootstrap.pth"
        destination.write_text("import network_guard.bootstrap\n", encoding="utf-8")


setup(cmdclass={"build_py": build_py})
