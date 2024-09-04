from pathlib import Path

from onboot import InstallerConfiguration
from onboot.darwin import PListInstaller
from os.path import isfile

plist_config = InstallerConfiguration(Path("/tmp/"), "myfile")


def test_plist_install():
    installer = PListInstaller(plist_config)
    installer.install()
    assert isfile(installer.get_autostart_path())


def test_plist_uninstall():
    installer = PListInstaller(plist_config)
    installer.uninstall()
    assert not isfile(installer.get_autostart_path())
