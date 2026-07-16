import sysconfig
from pathlib import Path


def install():

    site_packages = Path(sysconfig.get_paths()["purelib"])

    destination = site_packages / "network_guard_bootstrap.pth"

    destination.write_text("import network_guard.bootstrap\n", encoding="utf-8")

    print(f"Installed {destination}")


if __name__ == "__main__":
    install()
