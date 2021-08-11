from os import remove
from os.path import isfile, isdir
from subprocess import check_output

from onboot import Installer, random_str


class XDGInstaller(Installer):
    autostart_directory = "~/.config/autostart/"
    root_autostart_directory = "/etc/xdg/autostart/"

    def get_autostart_path(self):
        if self.is_root():
            return f"{self.root_autostart_directory}{self.config.name}.desktop"
        return f"{self.autostart_directory}{self.config.name}.desktop"

    def install(self) -> bool:
        conf = "[Desktop Entry]\n" \
               "Type=Application\n" \
               "Name={}\n" \
               "Exec={}\n" \
               "Terminal=false\n".format(self.config.name, self.config.name)

        try:
            with open(self.get_autostart_path(), "w") as o:
                o.write(conf)
        except Exception as e:
            print(e)
            return False
        return True

    def uninstall(self) -> bool:
        p = self.get_autostart_path()
        if isfile(p):
            remove(p)
            return True
        return False

    def is_supported(self) -> bool:
        if self.is_root():
            return isdir(self.root_autostart_directory)
        return isdir(self.autostart_directory)


class CrontabInstaller(Installer):
    def install(self) -> bool:
        try:
            fp = f"/tmp/{random_str()}"
            with open(fp, "w") as o:
                o.write(f"@reboot {self.config.get_path()}\n")
            check_output(f"crontab {fp}", shell=True)
            remove(fp)
        except Exception as e:
            print(e)
            return False

    def uninstall(self) -> bool:
        ct = check_output("crontab -l", shell=True)
        ct = ct.replace(f"@reboot {self.config.get_path()}".encode("utf-8"), b"")
        try:
            p = f"/tmp/{random_str()}"
            with open(p, "w") as o:
                o.write(ct.decode("utf-8"))
            check_output(f"crontab {p}")
        except Exception as e:
            print(e)
            return False

    def is_supported(self) -> bool:
        return True


class ProfileInstaller(Installer):
    autostart_directory = "/etc/profile.d/"

    def install(self) -> bool:
        try:
            with open(f"{self.autostart_directory}{self.config.name}") as o:
                o.write(f"#!/bin/sh\n{self.config.get_path()}")
        except Exception as e:
            print(e)
            return False

    def uninstall(self) -> bool:
        p = f"{self.autostart_directory}{self.config.name}"
        if isfile(p):
            remove(p)
            return True
        return False


class KDEPlasmaInstaller(Installer):
    autostart_directory = "~/.config/autostart-scripts/"

    def get_autostart_path(self):
        return f"{self.autostart_directory}{self.config.name}.sh"

    def install(self) -> bool:
        try:
            with open(self.get_autostart_path(), "w") as o:
                o.write(f"#!/bin/sh\n{self.config.get_path()}")
            return True
        except Exception as e:
            print(e)
            return False


class InitInstaller(Installer):
    autostart_directory = "/etc/init.d/"

    def install(self) -> bool:
        try:
            with open(f"{self.autostart_directory}{self.config.name}") as o:
                o.write(f"#!/bin/sh\n{self.config.get_path()}")
        except Exception as e:
            print(e)
            return False
