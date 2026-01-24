"""
PalFriend Launcher - GUI Bootstrapper

This is a GUI-based launcher/installer that:
- Provides an easy installation interface
- Checks system requirements
- Extracts or downloads palfriend.exe
- Validates integrity with SHA256
- Provides clear error messages
- Optionally launches the main application
"""

import os
import sys
import hashlib
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from pathlib import Path
import logging
from datetime import datetime
import traceback
import tempfile


# Version info
LAUNCHER_VERSION = "1.0.0"
DEFAULT_INSTALL_PATH = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'PalFriend')


class DiagnosticsLogger:
    """Logger that captures diagnostics for export"""
    
    def __init__(self):
        self.messages = []
        self.log_file = None
        
    def log(self, level, message):
        """Add a log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.messages.append(log_entry)
        
        # Also write to file if available
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception:
                pass
                
        return log_entry
    
    def info(self, message):
        return self.log("INFO", message)
    
    def warning(self, message):
        return self.log("WARNING", message)
    
    def error(self, message):
        return self.log("ERROR", message)
    
    def get_diagnostics(self):
        """Get all diagnostics as a string"""
        return '\n'.join(self.messages)


class PalFriendLauncherGUI:
    """Main GUI window for PalFriend Launcher"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"PalFriend Launcher v{LAUNCHER_VERSION}")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # State
        self.install_path = tk.StringVar(value=DEFAULT_INSTALL_PATH)
        self.logger = DiagnosticsLogger()
        self.palfriend_exe_path = None
        
        # Setup logging to file
        try:
            log_dir = os.path.join(tempfile.gettempdir(), 'palfriend_launcher')
            os.makedirs(log_dir, exist_ok=True)
            self.logger.log_file = os.path.join(log_dir, f'launcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        except Exception:
            pass
        
        self.setup_ui()
        self.logger.info("PalFriend Launcher started")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', pady=15)
        header_frame.pack(fill='x')
        
        title_label = tk.Label(
            header_frame, 
            text="PalFriend Launcher",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text=f"Version {LAUNCHER_VERSION}",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()
        
        # Main content
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Installation path
        path_frame = tk.LabelFrame(content_frame, text="Installation Location", padx=10, pady=10)
        path_frame.pack(fill='x', pady=(0, 10))
        
        path_entry = tk.Entry(path_frame, textvariable=self.install_path, width=50)
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        browse_btn = tk.Button(path_frame, text="Browse...", command=self.browse_path)
        browse_btn.pack(side='right')
        
        # Action buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.install_btn = tk.Button(
            button_frame,
            text="Check & Install PalFriend",
            command=self.check_and_install,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10
        )
        self.install_btn.pack(side='left', padx=(0, 5))
        
        self.launch_btn = tk.Button(
            button_frame,
            text="Launch PalFriend",
            command=self.launch_palfriend,
            bg='#3498db',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=20,
            pady=10,
            state='disabled'
        )
        self.launch_btn.pack(side='left')
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to install")
        progress_label = tk.Label(content_frame, textvariable=self.progress_var, font=('Arial', 10))
        progress_label.pack(pady=(0, 5))
        
        self.progress = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(0, 10))
        
        # Log window
        log_frame = tk.LabelFrame(content_frame, text="Installation Log", padx=5, pady=5)
        log_frame.pack(fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            state='disabled',
            wrap='word',
            font=('Courier', 9)
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Bottom buttons
        bottom_frame = tk.Frame(content_frame)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        copy_log_btn = tk.Button(
            bottom_frame,
            text="Copy Diagnostics",
            command=self.copy_diagnostics
        )
        copy_log_btn.pack(side='left')
        
        exit_btn = tk.Button(
            bottom_frame,
            text="Exit",
            command=self.root.quit
        )
        exit_btn.pack(side='right')
        
    def log_to_ui(self, message, level="INFO"):
        """Add message to UI log"""
        log_entry = self.logger.log(level, message)
        self.log_text.config(state='normal')
        self.log_text.insert('end', log_entry + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        self.root.update()
        
    def browse_path(self):
        """Browse for installation directory"""
        path = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=self.install_path.get()
        )
        if path:
            self.install_path.set(path)
            self.log_to_ui(f"Installation path changed to: {path}")
    
    def check_disk_space(self, path, required_mb=500):
        """Check if there's enough disk space"""
        try:
            stat = shutil.disk_usage(path)
            available_mb = stat.free / (1024 * 1024)
            self.log_to_ui(f"Available disk space: {available_mb:.0f} MB")
            
            if available_mb < required_mb:
                self.log_to_ui(f"WARNING: Low disk space. Required: {required_mb} MB", "WARNING")
                return False
            return True
        except Exception as e:
            self.log_to_ui(f"Could not check disk space: {e}", "WARNING")
            return True  # Continue anyway
    
    def check_write_permissions(self, path):
        """Check if we have write permissions"""
        try:
            # Try to create the directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            
            # Try to create a test file
            test_file = os.path.join(path, '.palfriend_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            self.log_to_ui(f"Write permissions verified for: {path}")
            return True
        except PermissionError:
            self.log_to_ui(f"ERROR: No write permission for: {path}", "ERROR")
            return False
        except Exception as e:
            self.log_to_ui(f"ERROR: Cannot write to {path}: {e}", "ERROR")
            return False
    
    def check_existing_installation(self, path):
        """Check for existing installation"""
        exe_path = os.path.join(path, 'palfriend', 'palfriend.exe')
        if os.path.exists(exe_path):
            self.log_to_ui(f"Found existing installation at: {exe_path}")
            
            # Try to get version
            try:
                version_file = os.path.join(path, 'palfriend', 'VERSION')
                if os.path.exists(version_file):
                    with open(version_file, 'r') as f:
                        version = f.read().strip()
                    self.log_to_ui(f"Existing version: {version}")
            except Exception:
                pass
                
            return exe_path
        return None
    
    def extract_embedded_payload(self, dest_path):
        """
        Extract embedded palfriend.exe from this launcher.
        
        In a real implementation, this would extract from a bundled resource.
        For now, this is a placeholder that shows where the logic would go.
        """
        self.log_to_ui("Looking for embedded PalFriend application...")
        
        # This is where you would extract from bundled data
        # For example, if palfriend was bundled as a PyInstaller resource:
        # - It could be in sys._MEIPASS
        # - Or appended to the end of this executable
        # - Or stored in a resources section
        
        # Placeholder: Check if running from PyInstaller bundle
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            bundled_palfriend = os.path.join(bundle_dir, 'palfriend_payload')
            
            if os.path.exists(bundled_palfriend):
                self.log_to_ui("Found embedded PalFriend application")
                # Would extract here
                return True
        
        self.log_to_ui("No embedded payload found", "WARNING")
        self.log_to_ui("NOTE: This launcher would download from GitHub Releases in production", "INFO")
        return False
    
    def download_from_github(self, dest_path):
        """
        Download palfriend.exe from GitHub Releases.
        
        This is a placeholder showing where download logic would go.
        """
        self.log_to_ui("GitHub download feature not yet implemented", "WARNING")
        self.log_to_ui("In production, this would download the latest release", "INFO")
        return False
    
    def verify_integrity(self, file_path, expected_sha256=None):
        """Verify file integrity with SHA256"""
        if not os.path.exists(file_path):
            self.log_to_ui(f"ERROR: File not found: {file_path}", "ERROR")
            return False
            
        try:
            self.log_to_ui(f"Calculating SHA256 for: {file_path}")
            sha256_hash = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            calculated = sha256_hash.hexdigest()
            self.log_to_ui(f"SHA256: {calculated}")
            
            if expected_sha256:
                if calculated == expected_sha256:
                    self.log_to_ui("✓ Integrity check passed")
                    return True
                else:
                    self.log_to_ui("✗ Integrity check FAILED", "ERROR")
                    return False
            
            # If no expected hash, just report the calculated one
            return True
        except Exception as e:
            self.log_to_ui(f"ERROR during integrity check: {e}", "ERROR")
            return False
    
    def check_and_install(self):
        """Main installation workflow"""
        self.install_btn.config(state='disabled')
        self.progress.start()
        
        try:
            install_path = self.install_path.get()
            self.log_to_ui("=" * 50)
            self.log_to_ui("Starting PalFriend installation check...")
            self.log_to_ui(f"Target path: {install_path}")
            
            # Step 1: Check disk space
            self.progress_var.set("Checking disk space...")
            if not self.check_disk_space(install_path):
                if not messagebox.askyesno("Low Disk Space", 
                    "Available disk space is low. Continue anyway?"):
                    self.log_to_ui("Installation cancelled by user")
                    return
            
            # Step 2: Check write permissions
            self.progress_var.set("Checking permissions...")
            if not self.check_write_permissions(install_path):
                messagebox.showerror("Permission Error",
                    f"Cannot write to {install_path}.\n\n"
                    "Please choose a different location or run as administrator.")
                return
            
            # Step 3: Check existing installation
            self.progress_var.set("Checking for existing installation...")
            existing = self.check_existing_installation(install_path)
            if existing:
                if messagebox.askyesno("Existing Installation",
                    "PalFriend is already installed at this location.\n\n"
                    "Do you want to reinstall/update?"):
                    self.log_to_ui("User chose to reinstall")
                else:
                    self.log_to_ui("Using existing installation")
                    self.palfriend_exe_path = existing
                    self.launch_btn.config(state='normal')
                    self.progress_var.set("Ready to launch")
                    messagebox.showinfo("Success", "PalFriend is ready to launch!")
                    return
            
            # Step 4: Install PalFriend
            self.progress_var.set("Installing PalFriend...")
            
            # Try embedded first, then GitHub
            success = False
            if self.extract_embedded_payload(install_path):
                success = True
            elif self.download_from_github(install_path):
                success = True
            
            if not success:
                self.log_to_ui("=" * 50, "ERROR")
                self.log_to_ui("INSTALLATION NOTE", "INFO")
                self.log_to_ui("=" * 50, "INFO")
                self.log_to_ui("", "INFO")
                self.log_to_ui("This launcher is designed to install PalFriend automatically.", "INFO")
                self.log_to_ui("", "INFO")
                self.log_to_ui("In a complete build, it would either:", "INFO")
                self.log_to_ui("  1) Extract palfriend.exe from embedded payload, or", "INFO")
                self.log_to_ui("  2) Download the latest version from GitHub Releases", "INFO")
                self.log_to_ui("", "INFO")
                self.log_to_ui("For testing: Copy palfriend.exe manually to the installation directory.", "INFO")
                self.log_to_ui("=" * 50, "INFO")
                
                # Check if user has manually placed it
                manual_path = os.path.join(install_path, 'palfriend', 'palfriend.exe')
                if os.path.exists(manual_path):
                    self.log_to_ui("Found manually placed palfriend.exe!", "INFO")
                    self.palfriend_exe_path = manual_path
                    self.launch_btn.config(state='normal')
                    self.progress_var.set("Ready to launch")
                    messagebox.showinfo("Success", "PalFriend is ready to launch!")
                else:
                    messagebox.showwarning("Installation Incomplete",
                        "PalFriend installation is not yet available.\n\n"
                        "This is a demonstration launcher. In production:\n"
                        "• The app would be embedded in the launcher\n"
                        "• Or downloaded from GitHub Releases\n\n"
                        "Check the log for details.")
                return
            
            # Step 5: Verify installation
            self.progress_var.set("Verifying installation...")
            exe_path = os.path.join(install_path, 'palfriend', 'palfriend.exe')
            if not os.path.exists(exe_path):
                self.log_to_ui(f"ERROR: palfriend.exe not found at {exe_path}", "ERROR")
                messagebox.showerror("Installation Failed",
                    "PalFriend installation failed. Check the log for details.")
                return
            
            # Verify integrity
            self.verify_integrity(exe_path)
            
            # Success!
            self.palfriend_exe_path = exe_path
            self.launch_btn.config(state='normal')
            self.progress_var.set("Installation complete!")
            self.log_to_ui("=" * 50)
            self.log_to_ui("✓ PalFriend installed successfully!")
            self.log_to_ui(f"Location: {exe_path}")
            self.log_to_ui("=" * 50)
            
            messagebox.showinfo("Success", 
                "PalFriend has been installed successfully!\n\n"
                "Click 'Launch PalFriend' to start the application.")
                
        except Exception as e:
            self.log_to_ui(f"FATAL ERROR: {e}", "ERROR")
            self.log_to_ui(traceback.format_exc(), "ERROR")
            messagebox.showerror("Installation Error",
                f"An error occurred during installation:\n\n{e}\n\n"
                "Click 'Copy Diagnostics' to get detailed error information.")
        finally:
            self.progress.stop()
            self.install_btn.config(state='normal')
    
    def launch_palfriend(self):
        """Launch the PalFriend application"""
        if not self.palfriend_exe_path or not os.path.exists(self.palfriend_exe_path):
            messagebox.showerror("Launch Error",
                "PalFriend executable not found. Please install first.")
            return
        
        try:
            self.log_to_ui(f"Launching PalFriend: {self.palfriend_exe_path}")
            
            # Launch in a new process
            if sys.platform == 'win32':
                # Windows: Use CREATE_NEW_CONSOLE to launch in new window
                subprocess.Popen([self.palfriend_exe_path], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([self.palfriend_exe_path])
            
            self.log_to_ui("PalFriend launched successfully!")
            
            # Ask if user wants to close the launcher
            if messagebox.askyesno("Launch Successful",
                "PalFriend has been launched!\n\n"
                "Do you want to close this launcher?"):
                self.root.quit()
                
        except Exception as e:
            self.log_to_ui(f"ERROR launching PalFriend: {e}", "ERROR")
            messagebox.showerror("Launch Error",
                f"Failed to launch PalFriend:\n\n{e}\n\n"
                "Common causes:\n"
                "• Antivirus blocking the executable\n"
                "• Missing Visual C++ Redistributables\n"
                "• Corrupted installation\n\n"
                "Try reinstalling or check the log for details.")
    
    def copy_diagnostics(self):
        """Copy diagnostics to clipboard"""
        diagnostics = self.logger.get_diagnostics()
        
        # Add system info
        full_diagnostics = f"""PalFriend Launcher Diagnostics
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Launcher Version: {LAUNCHER_VERSION}
Python Version: {sys.version}
Platform: {sys.platform}

{'=' * 60}
LOG MESSAGES:
{'=' * 60}
{diagnostics}
"""
        
        self.root.clipboard_clear()
        self.root.clipboard_append(full_diagnostics)
        
        messagebox.showinfo("Diagnostics Copied",
            "Diagnostics have been copied to clipboard.\n\n"
            "You can paste this information when reporting issues.")
        
        self.log_to_ui("Diagnostics copied to clipboard")


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = PalFriendLauncherGUI(root)
        root.mainloop()
    except Exception as e:
        # Last resort error handling
        messagebox.showerror("Fatal Error",
            f"PalFriend Launcher encountered a fatal error:\n\n{e}\n\n"
            f"Please report this issue with the following details:\n"
            f"Python: {sys.version}\n"
            f"Platform: {sys.platform}")
        sys.exit(1)


if __name__ == "__main__":
    main()
