from subprocess import check_output

from onboot import Installer


class PListInstaller(Installer):
    autostart_directory = "~/Library/LaunchAgents/"

    def generate_plist(self):
        return f'''
<key>{self.config.name}</key>
<array>
    <string>{self.config.get_path()}</string>
</array>
        '''

    def get_autostart_path(self):
        return f"~/Library/LaunchAgents/io.{self.config.name}.service.plist"

    def install(self) -> bool:
        try:
            with open(self.get_autostart_path(), "w") as o:
                o.write(self.generate_plist())
            check_output(f"launchctl load -w {self.get_autostart_path()}")
            return True
        except Exception as e:
            print(e)
            return False

    def uninstall(self) -> bool:
        return False
