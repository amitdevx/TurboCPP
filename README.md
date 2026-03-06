What is Turbo C++?
===================
![A screenshot of the TurboC++ IDE](https://upload.wikimedia.org/wikipedia/commons/1/16/Turbo_CPP_Compiler.jpg)

- It is a C++ compiler and integrated development environment (IDE) and computer language.
- Turbo C++ provides an environment called IDE (Integrated Development Environment).
- The editor is used to create the source file, compile it, link it and then execute it.

System Requirements
====================
- **Linux or Windows** with a display, keyboard and mouse.
- Latest version of [DOSBox Emulator](https://www.dosbox.com/download.php?main=1) installed:
  - **Ubuntu/Mint**: `sudo apt install dosbox`
  - **Fedora**: `sudo dnf install dosbox`
  - **Arch**: `sudo pacman -S dosbox`
  - **Windows**: Download installer from https://www.dosbox.com/download.php

Installation & Quick Start
===========================
- Download latest version of TurboCPP from [Releases](../../releases)
- Extract the zip file anywhere you like

### Linux
```bash
chmod +x start.sh
./start.sh
```

### Windows
Double-click `start.bat` (DOSBox must be installed first).

Performance Optimization
========================
This project includes CPU cycle optimization via `dosbox-turbo.conf`:
- **Default cycles**: 3000 (responsive without high CPU usage)
- **To increase speed**: Edit `dosbox-turbo.conf` and set `cycles=5000` or higher
- **For laptops**: Set `cycles=1000` for better battery life

Testing
=======
Run the test suite:
```bash
bash tests/test_dosbox_config.sh
bash tests/test_start_script.sh
bash tests/test_start_bat.sh
bash tests/test_tc_structure.sh
bash tests/test_gitignore.sh
```

Or use GitHub Actions (automated on every push):
- See [`.github/workflows/tests.yml`](.github/workflows/tests.yml)

About This Fork
===============
**Maintained by**: [Amit Divekar](https://github.com/amitdevx)  
**Profile**: https://github.com/amitdevx  
**Location**: Mumbai, India  
**Bio**: Full-Stack Developer building with Next.js, TypeScript, DevOps, CI/CD, and Cloud.

**Improvements in this version**:
- ✅ CPU optimization (DOSBox cycles capping at 3000)
- ✅ Cross-platform support (Windows batch launcher)
- ✅ Fixed mount path quoting (handles spaces in directory names)
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline with GitHub Actions

Credits
=======
- Original project: [AvinashReddy3108/TurboCPP4Linux](https://github.com/AvinashReddy3108/TurboCPP4Linux)
- Windows port inspiration: [vineetchoudhary](https://github.com/vineetchoudhary)
- Original TC++ IDE: Borland International

Issues ?
========
Report issues at: [GitHub Issues](../../issues)
