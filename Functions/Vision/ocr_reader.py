"""
OCR Reader for scanning and reading text from images
"""

import easyocr
import numpy as np

class OCRReader:
    def __init__(self, languages=['en']):
        """
        Initialize the OCR reader.
        
        Args:
            languages (list): List of language codes to recognize (default: ['en'])
        """
        self.languages = languages
        self.reader = None
        
    def initialize(self):
        """Initialize the EasyOCR reader."""
        try:
            print(f"Initializing OCR reader for languages: {self.languages}")
            self.reader = easyocr.Reader(self.languages, gpu=False)
            print("OCR reader initialized")
            return True
        except Exception as e:
            print(f"Error initializing OCR reader: {e}")
            return False
    
    def read_text(self, image):
        """
        Read text from an image.
        
        Args:
            image: Image array (numpy array from OpenCV)
            
        Returns:
            list: List of tuples containing (bounding_box, text, confidence)
        """
        if self.reader is None:
            if not self.initialize():
                return []
        
        try:
            # Perform OCR
            results = self.reader.readtext(image)
            return results
        except Exception as e:
            print(f"Error reading text from image: {e}")
            return []
    
    def read_text_simple(self, image):
        """
        Read text from an image and return simple list of strings.
        
        Args:
            image: Image array (numpy array from OpenCV)
            
        Returns:
            list: List of recognized text strings
        """
        results = self.read_text(image)
        return [text for (bbox, text, confidence) in results]
    
    def read_nutrition_label(self, image):
        """
        Read and parse nutrition label from an image.
        
        Args:
            image: Image array (numpy array from OpenCV)
            
        Returns:
            dict: Dictionary containing nutrition information
        """
        results = self.read_text(image)
        
        nutrition_info = {
            'raw_text': [],
            'calories': None,
            'protein': None,
            'fat': None,
            'carbs': None
        }
        
        # Extract all text
        for (bbox, text, confidence) in results:
            nutrition_info['raw_text'].append(text)
            text_lower = text.lower()
            
            # Look for common nutrition keywords
            if 'calor' in text_lower:
                nutrition_info['calories'] = text
            elif 'protein' in text_lower:
                nutrition_info['protein'] = text
            elif 'fat' in text_lower and 'trans' not in text_lower:
                nutrition_info['fat'] = text
            elif 'carb' in text_lower:
                nutrition_info['carbs'] = text
        
        return nutrition_info


# Example usage
if __name__ == "__main__":
    import cv2
    
    # Create OCR reader
    ocr = OCRReader()
    
    # Example: Read from an image file
    # image = cv2.imread('nutrition_label.jpg')
    # results = ocr.read_text(image)
    # 
    # for (bbox, text, confidence) in results:
    #     print(f"Text: {text} (Confidence: {confidence:.2f})")
