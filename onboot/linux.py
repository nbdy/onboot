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
        except (OSError, IOError, PermissionError, FileNotFoundError):
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
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        ct = check_output("crontab -l", shell=True)
        ct = ct.replace(f"@reboot {self.config.get_path()}".encode("utf-8"), b"")
        try:
            fp = Path("/tmp").joinpath(random_str())
            fp.write_text(ct.decode("utf-8"))
            check_output(f"crontab {fp}")
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return True


class ProfileInstaller(Installer):
    autostart_directory = Path("/etc/profile.d/")

    def install(self) -> bool:
        try:
            text = f"#!/bin/sh\n{self.config.get_path()}"
            return self.get_autostart_path().write_text(text) == len(text)
        except (OSError, IOError, PermissionError, FileNotFoundError):
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
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        if self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False


class InitInstaller(Installer):
    autostart_directory = Path("/etc/init.d/")

    def install(self) -> bool:
        try:
            text = f"#!/bin/sh\n{self.config.get_path()}"
            return self.get_autostart_path().write_text(text) == len(text)
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        if self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False


class SystemdUserInstaller(Installer):
    autostart_directory = Path("~/.config/systemd/user/")

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.expanduser().joinpath(f"{self.config.name}.service")

    def generate_service(self) -> str:
        return f"""[Unit]
Description={self.config.name} service
After=default.target

[Service]
Type=simple
ExecStart={self.config.get_path()}
Restart=on-failure

[Install]
WantedBy=default.target
"""

    def install(self) -> bool:
        try:
            # Ensure directory exists
            self.autostart_directory.expanduser().mkdir(parents=True, exist_ok=True)
            # Write service file
            service_path = self.get_autostart_path()
            text = self.generate_service()
            if service_path.write_text(text) != len(text):
                return False
            # Enable the service
            check_output(f"systemctl --user enable {self.config.name}.service", shell=True)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            # Disable the service
            check_output(f"systemctl --user disable {self.config.name}.service", shell=True)
            # Remove service file
            if self.get_autostart_path().is_file():
                self.get_autostart_path().unlink()
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        try:
            # Check if systemd is available
            check_output("systemctl --user --version", shell=True)
            return True
        except:
            return False


class SystemdSystemInstaller(SystemdUserInstaller):
    autostart_directory = Path("/etc/systemd/system/")

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.joinpath(f"{self.config.name}.service")

    def install(self) -> bool:
        try:
            # Ensure directory exists
            self.autostart_directory.mkdir(parents=True, exist_ok=True)
            # Write service file
            service_path = self.get_autostart_path()
            text = self.generate_service()
            if service_path.write_text(text) != len(text):
                return False
            # Enable the service
            check_output(f"systemctl enable {self.config.name}.service", shell=True)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            # Disable the service
            check_output(f"systemctl disable {self.config.name}.service", shell=True)
            # Remove service file
            if self.get_autostart_path().is_file():
                self.get_autostart_path().unlink()
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        try:
            # Check if systemd is available and we have root access
            check_output("systemctl --version", shell=True)
            return self.is_root()
        except:
            return False


class BashrcInstaller(Installer):
    autostart_directory = Path("~/")

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.expanduser().joinpath(".bashrc")

    def install(self) -> bool:
        try:
            bashrc_path = self.get_autostart_path()
            command = f"\n# {self.config.name} autostart\n{self.config.get_path()} &\n"
            
            # Append to .bashrc
            with open(bashrc_path, 'a') as f:
                f.write(command)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            bashrc_path = self.get_autostart_path()
            if not bashrc_path.is_file():
                return False
            
            # Read current content
            content = bashrc_path.read_text()
            
            # Remove our entry
            command = f"\n# {self.config.name} autostart\n{self.config.get_path()} &\n"
            new_content = content.replace(command, "")
            
            # Write back
            bashrc_path.write_text(new_content)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.get_autostart_path().exists()


class RcLocalInstaller(Installer):
    autostart_directory = Path("/etc/")

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.joinpath("rc.local")

    def install(self) -> bool:
        try:
            rc_local_path = self.get_autostart_path()
            
            # Check if rc.local exists, create if not
            if not rc_local_path.exists():
                rc_local_path.write_text("#!/bin/sh -e\n\nexit 0\n")
                rc_local_path.chmod(0o755)
            
            # Read current content
            content = rc_local_path.read_text()
            
            # Insert our command before 'exit 0'
            command = f"{self.config.get_path()} &\n"
            
            # If our command is already there, don't add it again
            if command in content:
                return True
            
            # Insert before exit 0 or at the end
            if "exit 0" in content:
                new_content = content.replace("exit 0", f"{command}exit 0")
            else:
                new_content = content + f"\n{command}"
            
            rc_local_path.write_text(new_content)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            rc_local_path = self.get_autostart_path()
            if not rc_local_path.is_file():
                return False
            
            # Read current content
            content = rc_local_path.read_text()
            
            # Remove our entry
            command = f"{self.config.get_path()} &\n"
            new_content = content.replace(command, "")
            
            # Write back
            rc_local_path.write_text(new_content)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.is_root()


# TODO: Implement OpenRCInstaller for /etc/init.d/ with OpenRC-specific management
# TODO: Implement GnomeAutostart for GNOME-specific autostart
# TODO: Implement UpstartInstaller for systems using Upstart init
