# Google Gemini API Setup

## Get Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Get API Key" or "Create API Key"
4. Copy the API key

## Set Environment Variable

### Temporary (current session only):
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### Permanent (add to ~/.bashrc):
```bash
echo "export GEMINI_API_KEY='your-api-key-here'" >> ~/.bashrc
source ~/.bashrc
```

## Test the Setup

### Test allergy checker directly:
```bash
cd /home/baymini/Baymin/Functions
source /home/baymini/Baymin/venv/bin/activate
export DISPLAY=:0
python AllergyCheck.py /path/to/food/image.jpg
```

### Test with wake word:
```bash
cd /home/baymini/Baymin/Functions
source /home/baymini/Baymin/venv/bin/activate
export DISPLAY=:0
export GEMINI_API_KEY='your-api-key-here'
python Wake.py
```

Then say "alexa" or "hey jarvis" - the system will:
1. Open camera for 5 seconds
2. Take a photo
3. Analyze it with Gemini for allergens
4. Print "DO NOT EAT" or "SAFE TO EAT"

## User Allergy Data

Edit `/home/baymini/Baymin/user_data.json` to add/modify user allergies:

```json
[
    {
        "name": "Person Name",
        "allergies": [
            "Peanuts",
            "Shellfish",
            "Dairy"
        ],
        "conditions": [
            "Diabetes"
        ]
    }
]
```

The system checks ALL users' allergies combined when analyzing food.
