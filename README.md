Py App Builder

A modern CustomTkinter GUI that wraps PyInstaller to package a .py script into a platform-native executable.

- On Windows: .exe
- On macOS: .app

Setup
- Create a virtual environment
- Activate it
- Install requirements with: pip install -r requirements.txt
- Run the app: python main.py

Usage
- Select your .py file
- Optionally set app name and icon (.ico on Windows, .icns on macOS)
- Choose output directory (defaults to ./dist)
- Pick options: One-file, Windowed, Clean build
- Click Build and watch the log

Notes
- macOS: Windowed produces a .app bundle; One-file is compatible
- Windows: One-file creates a single .exe; without it, artifacts go under dist/<name>
- For data files and advanced config, consider a PyInstaller spec file
