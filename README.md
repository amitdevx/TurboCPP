# Turbo C++ for Linux & Windows

<div align="center">

![TurboC++](https://upload.wikimedia.org/wikipedia/commons/1/16/Turbo_CPP_Compiler.jpg)

**A modern port of Borland's classic Turbo C++ IDE running on DOSBox for Linux and Windows**

[![Tests](https://github.com/amitdevx/TurboC-.svg?branch=main&style=flat-square)](https://github.com/amitdevx/TurboC-/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Optimization](#optimization)

</div>

---

## About

Turbo C++ is a legendary C++ IDE from the 1990s by Borland. This project brings it to modern operating systems using DOSBox emulation, with optimizations for CPU efficiency and cross-platform support.

## Features

- ✅ **Cross-Platform**: Works on Linux and Windows
- ✅ **CPU Optimized**: Cycle capping prevents high CPU usage
- ✅ **Easy Setup**: Single command to launch
- ✅ **Path Handling**: Supports directory names with spaces
- ✅ **Automated Testing**: 5 comprehensive test suites
- ✅ **CI/CD Ready**: GitHub Actions workflow included

## System Requirements

### Linux
- DOSBox emulator installed
- Terminal/shell environment

**Install DOSBox:**
```bash
# Ubuntu/Debian
sudo apt-get install dosbox

# Fedora/RHEL
sudo dnf install dosbox

# Arch Linux
sudo pacman -S dosbox

# macOS
brew install dosbox
```

### Windows
- DOSBox installed ([Download](https://www.dosbox.com/download.php))
- Windows 7 or later

## Installation

```bash
git clone https://github.com/amitdevx/TurboC-.git
cd TurboC-
chmod +x start.sh
```

## Usage

### Linux
```bash
./start.sh
```

### Windows
Double-click `start.bat` or run from Command Prompt:
```cmd
start.bat
```

## Optimization

The project includes `dosbox-turbo.conf` for CPU efficiency:

- **Default Cycles**: 3000 (balanced performance)
- **High Performance**: Edit `dosbox-turbo.conf` → set `cycles=5000` or higher
- **Battery Saving**: Set `cycles=1000` for laptops

### Example Configuration

```ini
[cpu]
cycles=3000      # Adjust based on your needs
core=auto
cputype=auto
```

## Project Structure

```
TurboC-/
├── start.sh                    # Linux launcher
├── start.bat                   # Windows launcher
├── dosbox-turbo.conf          # Performance configuration
├── README.md                   # This file
├── CHANGELOG.md               # Changes and improvements
├── .gitignore                 # Git ignore rules
├── tests/                     # Test suite
│   ├── test_dosbox_config.sh
│   ├── test_start_script.sh
│   ├── test_start_bat.sh
│   ├── test_tc_structure.sh
│   └── test_gitignore.sh
├── .github/workflows/
│   └── tests.yml             # CI/CD pipeline
└── TC/                        # Turbo C++ IDE
    ├── BIN/                   # Executables
    ├── INCLUDE/               # Header files
    ├── LIB/                   # Libraries
    ├── EXAMPLES/              # Sample code
    └── CLASSLIB/              # Class library
```

## Testing

The project includes automated tests that run on every push via GitHub Actions.

**Manual Test Run:**
```bash
bash tests/test_dosbox_config.sh
bash tests/test_start_script.sh
bash tests/test_start_bat.sh
bash tests/test_tc_structure.sh
bash tests/test_gitignore.sh
```

## Improvements Over Original

| Feature | Original | This Version |
|---------|----------|-------------|
| CPU Usage | 100% (max) | ~30% (capped) |
| Windows Support | ❌ No | ✅ Yes |
| Path Spacing | ❌ Breaks | ✅ Supported |
| Tests | ❌ No | ✅ 5 Tests |
| CI/CD | ❌ No | ✅ GitHub Actions |

## Troubleshooting

### DOSBox not found (Linux)
```bash
# Check if installed
which dosbox

# Install if missing
sudo apt-get install dosbox
```

### Compilation too slow
Edit `dosbox-turbo.conf` and increase `cycles`:
```ini
cycles=5000
```

### High CPU usage
Lower the cycles value:
```ini
cycles=1500
```

## Credits

- **Original Project**: [AvinashReddy3108/TurboCPP4Linux](https://github.com/AvinashReddy3108/TurboCPP4Linux)
- **Windows Port Reference**: [vineetchoudhary](https://github.com/vineetchoudhary)
- **Original IDE**: Borland International (Turbo C++)

## Maintainer

**Amit Divekar**
- GitHub: [@amitdevx](https://github.com/amitdevx)
- Website: [amitdevx.tech](https://amitdevx.tech)
- Twitter: [@amitdevx_](https://twitter.com/amitdevx_)
- Location: Mumbai, India

Full-Stack Developer specializing in Next.js, TypeScript, DevOps, CI/CD, and Cloud technologies.

## License

MIT License - See LICENSE file for details

## Support

Found an issue? Create an issue on [GitHub Issues](https://github.com/amitdevx/TurboC-/issues)

---

<div align="center">

Made with ❤️ by [Amit Divekar](https://github.com/amitdevx)

</div>
