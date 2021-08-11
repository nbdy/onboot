import ctypes
from dataclasses import dataclass
from os import geteuid, remove
from os.path import join, isdir, isfile
from random import choices
from string import digits, ascii_letters
from sys import platform


def random_str(length: int = 8) -> str:
    return ''.join(choices(digits + ascii_letters, k=length))


@dataclass
class InstallerConfiguration:
    directory: str
    name: str

    def __init__(self, directory: str, name: str):
        self.directory = directory
        self.name = name

    def get_path(self):
        return join(self.directory, self.name)


class Installer(object):
    autostart_directory: str = None
    target_path: str = None
    config: InstallerConfiguration = None

    def __init__(self, config: InstallerConfiguration):
        self.config = config

    @staticmethod
    def write_file(path: str, data: str) -> bool:
        try:
            with open(path, "w") as o:
                o.write(data)
            return True
        except Exception as e:
            print(e)
            return False

    def get_autostart_path(self):
        return f"{self.autostart_directory}{self.config.name}"

    def install(self) -> bool:
        return False

    def uninstall(self) -> bool:
        if self.is_supported() and isfile(self.get_autostart_path()):
            remove(self.get_autostart_path())
            return True
        return False

    def is_supported(self) -> bool:
        return self.autostart_directory is not None and isdir(self.autostart_directory)

    @staticmethod
    def is_root() -> bool:
        try:
            r = geteuid() == 0
        except AttributeError:
            r = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return r


def install_if_supported(installer) -> bool:
    if installer.is_supported():
        return installer.install()
    return False


def try_install(installers, config) -> [bool, Installer]:
    r = False
    i: Installer
    for installer in installers:
        i = installer(config)
        if not r and i.is_supported():
            if i.install():
                return True, i
    return False, None


def install_linux(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.Linux import XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller
    return try_install([XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller], config)


def install_windows(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.Windows import StartMenuInstaller
    return try_install([StartMenuInstaller], config)


def install_darwin(config: InstallerConfiguration) -> [bool, Installer]:
    from onboot.Darwin import PListInstaller
    from onboot.Linux import CrontabInstaller
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
    from onboot.Linux import XDGInstaller, CrontabInstaller, ProfileInstaller, InitInstaller
    _installers += ["XDGInstaller", "CrontabInstaller", "ProfileInstaller", "InitInstaller"]
elif platform == "darwin":
    from onboot.Darwin import PListInstaller
    _installers += ["PListInstaller"]
elif platform == "windows":
    from onboot.Windows import StartMenuInstaller, HKCUInstaller, HKLMInstaller
    _installers += ["StartMenuInstaller", "HKCUInstaller", "HKLMInstaller"]


__all__ = _installers
