from onboot.Darwin import PListInstaller, InstallerConfiguration
from os.path import isfile

plist_config = InstallerConfiguration("/tmp/", "myfile")


def test_plist_install():
    installer = PListInstaller(plist_config)
    installer.install()
    assert isfile(installer.get_autostart_path())


def test_plist_uninstall():
    installer = PListInstaller(plist_config)
    installer.uninstall()
    assert not isfile(installer.get_autostart_path())
