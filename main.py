import os
import sys
import threading
import subprocess
import shlex
import platform
import tkinter.filedialog as fd
import tkinter.messagebox as mb

# Ensure customtkinter is available before import
try:
	import customtkinter as ctk
except Exception:
	try:
		subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
		subprocess.run([sys.executable, "-m", "pip", "install", "customtkinter"], check=True)
		import customtkinter as ctk
	except Exception as exc:
		print(f"Failed to install customtkinter: {exc}")
		raise


APP_TITLE = "Buildfy Converter"


def _ensure_pyinstaller_installed() -> None:
	try:
		import PyInstaller  # noqa: F401
	except Exception:
		subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)


class BuilderApp(ctk.CTk):

	def __init__(self) -> None:
		super().__init__()

		ctk.set_appearance_mode("dark")
		ctk.set_default_color_theme("dark-blue")

		self.title(APP_TITLE)
		self.geometry("860x560")
		self.minsize(760, 520)

		self._build_state_lock = threading.Lock()
		self._build_thread: threading.Thread | None = None
		self._currently_building = False

		self._create_widgets()

	def _create_widgets(self) -> None:
		# Root grid
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)

		header = ctk.CTkLabel(self, text=APP_TITLE, font=("SF Pro Display", 24, "bold"))
		header.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))

		container = ctk.CTkFrame(self, corner_radius=12)
		container.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)
		container.grid_columnconfigure(1, weight=1)

		# Input Python file
		lbl_input = ctk.CTkLabel(container, text="Python file (.py)")
		lbl_input.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

		self.entry_input = ctk.CTkEntry(container, placeholder_text="Select a .py file to package")
		self.entry_input.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(12, 6))
		btn_browse_input = ctk.CTkButton(container, text="Browse", command=self._browse_input, corner_radius=10, fg_color="#4F46E5", hover_color="#4338CA", text_color="white")
		btn_browse_input.grid(row=0, column=2, padx=12, pady=(12, 6))

		# App name
		lbl_name = ctk.CTkLabel(container, text="App name")
		lbl_name.grid(row=1, column=0, sticky="w", padx=12, pady=6)
		self.entry_name = ctk.CTkEntry(container, placeholder_text="Defaults to Python file name")
		self.entry_name.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=6)

		# Icon file
		icon_label = "Icon (.ico on Windows, .icns on macOS)"
		lbl_icon = ctk.CTkLabel(container, text=icon_label)
		lbl_icon.grid(row=2, column=0, sticky="w", padx=12, pady=6)
		self.entry_icon = ctk.CTkEntry(container, placeholder_text="Optional")
		self.entry_icon.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=6)
		btn_browse_icon = ctk.CTkButton(container, text="Browse", command=self._browse_icon, corner_radius=10, fg_color="#4F46E5", hover_color="#4338CA", text_color="white")
		btn_browse_icon.grid(row=2, column=2, padx=12, pady=6)

		# Output directory
		lbl_out = ctk.CTkLabel(container, text="Output directory")
		lbl_out.grid(row=3, column=0, sticky="w", padx=12, pady=6)
		self.entry_out = ctk.CTkEntry(container, placeholder_text="Defaults to ./dist")
		self.entry_out.grid(row=3, column=1, sticky="ew", padx=(0, 12), pady=6)
		btn_browse_out = ctk.CTkButton(container, text="Browse", command=self._browse_out, corner_radius=10, fg_color="#4F46E5", hover_color="#4338CA", text_color="white")
		btn_browse_out.grid(row=3, column=2, padx=12, pady=6)

		# Options row
		options_frame = ctk.CTkFrame(container, corner_radius=12)
		options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 8))

		self.chk_onefile_var = ctk.BooleanVar(value=True)
		self.chk_windowed_var = ctk.BooleanVar(value=True)
		self.chk_clean_var = ctk.BooleanVar(value=True)

		chk_onefile = ctk.CTkCheckBox(options_frame, text="One file", variable=self.chk_onefile_var)
		chk_onefile.grid(row=0, column=0, padx=8, pady=8, sticky="w")

		chk_windowed = ctk.CTkCheckBox(options_frame, text="Windowed (no console)", variable=self.chk_windowed_var)
		chk_windowed.grid(row=0, column=1, padx=8, pady=8, sticky="w")

		chk_clean = ctk.CTkCheckBox(options_frame, text="Clean build", variable=self.chk_clean_var)
		chk_clean.grid(row=0, column=2, padx=8, pady=8, sticky="w")

		# Advanced: bundle identifier (macOS)
		self.bundle_id_entry = None
		if sys.platform == "darwin":
			lbl_bid = ctk.CTkLabel(options_frame, text="Bundle ID (macOS)")
			lbl_bid.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="w")
			self.bundle_id_entry = ctk.CTkEntry(options_frame, placeholder_text="com.example.myapp (optional)")
			self.bundle_id_entry.grid(row=1, column=1, columnspan=2, padx=8, pady=(0, 8), sticky="ew")
			options_frame.grid_columnconfigure(1, weight=1)

		# Build button
		self.btn_build = ctk.CTkButton(container, text=self._build_button_label(), command=self._on_build_clicked, corner_radius=12, height=42, fg_color="#22C55E", hover_color="#16A34A", text_color="white")
		self.btn_build.grid(row=5, column=0, columnspan=3, padx=12, pady=(4, 8), sticky="ew")

		# Output log
		log_label = ctk.CTkLabel(container, text="Build log")
		log_label.grid(row=6, column=0, sticky="w", padx=12, pady=(8, 6))
		self.txt_log = ctk.CTkTextbox(container, height=220)
		self.txt_log.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=12, pady=(0, 12))
		container.grid_rowconfigure(7, weight=1)

		# Footer
		self.footer = ctk.CTkLabel(self, text=self._footer_text(), font=("SF Pro Text", 12))
		self.footer.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

	def _build_button_label(self) -> str:
		system_name = platform.system()
		if system_name == "Windows":
			return "Build .exe with PyInstaller"
		if system_name == "Darwin":
			return "Build .app with PyInstaller"
		return "Build executable with PyInstaller"

	def _footer_text(self) -> str:
		sys_name = platform.system()
		target = ".exe" if sys_name == "Windows" else ".app" if sys_name == "Darwin" else "binary"
		return f"Detected OS: {sys_name} — Target: {target}"

	def _browse_input(self) -> None:
		file_path = fd.askopenfilename(title="Select Python file", filetypes=[("Python files", "*.py"), ("All files", "*.*")])
		if file_path:
			self.entry_input.delete(0, "end")
			self.entry_input.insert(0, file_path)
			if not self.entry_name.get().strip():
				base = os.path.splitext(os.path.basename(file_path))[0]
				self.entry_name.insert(0, base)

	def _browse_icon(self) -> None:
		if sys.platform == "win32":
			types = [("Icon files", "*.ico"), ("All files", "*.*")]
		else:
			types = [("ICNS files", "*.icns"), ("All files", "*.*")]
		file_path = fd.askopenfilename(title="Select icon", filetypes=types)
		if file_path:
			self.entry_icon.delete(0, "end")
			self.entry_icon.insert(0, file_path)

	def _browse_out(self) -> None:
		directory = fd.askdirectory(title="Select output directory")
		if directory:
			self.entry_out.delete(0, "end")
			self.entry_out.insert(0, directory)

	def _append_log(self, text: str) -> None:
		self.txt_log.insert("end", text)
		self.txt_log.see("end")

	def _validate_inputs(self) -> tuple[bool, str]:
		src = self.entry_input.get().strip()
		if not src:
			return False, "Please select a Python file.\n"
		if not os.path.isfile(src):
			return False, "Selected Python file does not exist.\n"
		if not src.lower().endswith(".py"):
			return False, "Selected file must be a .py file.\n"

		name = self.entry_name.get().strip() or os.path.splitext(os.path.basename(src))[0]
		if not name:
			return False, "Please provide an app name.\n"

		icon = self.entry_icon.get().strip()
		if icon:
			if sys.platform == "win32" and not icon.lower().endswith(".ico"):
				return False, "Windows icon must be a .ico file.\n"
			if sys.platform == "darwin" and not icon.lower().endswith(".icns"):
				return False, "macOS icon must be a .icns file.\n"
			if not os.path.isfile(icon):
				return False, "Icon path does not exist.\n"

		out_dir = self.entry_out.get().strip()
		if out_dir and not os.path.isdir(out_dir):
			try:
				os.makedirs(out_dir, exist_ok=True)
			except Exception as exc:
				return False, f"Failed to create output directory: {exc}\n"

		return True, ""

	def _on_build_clicked(self) -> None:
		with self._build_state_lock:
			if self._currently_building:
				mb.showinfo("Build in progress", "Please wait for the current build to finish.")
				return
			self._currently_building = True

		ok, err = self._validate_inputs()
		if not ok:
			with self._build_state_lock:
				self._currently_building = False
			mb.showerror("Invalid input", err)
			return

		self.txt_log.delete("1.0", "end")
		self._append_log("Starting build...\n\n")

		self.btn_build.configure(state="disabled", text="Building...")

		self._build_thread = threading.Thread(target=self._run_build, daemon=True)
		self._build_thread.start()

	def _compose_command(self) -> tuple[list[str], str]:
		src = self.entry_input.get().strip()
		name = self.entry_name.get().strip() or os.path.splitext(os.path.basename(src))[0]
		icon = self.entry_icon.get().strip()
		out_dir = self.entry_out.get().strip()

		args: list[str] = [sys.executable, "-m", "PyInstaller", src]

		# Common flags
		if self.chk_clean_var.get():
			args.append("--clean")

		if self.chk_onefile_var.get():
			args.append("--onefile")

		if self.chk_windowed_var.get():
			args.append("--windowed")

		if name:
			args.extend(["--name", name])

		if icon:
			args.extend(["--icon", icon])

		# macOS bundle identifier
		if sys.platform == "darwin" and self.bundle_id_entry is not None:
			bid = self.bundle_id_entry.get().strip()
			if bid:
				args.extend(["--osx-bundle-identifier", bid])

		# Output directories
		if out_dir:
			dist_dir = os.path.join(out_dir, "dist")
			build_dir = os.path.join(out_dir, "build")
			args.extend(["--distpath", dist_dir, "--workpath", build_dir])

		# Notes for platform expectations
		# - Windows: .exe will be created in dist/<name>.exe (onefile) or dist/<name>/<name>.exe
		# - macOS: with --windowed, PyInstaller emits an .app bundle; with --onefile it still creates a .app

		return args, name

	def _run_build(self) -> None:
		try:
			args, name = self._compose_command()

			self._append_log("Command:\n")
			self._append_log(" " + " ".join(shlex.quote(a) for a in args) + "\n\n")

			process = subprocess.Popen(
				args,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				bufsize=1,
			)

			assert process.stdout is not None
			for line in process.stdout:
				self._append_log(line)

			code = process.wait()

			if code == 0:
				self._append_log("\nBuild completed successfully.\n")
				artifact_hint = self._artifact_hint(name)
				if artifact_hint:
					self._append_log(artifact_hint + "\n")
				mb.showinfo("Success", "Build completed successfully.")
			else:
				self._append_log(f"\nBuild failed with exit code {code}.\n")
				mb.showerror("Build failed", f"PyInstaller exited with code {code}.")
		except FileNotFoundError:
			self._append_log("PyInstaller not found. Installing...\n")
			try:
				subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
				self._append_log("PyInstaller installed. Please click Build again.\n")
			except Exception as exc:
				self._append_log(f"Failed to install PyInstaller: {exc}\n")
				mb.showerror("Missing dependency", "Failed to install PyInstaller automatically.")
		except Exception as exc:
			self._append_log(f"Unexpected error: {exc}\n")
			mb.showerror("Error", f"Unexpected error: {exc}")
		finally:
			with self._build_state_lock:
				self._currently_building = False
			self.btn_build.configure(state="normal", text=self._build_button_label())

	def _artifact_hint(self, name: str) -> str:
		sys_name = platform.system()
		out_dir = self.entry_out.get().strip() or os.getcwd()
		dist_dir = os.path.join(out_dir, "dist")
		if sys_name == "Windows":
			if self.chk_onefile_var.get():
				return f"Artifact: {os.path.join(dist_dir, name + '.exe')}"
			return f"Artifact: {os.path.join(dist_dir, name, name + '.exe')}"
		if sys_name == "Darwin":
			return f"Artifact: {os.path.join(dist_dir, name + '.app')}"
		return f"Artifacts in: {dist_dir}"


def main() -> None:
	_ensure_pyinstaller_installed()
	app = BuilderApp()
	app.mainloop()


if __name__ == "__main__":
	main()


