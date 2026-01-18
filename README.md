# (●—●) Baymini
> **Your Personal AI Healthcare Companion.**
> *Built for nwHacks 2026*

**Baymini** is an autonomous IoT healthcare agent designed to protect users from severe allergic reactions and medication conflicts. By integrating a seamless web dashboard with a headless Raspberry Pi unit, Baymini acts as a second pair of eyes—scanning products, analyzing ingredients using **Gemini Vision AI**, and speaking safety warnings in real-time.

---

## ✨ Features

* **👁️ AI Vision Analysis:** Uses **Gemini 2.5 Flash** to visually analyze product packaging and ingredient labels in milliseconds.
* **🗣️ Voice Interface:** Provides immediate, spoken feedback using **Google Text-to-Speech (TTS)**, acting as a caring companion.
* **☁️ Instant Sync:** A modern Flask dashboard allows users to update allergies/meds, which are "beamed" instantly to the headless Pi unit via SCP.
* **🛡️ Personalized Care:** Logic is dynamically updated based on the specific user profile (e.g., specific allergies to Peanuts or conflicts with Insulin).

---

## 🛠️ Tech Stack

### **Hardware**
* Raspberry Pi 4 (Headless Mode)
* USB Webcam
* Speaker / Audio Output

### **Software & AI**
* **AI Model:** Google Gemini 2.5 Flash (via Google Generative AI SDK)
* **Computer Vision:** OpenCV (`cv2`)
* **Backend:** Python Flask
* **Voice:** Google Text-to-Speech (`gTTS`)
* **Networking:** SSH & SCP for local data synchronization

---

## 🚀 Getting Started

This project consists of two parts: the **Web Dashboard** (run on your laptop) and the **Robot Client** (run on the Raspberry Pi).

### Prerequisites
* Python 3.11
* A Raspberry Pi with SSH enabled.
* A Google Gemini API Key.


## 🧠 How It Works

1.  **User Input:** The user logs into the Web Dashboard and updates their profile (e.g., "Allergy: Peanuts").
2.  **Sync:** The Dashboard generates a JSON profile and uses `scp` to securely transfer it to the Raspberry Pi over the local network.
3.  **Scan:** The user holds a product in front of the Pi and triggers a scan.
4.  **Analyze:** The Pi captures an image and sends it + the JSON profile to **Gemini 2.0 Flash**.
5.  **Reasoning:** The AI reads the ingredients list, checks against the specific user constraints, and generates a response.
6.  **Response:** The Pi speaks the result aloud (e.g., *"Warning: This product contains peanuts."*).
