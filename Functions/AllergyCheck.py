"""
Allergy checking system using Google Gemini Vision
Analyzes food images and checks against user allergies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import google.generativeai as genai
from PIL import Image

class AllergyChecker:
    def __init__(self, api_key=None, user_data_path="../current_user.json"):
        """
        Initialize allergy checker with Gemini API.
        
        Args:
            api_key (str): Google Gemini API key (or set GEMINI_API_KEY env var)
            user_data_path (str): Path to current_user.json file
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("No API key provided. Set GEMINI_API_KEY environment variable or pass api_key parameter")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
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
            print(f"⚠️ No current user logged in. Create current_user.json or log in via webapp.")
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
        print(f"\n🔍 Analyzing image for allergens...")
        
        # Get all allergies to check
        allergies = self.get_all_allergies()
        if not allergies:
            print("⚠️ No allergies found in user data")
            return {
                'safe': True,
                'allergies_found': [],
                'ingredients': [],
                'analysis': 'No allergies to check'
            }
        
        print(f"📋 Checking for: {', '.join(allergies)}")
        
        try:
            # Load image
            img = Image.open(image_path)
            
            # Create prompt for Gemini
            prompt = f"""CRITICAL ALLERGEN DETECTION TASK - Lives depend on accuracy!

You are analyzing food/product for someone with SEVERE ALLERGIES to: {', '.join(allergies)}

YOUR TASK:
1. Carefully examine EVERY visible ingredient in this image
2. Identify the food/product shown
3. List ALL ingredients you can see or that are typically in this item
4. CHECK EXTREMELY CAREFULLY for ANY form of these allergens: {', '.join(allergies)}
   - Look for whole forms (e.g., "peanuts", "whole peanuts")
   - Look for processed forms (e.g., "peanut butter", "peanut oil", "ground peanuts")
   - Look for hidden forms (e.g., "groundnut", "arachis oil")
   - Check packaging labels if visible
   - Consider cross-contamination warnings
   - Only consider food items, not unrelated objects or people.

IMPORTANT RULES:
- If you see ANY of the allergens listed above, SET safe_to_eat to FALSE
- BE CAUTIOUS: When in doubt, mark as unsafe
- List the allergen even if you're only 70% sure it's present
- "Peanut" and "peanuts" are the SAME allergen
- Check for related terms (e.g., "tree nuts" includes almonds, walnuts, etc.)

Respond in this EXACT JSON format:
{{
    "item_name": "name of food/product",
    "ingredients": ["ingredient1", "ingredient2", ...],
    "allergens_detected": ["allergen1", "allergen2", ...],
    "safe_to_eat": true/false,
    "reasoning": "detailed explanation of allergen findings"
}}

REMEMBER: It's better to falsely warn about an allergen than to miss one!"""

            # Send to Gemini
            response = self.model.generate_content([prompt, img])
            
            # Parse response
            response_text = response.text.strip()
            
            # Debug: Print raw Gemini response
            print(f"\n{'='*60}")
            print("🔍 RAW GEMINI RESPONSE:")
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
                print("⚠️ OVERRIDE: Allergens detected but marked safe - changing to UNSAFE")
                safe = False
            
            print(f"\n📦 Item: {result.get('item_name', 'Unknown')}")
            print(f"🧪 Ingredients: {', '.join(result.get('ingredients', []))}")
            
            if verified_allergens:
                print(f"\n⚠️ ALLERGENS DETECTED: {', '.join(verified_allergens)}")
                print(f"❌ DO NOT EAT")
            else:
                print(f"\n✅ No allergens detected")
                print(f"✓ Safe to eat")
            
            print(f"\n💭 Reasoning: {result.get('reasoning', 'N/A')}")
            
            return {
                'safe': safe,
                'allergies_found': verified_allergens,
                'ingredients': result.get('ingredients', []),
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
        print("\nMake sure to set GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("\nSet it with: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Create checker and analyze
    checker = AllergyChecker()
    result = checker.check_food_safety(image_path)
    
    # Print final verdict
    print("\n" + "="*60)
    if result['safe'] is False:
        print("🚫 FINAL VERDICT: DO NOT EAT")
    elif result['safe'] is True:
        print("✅ FINAL VERDICT: SAFE TO EAT")
    else:
        print("⚠️ FINAL VERDICT: UNABLE TO DETERMINE")
    print("="*60)

if __name__ == "__main__":
    main()
