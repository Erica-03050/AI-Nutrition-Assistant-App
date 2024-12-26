# AI Nutritionist Assistant 🥗

An AI-powered nutritionist assistant that helps users achieve their healthy eating and weight management goals through personalized guidance and real-time food recognition.

## Features

- 💬 **Smart Chat**: Natural conversations with an AI nutritionist for professional advice
- 📸 **Food Recognition**: Upload food images for automatic nutrition analysis
- 📊 **Health Tracking**: Real-time monitoring of BMI, BMR, and other health metrics
- 🎯 **Personalized Guidance**: Customized dietary recommendations based on your goals

## Core Functions

1. Personal Profile Management
   - Set age, gender, height, and weight
   - Define target weight and timeline
   - Select daily activity level

2. Health Metrics Tracking
   - BMI calculation and classification
   - Basal Metabolic Rate (BMR) computation
   - Daily calorie expenditure estimation
   - Recommended calorie intake calculation

3. AI Nutritionist Chat
   - Intelligent understanding of user needs
   - Professional nutrition advice
   - Answers to diet-related questions

4. Food Recognition
   - Automatic food identification from images
   - Detailed nutritional information
   - Personalized dietary recommendations

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- AI Services: 
  - Volcano Engine AI Chat Service
  - Baidu AI Image Recognition
  - Nutritionix API

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd ai-nutritionist-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file and add the following:
```
# Baidu AI API Keys
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key

# Nutritionix API Keys
NUTRITIONIX_APP_ID=your_nutritionix_app_id
NUTRITIONIX_APP_KEY=your_nutritionix_app_key

# Volcano Engine API Keys
VOLCANO_API_KEY=your_volcano_api_key
VOLCANO_MODEL_EP=your_volcano_model_ep
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage Guide

1. Fill in your personal information in the sidebar
2. Chat with the AI nutritionist through the chat interface
3. Upload food images for nutrition analysis
4. Monitor your health metrics in real-time

## Important Notes

- The advice provided by this application is for reference only and should not replace professional medical advice
- Please provide accurate personal information for better recommendations
- Food recognition requires clear images for accurate results

## License

MIT License