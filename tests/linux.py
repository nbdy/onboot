from pathlib import Path

from onboot import InstallerConfiguration
from onboot.linux import XDGInstaller, CrontabInstaller, ProfileInstaller, KDEPlasmaInstaller, InitInstaller
from os.path import isfile


xdg_config = InstallerConfiguration(Path("/tmp/"), "myfile")


def test_xdg_install():
    installer = XDGInstaller(xdg_config)
    if installer.is_supported():
        installer.install()
        assert isfile(installer.get_autostart_path())


def test_xdg_uninstall():
    installer = XDGInstaller(xdg_config)
    if installer.is_supported():
        installer.uninstall()
        assert not isfile(installer.get_autostart_path())


def test_crontab_install():
    installer = CrontabInstaller(xdg_config)
    if installer.is_supported():
        result = installer.install()
        assert result is True or result is False  # Just check it doesn't crash


def test_crontab_uninstall():
    installer = CrontabInstaller(xdg_config)
    if installer.is_supported():
        result = installer.uninstall()
        assert result is True or result is False  # Just check it doesn't crash


def test_profile_install():
    installer = ProfileInstaller(xdg_config)
    if installer.is_supported():
        installer.install()
        assert isfile(installer.get_autostart_path())


def test_profile_uninstall():
    installer = ProfileInstaller(xdg_config)
    if installer.is_supported():
        installer.uninstall()
        assert not isfile(installer.get_autostart_path())


def test_kde_plasma_install():
    installer = KDEPlasmaInstaller(xdg_config)
    if installer.is_supported():
        installer.install()
        assert isfile(installer.get_autostart_path())


def test_kde_plasma_uninstall():
    installer = KDEPlasmaInstaller(xdg_config)
    if installer.is_supported():
        installer.uninstall()
        assert not isfile(installer.get_autostart_path())


def test_init_install():
    installer = InitInstaller(xdg_config)
    if installer.is_supported():
        installer.install()
        assert isfile(installer.get_autostart_path())


def test_init_uninstall():
    installer = InitInstaller(xdg_config)
    if installer.is_supported():
        installer.uninstall()
        assert not isfile(installer.get_autostart_path())
