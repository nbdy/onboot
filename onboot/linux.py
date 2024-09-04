from pathlib import Path
from subprocess import check_output

from onboot import Installer, random_str


class XDGInstaller(Installer):
    autostart_directory = Path("~/.config/autostart/")
    root_autostart_directory = Path("/etc/xdg/autostart/")

    def get_autostart_path(self) -> Path:
        name = f"{self.config.name}.desktop"
        if self.is_root():
            return self.root_autostart_directory.joinpath(name)
        return self.autostart_directory.joinpath(name)

    def install(self) -> bool:
        conf = "[Desktop Entry]\n" \
               "Type=Application\n" \
               "Name={}\n" \
               "Exec={}\n" \
               "Terminal=false\n".format(self.config.name, self.config.name)

        try:
            return self.get_autostart_path().write_text(conf) == len(conf)
        except:  # TODO
            return False

    def uninstall(self) -> bool:
        if self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False

    def is_supported(self) -> bool:
        if self.is_root():
            return self.root_autostart_directory.is_dir()
        return self.autostart_directory.is_dir()


class CrontabInstaller(Installer):
    def install(self) -> bool:
        try:
            fp = Path("/tmp").joinpath(random_str())
            fp.write_text(f"@reboot {self.config.get_path()}\n")
            check_output(f"crontab {fp}", shell=True)
            fp.unlink()
        except:  # TODO
            return False

    def uninstall(self) -> bool:
        ct = check_output("crontab -l", shell=True)
        ct = ct.replace(f"@reboot {self.config.get_path()}".encode("utf-8"), b"")
        try:
            fp = Path("/tmp").joinpath(random_str())
            fp.write_text(ct.decode("utf-8"))
            check_output(f"crontab {fp}")
        except:  # TODO
            return False

    def is_supported(self) -> bool:
        return True


class ProfileInstaller(Installer):
    autostart_directory = Path("/etc/profile.d/")

    def install(self) -> bool:
        try:
            text = f"#!/bin/sh\n{self.config.get_path()}"
            return self.get_autostart_path().write_text(text) == len(text)
        except:  # TODO
            return False

    def uninstall(self) -> bool:
        if self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False


class KDEPlasmaInstaller(Installer):
    autostart_directory = Path("~/.config/autostart-scripts/")

    def get_autostart_path(self):
        return self.autostart_directory.joinpath(f"{self.config.name}.sh")

    def install(self) -> bool:
        try:
            text = f"#!/bin/sh\n{self.config.get_path()}"
            return self.get_autostart_path().write_text(text) == len(text)
        except:  # TODO
            return False


class InitInstaller(Installer):
    autostart_directory = Path("/etc/init.d/")

    def install(self) -> bool:
        try:
            text = f"#!/bin/sh\n{self.config.get_path()}"
            return self.get_autostart_path().write_text(text) == len(text)
        except:  # TODO
            return False
