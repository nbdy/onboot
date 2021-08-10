# pyautorun
cross-platform autostart installer(s)
## install
```shell
pip3 install onboot
```
## usage
### try all available installers for a certain os
```python
from onboot import install_linux, InstallerConfiguration

# install
install_successful, used_installer = install_linux(InstallerConfiguration("/home/user/", "myapp"))

# uninstall
if install_successful:
    used_installer.uninstall()
```
### only use a specific installer

```python
from onboot.Windows import HKCUInstaller
from onboot import InstallerConfiguration

# install
installer = HKCUInstaller(InstallerConfiguration("C:\\", "myapp"))
installer.install()

# uninstall
installer.uninstall()
```
