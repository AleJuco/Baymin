"""
Allergy checking system using OpenRouter API (Gemini via OpenRouter)
Analyzes food images and checks against user allergies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import base64
import time
import requests
from PIL import Image

class AllergyChecker:
    def __init__(self, api_key=None, user_data_path="../current_user.json"):
        """
        Initialize allergy checker with OpenRouter API.
        
        Args:
            api_key (str): OpenRouter API key (or set OPENROUTER_API_KEY env var)
            user_data_path (str): Path to current_user.json file
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("No API key provided. Set OPENROUTER_API_KEY environment variable or pass api_key parameter")
        
        # OpenRouter configuration
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model_name = "google/gemini-2.0-flash-001"  # Gemini via OpenRouter
        
        # Load current user data
        self.user_data_path = os.path.join(
            os.path.dirname(__file__), 
            user_data_path
        )
        self.current_user = self.load_user_data()
        
    def load_user_data(self):
        """Load current user allergy data from JSON file."""
        try:
            with open(self.user_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: No current user logged in. Create current_user.json or log in via webapp.")
            return {"name": "Guest", "allergies": [], "conditions": [], "medications": []}
        except Exception as e:
            print(f"Error loading user data: {e}")
            return {"name": "Guest", "allergies": [], "conditions": [], "medications": []}
    
    def get_all_allergies(self):
        """Get allergies for the current logged-in user."""
        return self.current_user.get('allergies', [])
    
    def check_food_safety(self, image_path):
        """
        Analyze food image and check for allergens.
        
        Args:
            image_path (str): Path to food image
            
        Returns:
            dict: {
                'safe': bool,
                'allergies_found': list,
                'ingredients': list,
                'analysis': str
            }
        """
        print(f"\nAnalyzing image for allergens...")
        
        # Get all allergies to check
        allergies = self.get_all_allergies()
        if not allergies:
            print("No allergies found in user data")
            return {
                'safe': True,
                'allergies_found': [],
                'ingredients': [],
                'analysis': 'No allergies to check'
            }
        
        print(f"Checking for allergies: {', '.join(allergies)}")
        
        try:
            # Load image and encode as base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Create prompt for Gemini
            prompt = f"""FOOD ANALYSIS AND ALLERGEN DETECTION TASK

You are analyzing food/product for someone with allergies to: {', '.join(allergies)}

YOUR TASK:
1. Identify the food/product shown in this image
2. List ALL visible ingredients or typical ingredients for this food
3. Provide health information (calories, protein, carbs, fat, key nutrients)
4. CHECK for ANY form of these allergens: {', '.join(allergies)}
   - Look for whole, processed, and hidden forms
   - Check packaging labels if visible
   - Consider cross-contamination warnings

Respond in this EXACT JSON format:
{{
    "item_name": "name of food/product",
    "ingredients": ["ingredient1", "ingredient2", ...],
    "health_info": {{
        "calories": "estimated calories per serving",
        "protein": "estimated protein",
        "carbs": "estimated carbs", 
        "fat": "estimated fat",
        "key_nutrients": ["nutrient1", "nutrient2"],
        "health_benefits": "brief health benefits",
        "health_concerns": "any health concerns"
    }},
    "allergens_detected": ["allergen1", "allergen2", ...],
    "safe_to_eat": true/false,
    "reasoning": "detailed explanation"
}}"""

            # Send to OpenRouter with retry logic for rate limits
            max_retries = 3
            retry_delay = 5  # seconds
            response = None
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/baymin",
                "X-Title": "Baymin Food Analyzer"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ]
            }
            
            for attempt in range(max_retries):
                try:
                    resp = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                    
                    if resp.status_code == 429:
                        if attempt < max_retries - 1:
                            print(f"Rate limited. Waiting {retry_delay}s before retry {attempt + 2}/{max_retries}...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            resp.raise_for_status()
                    
                    resp.raise_for_status()
                    response = resp.json()
                    break  # Success, exit retry loop
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Request failed. Retrying {attempt + 2}/{max_retries}...")
                        time.sleep(retry_delay)
                    else:
                        raise
            
            if response is None:
                raise Exception("Failed to get response from OpenRouter after retries")
            
            # Extract response text
            response_text = response['choices'][0]['message']['content'].strip()
            
            # Debug: Print raw response
            print(f"\n{'='*60}")
            print("RAW API RESPONSE:")
            print(response_text)
            print("="*60)
            
            # Try to extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            
            # Format output
            safe = result.get('safe_to_eat', True)
            allergies_found = result.get('allergens_detected', [])
            
            # Double-check: verify detected allergens match our list (case-insensitive)
            verified_allergens = []
            user_allergies_lower = [a.lower() for a in allergies]
            for detected in allergies_found:
                detected_lower = detected.lower()
                # Check if detected allergen matches any user allergy (case-insensitive, partial match)
                for user_allergy in allergies:
                    if user_allergy.lower() in detected_lower or detected_lower in user_allergy.lower():
                        verified_allergens.append(user_allergy)
                        break
            
            # If allergens found but safe_to_eat is True, override to False
            if verified_allergens and safe:
                print("WARNING: Allergens detected but marked safe - changing to UNSAFE")
                safe = False
            
            print(f"\n{'='*60}")
            print(f"FOOD ANALYSIS RESULTS")
            print(f"{'='*60}")
            print(f"Item: {result.get('item_name', 'Unknown')}")
            print(f"Ingredients: {', '.join(result.get('ingredients', []))}")
            
            # Print health info
            health_info = result.get('health_info', {})
            if health_info:
                print(f"\n--- HEALTH INFORMATION ---")
                print(f"Calories: {health_info.get('calories', 'N/A')}")
                print(f"Protein: {health_info.get('protein', 'N/A')}")
                print(f"Carbs: {health_info.get('carbs', 'N/A')}")
                print(f"Fat: {health_info.get('fat', 'N/A')}")
                if health_info.get('key_nutrients'):
                    print(f"Key Nutrients: {', '.join(health_info.get('key_nutrients', []))}")
                if health_info.get('health_benefits'):
                    print(f"Health Benefits: {health_info.get('health_benefits')}")
                if health_info.get('health_concerns'):
                    print(f"Health Concerns: {health_info.get('health_concerns')}")
            
            print(f"\n--- ALLERGY CHECK ---")
            if verified_allergens:
                print(f"ALLERGENS DETECTED: {', '.join(verified_allergens)}")
                print(f"VERDICT: DO NOT EAT")
            else:
                print(f"No allergens detected")
                print(f"VERDICT: Safe to eat")
            
            print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
            print(f"{'='*60}")
            
            return {
                'safe': safe,
                'allergies_found': verified_allergens,
                'ingredients': result.get('ingredients', []),
                'health_info': health_info,
                'analysis': result.get('reasoning', '')
            }
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {response.text}")
            return {
                'safe': None,
                'allergies_found': [],
                'ingredients': [],
                'analysis': 'Failed to parse response'
            }
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return {
                'safe': None,
                'allergies_found': [],
                'ingredients': [],
                'analysis': str(e)
            }

def main():
    """Test the allergy checker."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python AllergyCheck.py <image_path>")
        print("\nMake sure to set OPENROUTER_API_KEY environment variable")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("Error: OPENROUTER_API_KEY environment variable not set")
        print("\nSet it with: $env:OPENROUTER_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Create checker and analyze
    checker = AllergyChecker()
    result = checker.check_food_safety(image_path)
    
    # Print final verdict
    print("\n" + "="*60)
    if result['safe'] is False:
        print("FINAL VERDICT: DO NOT EAT")
    elif result['safe'] is True:
        print("FINAL VERDICT: SAFE TO EAT")
    else:
        print("FINAL VERDICT: UNABLE TO DETERMINE")
    print("="*60)

if __name__ == "__main__":
    main()
