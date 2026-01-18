#!/usr/bin/env python3
"""
Simple microphone test - displays recognized speech in a window
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import scrolledtext
from Peripherals.mic import Microphone
import threading

class MicTester:
    def __init__(self):
        self.mic = Microphone()
        self.is_running = False
        
        # Create window
        self.window = tk.Tk()
        self.window.title("Microphone Test - Speak Now")
        self.window.geometry("600x400")
        
        # Status label
        self.status_label = tk.Label(
            self.window, 
            text="🎤 Listening...", 
            font=("Arial", 16, "bold"),
            fg="green"
        )
        self.status_label.pack(pady=10)
        
        # Text display area
        self.text_area = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 12)
        )
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Initial message
        self.text_area.insert(tk.END, "Microphone Test Ready\n")
        self.text_area.insert(tk.END, "=" * 50 + "\n\n")
        self.text_area.insert(tk.END, "Start speaking... Everything you say will appear here.\n\n")
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="Clear Text",
            command=self.clear_text,
            font=("Arial", 10)
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(
            button_frame,
            text="Quit",
            command=self.quit_app,
            font=("Arial", 10)
        )
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        
    def add_text(self, text, tag=None):
        """Add text to the display area."""
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)  # Auto-scroll to bottom
        
    def set_status(self, text, color="green"):
        """Update status label."""
        self.status_label.config(text=text, fg=color)
        
    def clear_text(self):
        """Clear the text area."""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Text cleared. Continue speaking...\n\n")
        
    def listen_loop(self):
        """Continuous listening loop."""
        counter = 1
        self.is_running = True
        
        while self.is_running:
            try:
                self.set_status("🎤 Listening...", "green")
                
                # Listen for speech
                text = self.mic.listen_for_command(timeout=5, phrase_time_limit=10)
                
                if text:
                    self.set_status("✅ Speech Recognized!", "blue")
                    timestamp = f"[{counter}] "
                    self.add_text(f"{timestamp}You said: \"{text}\"\n\n")
                    counter += 1
                else:
                    self.set_status("⏳ No speech detected, listening again...", "orange")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.set_status(f"❌ Error: {str(e)}", "red")
                self.add_text(f"ERROR: {str(e)}\n\n")
                
        self.set_status("⏹ Stopped", "gray")
        
    def start(self):
        """Start the microphone test."""
        # Start listening in a separate thread
        listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        listen_thread.start()
        
        # Start GUI main loop
        self.window.mainloop()
        
    def quit_app(self):
        """Clean up and quit."""
        self.is_running = False
        self.mic.release()
        self.window.quit()
        self.window.destroy()


if __name__ == "__main__":
    print("Starting Microphone Test...")
    print("A window will open - speak and see your words appear!")
    
    tester = MicTester()
    tester.start()
