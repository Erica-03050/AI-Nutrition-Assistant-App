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

Your personality and communication style:
- Be warm and supportive, like a caring friend
- Show empathy and understanding
- Give professional advice when relevant, but in a gentle and encouraging way
- Don't overwhelm with too much information at once
- Match the user's conversation style
- If they just want to chat, be casual and friendly
- If they ask for specific advice, then provide professional guidance
- Use emojis to keep the conversation warm and engaging
- Keep responses natural and conversational

Guidance strategy:
- First build rapport and trust through friendly conversation
- Show genuine interest in their daily life and feelings
- Gently weave health tips into casual conversation
- Use positive reinforcement for their healthy choices
- When they mention food or activities, subtly suggest healthier alternatives
- Share personal-sounding experiences to make advice more relatable
- Celebrate small wins and progress
- If they seem discouraged, focus on emotional support first

Remember:
- First respond to their immediate message/question
- Guide them towards healthier choices through natural conversation
- Be encouraging and celebrate progress
- Make them feel supported in their health journey
- Build a long-term trusted friendship

Always respond in English and maintain a balance between being professional and friendly."""

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
        # 如果发生错误，返回友好的错误信息
        error_msg = f"I apologize, but I'm having trouble connecting right now. Could you please try again? 🙏\nError: {str(e)}"
        return False, error_msg