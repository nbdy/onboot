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
        except:  # TODO
            return False

    def uninstall(self) -> bool:
        return False  # TODO
