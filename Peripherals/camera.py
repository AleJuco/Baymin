import cv2
import numpy as np
from datetime import datetime
import os

class Camera:
    def __init__(self, camera_index=0, resolution=(640, 480)):
        """
        Initialize the Camera for the Raspberry Pi.
        
        Args:
            camera_index (int): Camera device index (0 for default camera)
            resolution (tuple): Camera resolution (width, height)
        """
        self.camera_index = camera_index
        self.resolution = resolution
        self.camera = None
        
    def initialize(self):
        """Initialize the camera connection."""
        try:
            # Use DirectShow on Windows for better compatibility
            self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            if not self.camera.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Warm up camera - Windows needs a few frames
            for _ in range(5):
                self.camera.read()
            
            print(f"Camera initialized at {self.resolution[0]}x{self.resolution[1]}")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self):
        """
        Capture a single image from the camera.
        
        Returns:
            numpy.ndarray: Captured image as numpy array, or None if failed
        """
        if not self.camera or not self.camera.isOpened():
            if not self.initialize():
                return None
        
        try:
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                print("Error: Failed to capture image")
                return None
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
    
    def capture_and_save(self, save_path=None, filename=None):
        """
        Capture an image and save it to disk.
        
        Args:
            save_path (str): Directory to save the image
            filename (str): Filename for the image (auto-generated if None)
            
        Returns:
            tuple: (image, filepath) or (None, None) if failed
        """
        image = self.capture_image()
        
        if image is None:
            return None, None
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
        
        # Set default save path
        if save_path is None:
            save_path = "/tmp"
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Full filepath
        filepath = os.path.join(save_path, filename)
        
        # Save the image
        try:
            cv2.imwrite(filepath, image)
            print(f"Image saved to: {filepath}")
            return image, filepath
        except Exception as e:
            print(f"Error saving image: {e}")
            return image, None
    
    def capture_for_processing(self):
        """
        Capture an image optimized for processing (e.g., OCR, object detection).
        Returns RGB format suitable for most ML libraries.
        
        Returns:
            numpy.ndarray: Image in RGB format
        """
        image = self.capture_image()
        
        if image is not None:
            # Convert BGR (OpenCV format) to RGB (most ML libraries)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image_rgb
        
        return None
    
    def start_video_stream(self):
        """
        Start a continuous video stream (for preview or live processing).
        Use with get_frame() to retrieve frames.
        """
        if not self.camera or not self.camera.isOpened():
            self.initialize()
    
    def get_frame(self):
        """
        Get a single frame from an active video stream.
        
        Returns:
            numpy.ndarray: Current frame or None
        """
        return self.capture_image()
    
    def release(self):
        """Release the camera resource."""
        if self.camera:
            self.camera.release()
            print("Camera released")
            self.camera = None
    
    def __del__(self):
        """Ensure camera is released when object is destroyed."""
        self.release()


# Example usage
if __name__ == "__main__":
    # Initialize camera
    camera = Camera()
    
    # Capture a single image
    image = camera.capture_image()
    
    if image is not None:
        print(f"Captured image shape: {image.shape}")
    
    # Capture and save
    img, filepath = camera.capture_and_save(save_path="/tmp", filename="test.jpg")
    
    # Capture for processing (RGB format)
    rgb_image = camera.capture_for_processing()
    
    # Release camera
    camera.release()
