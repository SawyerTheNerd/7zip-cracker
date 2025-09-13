#!/usr/bin/env python3
"""
7-Zip Password Cracker GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path

class SevenZipCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("7-Zip Password Cracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.archive_file = tk.StringVar()
        self.wordlist_file = tk.StringVar()
        self.is_running = False
        self.total_passwords = 0
        self.current_password = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="7-Zip Password Cracker", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Archive file selection
        ttk.Label(main_frame, text="7-Zip Archive:").grid(row=1, column=0, sticky=tk.W, pady=5)
        archive_entry = ttk.Entry(main_frame, textvariable=self.archive_file, width=50)
        archive_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_archive).grid(row=1, column=2, pady=5)
        
        # Wordlist file selection
        ttk.Label(main_frame, text="Wordlist File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        wordlist_entry = ttk.Entry(main_frame, textvariable=self.wordlist_file, width=50)
        wordlist_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_wordlist).grid(row=2, column=2, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Cracking", 
                                      command=self.start_cracking)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_cracking, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Wordlist info label
        self.wordlist_info_label = ttk.Label(progress_frame, text="Wordlist: 0 passwords")
        self.wordlist_info_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to start...")
        self.status_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, width=70, height=15, 
                                                    wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame weights for resizing
        main_frame.rowconfigure(5, weight=1)
        
    def browse_archive(self):
        filename = filedialog.askopenfilename(
            title="Select 7-Zip Archive",
            filetypes=[("7-Zip files", "*.7z"), ("All files", "*.*")]
        )
        if filename:
            self.archive_file.set(filename)
            
    def browse_wordlist(self):
        filename = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.wordlist_file.set(filename)
            self.update_wordlist_info()
            
    def start_cracking(self):
        if not self.archive_file.get():
            messagebox.showerror("Error", "Please select a 7-Zip archive file.")
            return
            
        if not self.wordlist_file.get():
            messagebox.showerror("Error", "Please select a wordlist file.")
            return
            
        if not os.path.exists(self.archive_file.get()):
            messagebox.showerror("Error", f"Archive file not found: {self.archive_file.get()}")
            return
            
        if not os.path.exists(self.wordlist_file.get()):
            messagebox.showerror("Error", f"Wordlist file not found: {self.wordlist_file.get()}")
            return
            
        # Check if 7z.exe is available
        seven_zip_paths = [
            "C:\\Program Files\\7-Zip\\7z.exe",
            "C:\\Program Files (x86)\\7-Zip\\7z.exe",
            "7z.exe"  # If it's in PATH
        ]
        
        self.seven_zip_exe = None
        for path in seven_zip_paths:
            if os.path.exists(path):
                self.seven_zip_exe = path
                break
                
        if not self.seven_zip_exe:
            messagebox.showerror("Error", "7z.exe not found. Please install 7-Zip or ensure it's in your PATH.")
            return
            
        # Count passwords in wordlist
        try:
            with open(self.wordlist_file.get(), 'r', encoding='utf-8', errors='ignore') as f:
                self.total_passwords = sum(1 for _ in f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read wordlist: {str(e)}")
            return
            
        self.wordlist_info_label.config(text=f"Wordlist: {self.total_passwords} passwords")
        
        self.is_running = True
        self.current_password = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = self.total_passwords
        self.status_label.config(text="Cracking in progress...")
        
        self.append_output("Starting 7-Zip password cracker...")
        self.append_output(f"Archive: {self.archive_file.get()}")
        self.append_output(f"Wordlist: {self.wordlist_file.get()}")
        self.append_output("-" * 50)
        
        # Run in separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_cracker)
        thread.daemon = True
        thread.start()
        
    def stop_cracking(self):
        self.is_running = False
        self.append_output("\nOperation stopped by user.")
        self.cleanup_after_cracking()
        
    def run_cracker(self):
        try:
            # Read the wordlist
            with open(self.wordlist_file.get(), 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            
            total_passwords = len(passwords)
            self.update_progress(0, total_passwords)
            
            cracked = False
            found_password = None
            
            for i, password in enumerate(passwords, 1):
                if not self.is_running:
                    break
                    
                self.update_progress(i, total_passwords)
                self.append_output(f"Trying password: {password}")
                
                # Try to extract with current password
                try:
                    process = subprocess.Popen(
                        [self.seven_zip_exe, "x", f"-p{password}", self.archive_file.get(), "-aoa"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()
                    
                    if process.returncode == 0:
                        cracked = True
                        found_password = password
                        self.append_output(f"\nSUCCESS: Password found: {password}")
                        break
                        
                except Exception as e:
                    self.append_output(f"Error trying password {password}: {str(e)}")
            
            if cracked:
                self.append_output(f"\nPassword successfully cracked: {found_password}")
            else:
                self.append_output("\nPassword not found in the wordlist.")
                
        except Exception as e:
            self.append_output(f"Error during cracking process: {str(e)}")
        finally:
            self.cleanup_after_cracking()
            
    def cleanup_after_cracking(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Ready to start...")
        
    def update_wordlist_info(self):
        """Update wordlist information when a new file is selected"""
        if self.wordlist_file.get() and os.path.exists(self.wordlist_file.get()):
            try:
                with open(self.wordlist_file.get(), 'r', encoding='utf-8', errors='ignore') as f:
                    count = sum(1 for _ in f)
                self.wordlist_info_label.config(text=f"Wordlist: {count} passwords")
            except Exception as e:
                self.wordlist_info_label.config(text="Wordlist: Error reading file")
        else:
            self.wordlist_info_label.config(text="Wordlist: 0 passwords")
            
    def update_progress(self, current, total):
        """Update progress bar and status"""
        if total > 0:
            progress_percent = (current / total) * 100
            self.progress_bar['value'] = current
            self.status_label.config(text=f"Cracking... {current}/{total} ({progress_percent:.1f}%)")
        
    def append_output(self, text):
        def update_output():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, text + "\n")
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)
            
        self.root.after(0, update_output)
        
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_label.config(text="Output cleared. Ready to start...")

def main():
    root = tk.Tk()
    app = SevenZipCrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()