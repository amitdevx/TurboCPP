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

Download and Instructions
=========================
- Download latest version of TurboCPP from [here](https://github.com/AvinashReddy3108/TurboCPP4Linux/archive/refs/heads/master.zip)
- Extract the zip file anywhere you like

### Linux
- Open a terminal in that folder and run:
  ```bash
  chmod +x start.sh
  ./start.sh
  ```

### Windows
- Double-click `start.bat` (DOSBox must be installed first).

Performance Note
================
A project-local `dosbox-turbo.conf` is included to keep CPU usage reasonable.
If Turbo C++ feels slow during compilation, edit `dosbox-turbo.conf` and raise the `cycles` value (e.g. `cycles=5000`).

Credits
=======
- Huge thanks to [@vineetchoudhary](https://github.com/vineetchoudhary) for the TurboCPP files.

Issues ?
========
Report them [here](https://github.com/AvinashReddy3108/TurboCPP4Linux/issues)
