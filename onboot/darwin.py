from pathlib import Path
from subprocess import check_output

from onboot import Installer


class PListInstaller(Installer):
    autostart_directory = Path("~/Library/LaunchAgents/")

    def generate_plist(self):
        return f'''
<key>{self.config.name}</key>
<array>
    <string>{self.config.get_path()}</string>
</array>
        '''

    def get_autostart_path(self) -> Path:
        return Path(f"~/Library/LaunchAgents/io.{self.config.name}.service.plist")

    def install(self) -> bool:
        try:
            self.get_autostart_path().write_text(self.generate_plist())
            check_output(f"launchctl load -w {self.get_autostart_path()}")
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError) as e:
            return False

    def uninstall(self) -> bool:
        try:
            if self.get_autostart_path().is_file():
                check_output(f"launchctl unload {self.get_autostart_path()}", shell=True)
                self.get_autostart_path().unlink()
                return True
            return False
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False


class LaunchDaemonInstaller(Installer):
    autostart_directory = Path("/Library/LaunchDaemons/")

    def generate_plist(self):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>io.{self.config.name}.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.config.get_path()}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.joinpath(f"io.{self.config.name}.daemon.plist")

    def install(self) -> bool:
        try:
            self.get_autostart_path().write_text(self.generate_plist())
            check_output(f"launchctl load -w {self.get_autostart_path()}", shell=True)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            if self.get_autostart_path().is_file():
                check_output(f"launchctl unload {self.get_autostart_path()}", shell=True)
                self.get_autostart_path().unlink()
                return True
            return False
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.is_root() and self.autostart_directory.is_dir()


class ProfileInstaller(Installer):
    autostart_directory = Path("/etc/")

    def get_autostart_path(self) -> Path:
        return self.autostart_directory.joinpath("profile")

    def install(self) -> bool:
        try:
            profile_path = self.get_autostart_path()
            command = f"\n# {self.config.name} autostart\n{self.config.get_path()} &\n"
            
            # Append to /etc/profile
            with open(profile_path, 'a') as f:
                f.write(command)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            profile_path = self.get_autostart_path()
            if not profile_path.is_file():
                return False
            
            # Read current content
            content = profile_path.read_text()
            
            # Remove our entry
            command = f"\n# {self.config.name} autostart\n{self.config.get_path()} &\n"
            new_content = content.replace(command, "")
            
            # Write back
            profile_path.write_text(new_content)
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.is_root() and self.get_autostart_path().exists()


# TODO: Implement LoginItemsInstaller for System Preferences > Users & Groups > Login Items
# TODO: Implement LoginHookInstaller for /var/root/Library/Preferences/com.apple.loginwindow
# TODO: Implement LogoutHookInstaller for logout scripts
# TODO: Implement StartupItemsInstaller for /Library/StartupItems/ (deprecated but still functional)
# TODO: Implement PeriodicScriptInstaller for /etc/periodic/ scripts
# TODO: Implement DyldInsertLibrariesInstaller for DYLD_INSERT_LIBRARIES environment variable
