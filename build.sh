#!/bin/bash
pyinstaller --onefile --windowed app/main.py -n SmartAccountant
echo "Build complete. Executable in dist/"