# ⚡ Buildfy Converter

> 🎯 A modern GUI-based tool (built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)) to convert your Python `.py` files into **standalone executables** (`.exe` on Windows, `.app` on macOS, binaries on Linux) using **PyInstaller**.

---

## ✨ Features

✅ Convert `.py` → `.exe` (Windows) or `.app` (macOS)
✅ Sleek dark-mode **CustomTkinter UI**
✅ One-click packaging with **PyInstaller**
✅ Choose **App Name**, **Icon**, and **Output Directory**
✅ Options:

* 📦 One-file executable
* 🖼 Windowed mode (no console)
* 🧹 Clean build
  ✅ Live **build logs** in-app
  ✅ Auto-installs missing dependencies
  ✅ Cross-platform (Windows, macOS, Linux)

---

## 📸 Preview

*(Insert screenshot of your app here)*

```
🖼 Screenshot coming soon…  
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repo

```bash
git clone https://github.com/your-username/buildfy-converter.git
cd buildfy-converter
```

### 2️⃣ Install dependencies

Make sure you have **Python 3.10+** installed.

```bash
pip install -r requirements.txt
```

> Dependencies:

* `customtkinter`
* `pyinstaller`

### 3️⃣ Run Buildfy Converter

```bash
python buildfy.py
```

---

## 🛠 Usage

1. Open Buildfy Converter.
2. Select your `.py` file.
3. (Optional) Enter app name, icon, and output directory.
4. Select build options (One File, Windowed, Clean).
5. Click **Build** → wait while PyInstaller does its magic ✨.
6. Find your executable inside the `dist/` folder.

---

## 📂 Project Structure

```
📦 buildfy-converter
 ┣ 📜 buildfy.py        # Main GUI app
 ┣ 📜 requirements.txt  # Dependencies
 ┣ 📜 README.md         # This file
 ┗ 📂 dist/             # Build outputs (auto-generated)
```

---

## 🖥 Supported Platforms

* 🪟 Windows → `.exe`
* 🍎 macOS → `.app`
* 🐧 Linux → ELF binary

---

## 💡 Roadmap

* [ ] Save logs to file
* [ ] Progress bar during builds
* [ ] Preset profiles (CLI app / GUI app)
* [ ] UPX compression option
* [ ] Pack Buildfy itself into `.exe` & `.app`

---

## 🤝 Contributing

Pull requests are welcome!
If you’d like to add new features or fix bugs, feel free to fork this repo and submit a PR 🚀.

---

## 📜 License

GNU License © 2025 \Proxlight

---

## 🌟 Support

If you like this project, give it a ⭐ on GitHub — it helps a lot!
And share it with other Python developers ❤️

