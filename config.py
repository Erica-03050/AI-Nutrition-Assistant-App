import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 火山引擎配置（用于AI对话）
API_KEY = os.getenv('MARSCODE_API_KEY', '78f6d224-ea6d-4ba4-9a30-2fd26e955e90')
MODEL_EP = os.getenv('MARSCODE_MODEL_EP', 'ep-20241122151747-sdctd')

# 百度API配置（用于图像识别）
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY', 'djtoASQlPIUWtbHAHNkxWS5E')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY', 'D9WVeHGO4eKuECBuK5sUiPmf3xo2KaCn')

# 其他配置...
DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "user_profiles.csv")
MEAL_LOG_FILE = os.path.join(DATA_DIR, "meal_logs.csv")
ACTIVITY_LOG_FILE = os.path.join(DATA_DIR, "activity_logs.csv")
WEIGHT_LOG_FILE = os.path.join(DATA_DIR, "weight_logs.csv")
FOOD_DB_FILE = os.path.join(DATA_DIR, "food_database.json")
EXERCISE_DB_FILE = os.path.join(DATA_DIR, "exercise_database.json")

# 创建数据目录
os.makedirs(DATA_DIR, exist_ok=True)

# 游戏化设置
BADGES = {
    "weight_loss": {
        "初级减重者": "减重1kg",
        "中级减重者": "减重3kg",
        "高级减重者": "减重5kg",
        "减重达人": "减重10kg"
    },
    "logging_streak": {
        "坚持一周": "连续记录7天",
        "坚持一月": "连续记录30天",
        "坚持达人": "连续记录100天"
    }
}

# AI反馈模板
FEEDBACK_TEMPLATES = {
    "success": [
        "你太棒了！昨天的目标完成得很好！未来的你一定会感谢现在的努力 💪",
        "看来有人正在成为卡路里控制大师啊！继续保持 🌟",
        "哇！你��仅控制住了食欲，还保持了运动，给你点赞！ 👍"
    ],
    "overeating": [
        "嗯...来今天胃��错？没关系，明天继续加油！ 😊",
        "记录这顿大餐很勇敢！现在让我们想想怎么燃烧它们吧！ 💪",
        "今天吃得多了点，但是诚实记录很重要！明天我们一起继续努力！ 🎯"
    ],
    "missed_logging": [
        "昨天是不是忘记记录啦？你的小零食可都记着呢~ 😉",
        "不记录不要紧，重要的是现在开始！让我们重新开始吧！ 🚀",
        "哎呀，昨天怎么没见到你呢？今天要补回来哦！ 😊"
    ]
} 