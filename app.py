import os
import sys
from pathlib import Path
import logging
import streamlit as st
from dotenv import load_dotenv

# 必须在任何其他st命令之前设置页面配置
st.set_page_config(
    page_title="AI Nutritionist Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载环境变量
load_dotenv()

# 尝试从不同来源加载环境变量
required_vars = [
    'VOLCANO_API_KEY',
    'VOLCANO_MODEL_EP',
    'BAIDU_API_KEY',
    'BAIDU_SECRET_KEY',
    'NUTRITIONIX_APP_ID',
    'NUTRITIONIX_APP_KEY'
]

# 尝试从 Streamlit secrets 获取环境变量
for var in required_vars:
    if var not in os.environ:  # 如果环境变量还没有设置
        try:
            os.environ[var] = st.secrets[var]
        except:
            st.error(f"Missing {var}. Please set it in Streamlit secrets or .env file")
            st.stop()

# 显示环境变量状态（调试用）
st.write("Environment variables status:")
for var in required_vars:
    value = os.getenv(var)
    st.write(f"{var}: {'✅ Set' if value else '❌ Missing'}")

# 检查环境变量
required_vars = {
    'VOLCANO_API_KEY': os.getenv('VOLCANO_API_KEY'),
    'VOLCANO_MODEL_EP': os.getenv('VOLCANO_MODEL_EP'),
    'BAIDU_API_KEY': os.getenv('BAIDU_API_KEY'),
    'BAIDU_SECRET_KEY': os.getenv('BAIDU_SECRET_KEY'),
    'NUTRITIONIX_APP_ID': os.getenv('NUTRITIONIX_APP_ID'),
    'NUTRITIONIX_APP_KEY': os.getenv('NUTRITIONIX_APP_KEY')
}

# 显示当前环境变量状态（仅供调试）
st.write("Current environment variables status:")
for key, value in required_vars.items():
    st.write(f"{key}: {'✅ Set' if value else '❌ Missing'}")

# 检查是否所有必需的变量都存在
missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.stop()

# 获取项目根目录的绝对路径
ROOT_DIR = Path(__file__).resolve().parent

# 将项目根目录添加到Python路径
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# 其他导入
import pandas as pd
import plotly.express as px
from datetime import datetime
from PIL import Image
import io
import json
from modules.chat import get_ai_response, get_initial_greeting
from modules.image_recognition import process_food_image

# 配置详细的日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def on_value_change():
    """当值发生变化时的回调函数"""
    st.session_state.chat_messages = []

def main():
    logger.debug("正在初始化应用...")
    
    # 检查环境变量
    api_key = os.getenv('VOLCANO_API_KEY')
    model_ep = os.getenv('VOLCANO_MODEL_EP')
    
    if not api_key or not model_ep:
        st.error("未找到必须的API配置。请检查 .env 文件。")
        logger.error(f"API Key: {api_key}, Model EP: {model_ep}")
        return
        
    logger.debug(f"API Key configured: {bool(api_key)}")
    logger.debug(f"Model EP configured: {bool(model_ep)}")
    
    logger.debug("正在初始化应用...")
    logger.debug(f"当前工作目录: {os.getcwd()}")
    logger.debug(f"Python路径: {sys.path}")
    
    try:
        # 修改导入语句
        from modules.chat import get_ai_response
        from modules.image_recognition import process_food_image
        logger.debug("成功导入所需模块")
    except Exception as e:
        logger.error(f"导入模块时出错: {str(e)}")
        st.error(f"初始化时出错: {str(e)}")
        return

    # 初始化session state - 只在第一次运行时设置默认值
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
        # 设置默认值
        st.session_state.update({
            'age': 25,
            'gender': "Female",
            'height': 165.0,
            'weight': 60.0,
            'target_weight': 55.0,
            'days_to_target': 90,
            'activity_level': 2
        })

    # 侧边栏：用户信息和统计
    with st.sidebar:
        st.header("👤 Personal Information")
        
        # 存储修改前的值
        old_values = {
            'age': st.session_state.age,
            'gender': st.session_state.gender,
            'height': st.session_state.height,
            'weight': st.session_state.weight,
            'target_weight': st.session_state.target_weight,
            'days_to_target': st.session_state.days_to_target,
            'activity_level': st.session_state.activity_level
        }
        
        # 用户输入部分
        age = st.number_input("Age", 
                             value=st.session_state.age, 
                             min_value=1, 
                             max_value=120,
                             step=1)
        
        gender = st.selectbox("Gender", 
                             ["Male", "Female"], 
                             index=0 if st.session_state.gender == "Male" else 1)
        
        height = st.number_input("Height (cm)", 
                                value=st.session_state.height, 
                                min_value=50.0, 
                                max_value=250.0,
                                step=0.1)
        
        weight = st.number_input("Current Weight (kg)", 
                                value=st.session_state.weight, 
                                min_value=20.0, 
                                max_value=200.0,
                                step=0.1)
        
        target_weight = st.number_input("Target Weight (kg)", 
                                       value=st.session_state.target_weight, 
                                       min_value=20.0, 
                                       max_value=200.0,
                                       step=0.1)
        
        days_to_target = st.number_input("Target Days", 
                                        value=st.session_state.days_to_target, 
                                        min_value=1, 
                                        max_value=365,
                                        step=1)
        
        activity_level = st.selectbox(
            "Activity Level",
            [1, 2, 3, 4, 5],
            index=st.session_state.activity_level - 1,
            format_func=lambda x: {
                1: "Sedentary",
                2: "Lightly Active",
                3: "Moderately Active",
                4: "Very Active",
                5: "Extremely Active"
            }[x]
        )

        # 检查值是否发生变化
        values_changed = (
            age != old_values['age'] or
            gender != old_values['gender'] or
            height != old_values['height'] or
            weight != old_values['weight'] or
            target_weight != old_values['target_weight'] or
            days_to_target != old_values['days_to_target'] or
            activity_level != old_values['activity_level']
        )

        if values_changed:
            # 更新 session state
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.height = height
            st.session_state.weight = weight
            st.session_state.target_weight = target_weight
            st.session_state.days_to_target = days_to_target
            st.session_state.activity_level = activity_level

            # 重新计算健康指标
            bmi = weight / ((height / 100) ** 2)
            if gender == "Male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            activity_multiplier = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
            daily_calories_burned = bmr * activity_multiplier[activity_level]
            
            weight_diff = weight - target_weight
            if weight_diff > 0:
                daily_deficit = (weight_diff * 7700) / days_to_target
                recommended_daily_intake = max(1200, daily_calories_burned - daily_deficit)
                weight_goal_type = "减重"
            else:
                daily_surplus = (abs(weight_diff) * 7700) / days_to_target
                recommended_daily_intake = daily_calories_burned + daily_surplus
                weight_goal_type = "增重"

            # 清除对话历史并添加新的问候语
            st.session_state.chat_messages = []
            initial_greeting = get_initial_greeting({
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'target_weight': target_weight,
                'bmi': bmi,
                'recommended_intake': recommended_daily_intake,
                'days_to_target': days_to_target
            })
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": initial_greeting
            })
            st.rerun()

        # 计算健康指标
        bmi = weight / ((height / 100) ** 2)
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 24.9:
            bmi_category = "Normal"
        elif 25 <= bmi < 29.9:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        # 计算基础代谢率和每日消耗
        if gender == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity_multiplier = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        daily_calories_burned = bmr * activity_multiplier[activity_level]
        
        # 计算建议摄入热量
        weight_diff = weight - target_weight
        if weight_diff > 0:  # 需要减重
            daily_deficit = (weight_diff * 7700) / days_to_target
            recommended_daily_intake = max(1200, daily_calories_burned - daily_deficit)
            weight_goal_type = "减重"
        else:  # 需要增重
            daily_surplus = (abs(weight_diff) * 7700) / days_to_target
            recommended_daily_intake = daily_calories_burned + daily_surplus
            weight_goal_type = "增重"

        # 健康指标显示
        st.markdown("---")
        st.header("📊 Health Metrics")
        st.metric("BMI", f"{bmi:.1f}", bmi_category)
        st.metric("Basal Metabolic Rate", f"{bmr:.0f} kcal/day")
        st.metric("Daily Calories Burned", f"{daily_calories_burned:.0f} kcal")
        st.metric("Recommended Daily Intake", f"{recommended_daily_intake:.0f} kcal")

    # AI对话部分
    st.header("💬 Chat with AI Nutritionist")
    
    # 如果是新对话，显示欢迎语
    if not st.session_state.chat_messages:
        initial_greeting = get_initial_greeting({
            'gender': st.session_state.gender,  # 现在可以安全使用这些变量了
            'age': st.session_state.age,
            'height': st.session_state.height,
            'weight': st.session_state.weight,
            'target_weight': st.session_state.target_weight,
            'bmi': bmi,
            'recommended_intake': recommended_daily_intake,
            'days_to_target': st.session_state.days_to_target
        })
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": initial_greeting
        })

    # 在AI对话部分修改
    def format_chat_message(message):
        """式化聊天消息去除必的图引用"""
        if message["role"] == "user":
            # 如果是图片上传消息，使用特殊格式
            if "image" in message:
                return None  # 返回None表示不显示这条消息
            return message["content"]
        else:
            return message["content"]

    # 示聊天历史
    for message in st.session_state.chat_messages:
        formatted_message = format_chat_message(message)
        if formatted_message is not None:
            with st.chat_message(message["role"]):
                if "image" in message:
                    st.image(message["image"], caption="上传的物图片")
                st.markdown(formatted_message)

    # 聊天输入
    if prompt := st.chat_input("Chat with your AI nutritionist..."):
        # 先显示用户输入
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 添加用户消息到历史记录
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 使用最新的用户信息
        user_info = {
            'gender': st.session_state.gender,
            'age': st.session_state.age,
            'height': st.session_state.height,
            'weight': st.session_state.weight,
            'target_weight': st.session_state.target_weight,
            'bmi': bmi,
            'recommended_intake': recommended_daily_intake,
            'days_to_target': st.session_state.days_to_target,
            'activity_level': st.session_state.activity_level,
            'daily_calories_burned': daily_calories_burned,
            'weight_goal_type': weight_goal_type
        }
        
        # 获取AI回复
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                # 确保消息历史不会太长
                recent_messages = st.session_state.chat_messages[-5:]  # 只保留最近5条消息
                success, response = get_ai_response(recent_messages, user_info)
                
                if success:
                    # 显示AI回复
                    st.markdown(response)
                    # 添加AI回复到历史记录
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": response
                    })
                else:
                    st.error(f"AI响应错误: {response}")

    # 添加分隔线
    st.markdown("---")

    # 图片上传部分
    st.markdown("""
        <style>
        /* 调整标题大小 */
        .small-header {
            font-size: 1.2rem !important;
            margin-bottom: 0.5rem !important;
        }
        /* 调整说明文字大小 */
        .small-text {
            font-size: 0.9rem !important;
            margin-bottom: 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h2 class="small-header">📸 Upload Food Image</h2>', unsafe_allow_html=True)
    st.markdown('<p class="small-text">Upload a food image, and I\'ll tell you its calories and nutritional information</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        help="Supports PNG, JPG, JPEG formats"
    )

    # 处理图片上传
    if uploaded_file:
        try:
            with st.spinner("Analyzing food image..."):
                result = process_food_image(uploaded_file)
                
                if result['success'] and result['foods']:
                    food = result['foods'][0]
                    
                    # 构建消息让AI来处理
                    prompt = (
                        f"The user has uploaded a food image of '{food['food_name']}'. "
                        "You are their friendly nutrition buddy (not a professional nutritionist). "
                        "Chat with them casually about this food and its nutritional value. "
                        "Always use English names for the food, and never show the Chinese characters in your response. "
                        "Make sure to mention what the food is in your response. "
                    )
                    
                    if food['has_calorie'] and food['nutrition']:
                        nutrition = food['nutrition']
                        prompt += (
                            f"The food contains: "
                            f"calories: {nutrition.get('calories', 0):.0f}kcal, "
                            f"protein: {nutrition.get('protein', 0):.1f}g, "
                            f"carbs: {nutrition.get('carbs', 0):.1f}g, "
                            f"fat: {nutrition.get('fat', 0):.1f}g, "
                            f"fiber: {nutrition.get('fiber', 0):.1f}g. "
                        )
                    
                    prompt += (
                        "If the food name is in Chinese, use only its English name in your response "
                        "without showing the Chinese characters. Start your response by casually mentioning "
                        "what food you see in the image. Give friendly advice about this food "
                        "considering the user's health goals. Keep the tone casual and fun, like chatting with a friend. "
                        "Use emojis to make it engaging!"
                    )
                    
                    # 构建用户信息
                    current_user_info = {
                        'gender': st.session_state.gender,
                        'age': st.session_state.age,
                        'height': st.session_state.height,
                        'weight': st.session_state.weight,
                        'target_weight': st.session_state.target_weight,
                        'bmi': weight / ((height / 100) ** 2),
                        'recommended_intake': recommended_daily_intake,
                        'days_to_target': st.session_state.days_to_target,
                        'activity_level': st.session_state.activity_level,
                        'daily_calories_burned': daily_calories_burned,
                        'weight_goal_type': weight_goal_type
                    }
                    
                    # 构建系统消息
                    image_message = {
                        "role": "system",
                        "content": prompt
                    }
                    
                    # 获取AI回复
                    success, response = get_ai_response([image_message], current_user_info)
                    
                    if success:
                        # 更新消息历史
                        st.session_state.chat_messages.append({
                            "role": "user",
                            "content": "I uploaded a food image",
                            "image": uploaded_file
                        })
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        
                        # 显示当前响应
                        with st.chat_message("assistant"):
                            st.markdown(response)
                    else:
                        st.error(f"AI response error: {response}")
                else:
                    st.error(f"Image recognition failed: {result.get('message', 'Could not identify food')}")
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.rerun()

if __name__ == "__main__":
    main()


