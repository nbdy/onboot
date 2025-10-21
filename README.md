# 🚀 onboot

[![PyPI version](https://badge.fury.io/py/onboot.svg)](https://badge.fury.io/py/onboot)
[![Python Support](https://img.shields.io/pypi/pyversions/onboot.svg)](https://pypi.org/project/onboot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> Cross-platform autostart installer library for Python

**onboot** provides a unified interface to install and manage autostart entries across different operating systems and initialization methods. Whether you need to configure startup scripts on Linux, launch agents on macOS, or registry entries on Windows, onboot has you covered.

---

## ✨ Features

### 🐧 Linux
- ✅ **XDG** - XDG Autostart standard
- ✅ **Cron** - Cron jobs (@reboot)
- ✅ **Profile.d** - Shell profile scripts
- ✅ **KDE Plasma** - KDE autostart
- ✅ **Init.d** - System V init scripts

### 🍎 macOS (Darwin)
- ✅ **PList** - Launch Agents/Daemons
- ✅ **Cron** - Cron jobs (@reboot)

### 🪟 Windows
- ✅ **StartMenu** - Startup folder
- ✅ **Registry** - Windows Registry
  - ✅ HKCU (Current User)
  - ✅ HKLM (Local Machine)
  - ⏳ IFEO (Image File Execution Options)
  - ⏳ UserInit (Winlogon)
- ✅ **Task Scheduler** - Windows Task Scheduler
- ⏳ **WMIC** - Windows Management Instrumentation

---

## 📦 Installation

Install onboot using pip:

```bash
pip install onboot
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add onboot
```

---

## 🔧 Usage

### Quick Start - Auto-detect Best Installer

Let onboot automatically try all available installers for your operating system:

```python
from onboot import install_linux, InstallerConfiguration

# Create configuration
config = InstallerConfiguration("/home/user/myapp", "myapp")

# Install - tries all available installers until one succeeds
install_successful, used_installer = install_linux(config)

# Uninstall using the same installer
if install_successful:
    used_installer.uninstall()
```

### Platform-Specific Functions

```python
from onboot import install_windows, install_darwin, InstallerConfiguration

# Windows
success, installer = install_windows(InstallerConfiguration("C:\\myapp", "myapp"))

# macOS
success, installer = install_darwin(InstallerConfiguration("/Users/user/myapp", "myapp"))
```

### Use a Specific Installer

For more control, use a specific installer directly:

```python
from onboot.windows import HKCUInstaller
from onboot import InstallerConfiguration

# Create configuration
config = InstallerConfiguration("C:\\myapp", "myapp")

# Use Windows Registry (HKCU) installer
installer = HKCUInstaller(config)
installer.install()

# Later, uninstall
installer.uninstall()
```

### Available Installers by Platform

**Linux:**
```python
from onboot.linux import (
    XDGInstaller,              # XDG autostart (.desktop files)
    CrontabInstaller,          # Crontab @reboot
    ProfileInstaller,          # /etc/profile.d/
    KDEPlasmaInstaller,        # KDE Plasma autostart scripts
    InitInstaller,             # /etc/init.d/
    SystemdUserInstaller,      # ~/.config/systemd/user/ services
    SystemdSystemInstaller,    # /etc/systemd/system/ services
    BashrcInstaller,           # ~/.bashrc
    RcLocalInstaller           # /etc/rc.local
)
```

**macOS:**
```python
from onboot.darwin import (
    PListInstaller,            # ~/Library/LaunchAgents/
    LaunchDaemonInstaller,     # /Library/LaunchDaemons/ (system-wide)
    ProfileInstaller           # /etc/profile
)
```

**Windows:**
```python
from onboot.windows import (
    HKCUInstaller,             # HKEY_CURRENT_USER registry
    HKLMInstaller,             # HKEY_LOCAL_MACHINE registry
    StartMenuInstaller,        # Start Menu startup folder
    SchTaskInstaller,          # Task Scheduler
    UserInitInstaller          # Winlogon UserInit
)
```

---

## 📝 Configuration

The `InstallerConfiguration` class accepts the following parameters:

- **`directory`** (Path): Directory containing the executable or script
- **`name`** (str): Name of the application/service (filename)

Example:
```python
from pathlib import Path
from onboot import InstallerConfiguration

config = InstallerConfiguration(
    directory=Path("/usr/local/bin"),
    name="myapp"
)

# The full path will be: /usr/local/bin/myapp
print(config.get_path())
```

---

## 🛠️ Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run tests
uv run pytest
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
