import os
import requests
import json
from volcengine.ark import Ark
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
API_KEY = os.getenv('VOLCANO_API_KEY')
MODEL_EP = os.getenv('VOLCANO_MODEL_EP')

# 添加验证
if not all([API_KEY, MODEL_EP]):
    raise ValueError("Missing required API keys in environment variables")

def get_initial_greeting(user_info):
    """Generate initial greeting"""
    greeting = f"""Hello! I'm your AI Nutritionist Assistant! 😊

Based on your personal information, I've created the following plan for you:

Current Weight: {user_info['weight']}kg
Target Weight: {user_info['target_weight']}kg ({abs(user_info['weight'] - user_info['target_weight']):.1f}kg to {"lose" if user_info['weight'] > user_info['target_weight'] else "gain"})
Target Days: {user_info['days_to_target']} days
Recommended Daily Calorie Intake: {user_info['recommended_intake']:.0f} kcal

You can tell me:
1. What you've eaten, and I'll calculate the calories and keep track 🍽️
2. What exercises you've done, and I'll calculate the calories burned 💪
3. Any questions about diet and health

Let's chat about your diet and exercise today!"""
    return greeting

def get_ai_response(messages, user_info):
    """Get AI response"""
    try:
        # Build detailed system prompt
        system_prompt = f"""You are a caring and supportive AI Nutritionist Assistant who talks like a knowledgeable friend. 

User's information:
- Gender: {user_info['gender']}
- Age: {user_info['age']} years
- Height: {user_info['height']}cm
- Current Weight: {user_info['weight']}kg
- Target Weight: {user_info['target_weight']}kg (Need to {user_info['weight_goal_type'].lower()} {abs(user_info['weight'] - user_info['target_weight']):.1f}kg)
- BMI: {user_info['bmi']:.1f}
- Daily Calories Burned: {user_info['daily_calories_burned']:.0f} kcal
- Recommended Daily Intake: {user_info['recommended_intake']:.0f} kcal
- Target Days: {user_info['days_to_target']} days

...（保持原来的 prompt）..."""

        # 使用 Ark SDK 创建客户端
        client = Ark(api_key=API_KEY)
        
        # 构建消息历史
        chat_messages = [{"role": "system", "content": system_prompt}]
        chat_messages.extend([
            {"role": m["role"], "content": m["content"]} 
            for m in messages[-4:]  # 只保留最近4条消息
        ])
        
        # 发送请求
        completion = client.chat.completions.create(
            model=MODEL_EP,
            messages=chat_messages
        )
        
        # 返回响应
        return True, completion.choices[0].message.content

    except Exception as e:
        error_msg = f"I apologize, but I'm having trouble connecting right now. Could you please try again? 🙏\nError: {str(e)}"
        return False, error_msg