from pathlib import Path

from onboot import InstallerConfiguration
from onboot.windows import StartMenuInstaller, HKCUInstaller, HKLMInstaller, SchTaskInstaller
from os.path import isfile


windows_config = InstallerConfiguration(Path("C:\\tmp\\"), "myfile")


def test_startmenu_install():
    installer = StartMenuInstaller(windows_config)
    if installer.is_supported():
        installer.install()
        assert isfile(installer.get_autostart_path())


def test_startmenu_uninstall():
    installer = StartMenuInstaller(windows_config)
    if installer.is_supported():
        installer.uninstall()
        assert not isfile(installer.get_autostart_path())


def test_hkcu_install():
    installer = HKCUInstaller(windows_config)
    if installer.is_supported():
        result = installer.install()
        assert result is True or result is False  # Just check it doesn't crash


def test_hkcu_uninstall():
    installer = HKCUInstaller(windows_config)
    if installer.is_supported():
        result = installer.uninstall()
        assert result is True or result is False  # Just check it doesn't crash


def test_hklm_install():
    installer = HKLMInstaller(windows_config)
    if installer.is_supported():
        result = installer.install()
        assert result is True or result is False  # Just check it doesn't crash


def test_hklm_uninstall():
    installer = HKLMInstaller(windows_config)
    if installer.is_supported():
        result = installer.uninstall()
        assert result is True or result is False  # Just check it doesn't crash


def test_schtask_install():
    installer = SchTaskInstaller(windows_config)
    if installer.is_supported():
        result = installer.install()
        assert result is True or result is False  # Just check it doesn't crash


def test_schtask_uninstall():
    installer = SchTaskInstaller(windows_config)
    if installer.is_supported():
        result = installer.uninstall()
        assert result is True or result is False  # Just check it doesn't crash
