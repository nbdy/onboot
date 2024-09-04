import ctypes
from abc import abstractmethod
from dataclasses import dataclass
from os import geteuid
from pathlib import Path
from random import choices
from string import digits, ascii_letters
from sys import platform
from typing import Type, Optional


def random_str(length: int = 8) -> str:
    return ''.join(choices(digits + ascii_letters, k=length))


@dataclass
class InstallerConfiguration:
    directory: Path
    name: str

    def __init__(self, directory: Path, name: str):
        self.directory = directory
        self.name = name

    def get_path(self) -> Path:
        return self.directory.joinpath(self.name)


class Installer:
    autostart_directory: Path
    target_path: Path
    config: InstallerConfiguration

    def __init__(self, config: InstallerConfiguration):
        self.config = config

    @staticmethod
    def write_file(path: Path, data: str) -> bool:
        return path.write_text(data) == len(data)

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.joinpath(self.config.name)

    @abstractmethod
    def install(self) -> bool:
        ...

    def uninstall(self) -> bool:
        if self.is_supported() and self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False

    def is_supported(self) -> bool:
        return self.autostart_directory.is_dir()

    @staticmethod
    def is_root() -> bool:
        try:
            r = geteuid() == 0
        except AttributeError:
            r = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return r


def install_if_supported(installer: Installer) -> bool:
    if installer.is_supported():
        return installer.install()
    return False


def try_install(installers: list[Type[Installer]], config) -> [bool, Installer]:
    ret = False
    used: Optional[Installer] = None

    for installer in installers:
        i = installer(config)
        if not ret and i.is_supported():
            ret = i.install()
            if ret:
                used = i
                break

    return ret, used


def install_linux(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.linux import XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller
    return try_install([XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller], config)


def install_windows(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.windows import StartMenuInstaller
    return try_install([StartMenuInstaller], config)


def install_darwin(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.darwin import PListInstaller
    from onboot.linux import CrontabInstaller
    return try_install([PListInstaller, CrontabInstaller], config)


def install(config: InstallerConfiguration) -> [bool, Installer]:
    if platform == "linux":
        return install_linux(config)
    elif platform == "darwin":
        return install_darwin(config)
    elif platform == "windows":
        return install_windows(config)
    else:
        raise NotImplementedError(f"Platform {platform} is not implemented.")


_installers = ["install", "install_linux", "install_darwin", "install_windows", "InstallerConfiguration"]

if platform == "linux":
    from onboot.linux import XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller
    _installers += ["XDGInstaller", "CrontabInstaller", "ProfileInstaller", "InitInstaller"]
elif platform == "darwin":
    from onboot.darwin import PListInstaller
    from onboot.linux import CrontabInstaller
    _installers += ["PListInstaller", "CrontabInstaller"]
elif platform == "windows":
    from onboot.windows import StartMenuInstaller, HKCUInstaller, HKLMInstaller
    _installers += ["StartMenuInstaller", "HKCUInstaller", "HKLMInstaller"]


__all__ = ["Installer", "random_str"] + _installers
