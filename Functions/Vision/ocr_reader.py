import cv2
import easyocr
import numpy as np


class OCRReader:
    def __init__(self):
        """
        Initialize EasyOCR reader for nutrition label text extraction.
        First run will download models (~500MB).
        """
        print("Initializing EasyOCR (first run downloads models)...")
        self.reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=False for Pi
        print("EasyOCR ready!")

    def read_text(self, image):
        """Extract text from nutrition labels using EasyOCR."""
        results = self.reader.readtext(image)
        
        # Extract just the text from results
        text_lines = [result[1] for result in results]
        
        return '\n'.join(text_lines)

    def extract_food_values(self, image):
        """
        Extract structured nutrition data from labels.
        Returns list of text items with confidence scores.
        """
        results = self.reader.readtext(image)
        
        extracted_data = []
        for bbox, text, confidence in results:
            if confidence > 0.3:  # Filter low confidence results
                extracted_data.append({
                    'text': text,
                    'confidence': confidence
                })
        
        return extracted_data
    
    def read_text_with_confidence(self, image, min_confidence=0.5):
        """
        Extract text with minimum confidence threshold.
        """
        results = self.reader.readtext(image)
        
        # Filter by confidence
        filtered_text = [result[1] for result in results if result[2] >= min_confidence]
        
        return '\n'.join(filtered_text)