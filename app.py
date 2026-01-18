import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import os


class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Photo Capture")
        
        # Create captures directory if it doesn't exist
        self.capture_dir = "captures"
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir)
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam")
            self.root.destroy()
            return
        
        # Create GUI elements
        self.video_label = tk.Label(root)
        self.video_label.pack(padx=10, pady=10)
        
        self.capture_button = tk.Button(
            root, 
            text="Take Photo", 
            command=self.capture_photo,
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=10
        )
        self.capture_button.pack(pady=10)
        
        self.info_label = tk.Label(root, text="", font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        # Start video feed
        self.update_frame()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_frame(self):
        """Update the video frame continuously"""
        ret, frame = self.cap.read()
        
        if ret:
            # Convert from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Store current frame for capture
            self.current_frame = frame
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Convert to ImageTk
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        
        # Schedule next update
        self.root.after(10, self.update_frame)
    
    def capture_photo(self):
        """Capture and save the current frame"""
        if hasattr(self, 'current_frame'):
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.capture_dir}/photo_{timestamp}.jpg"
            
            # Save the image
            cv2.imwrite(filename, self.current_frame)
            
            # Update info label
            self.info_label.config(text=f"Photo saved: {filename}", fg="green")
            print(f"Photo saved: {filename}")
            
            # Clear message after 3 seconds
            self.root.after(3000, lambda: self.info_label.config(text=""))
    
    def on_closing(self):
        """Clean up resources when closing"""
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
