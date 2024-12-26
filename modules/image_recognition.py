import requests
import json
import os
from PIL import Image
import io
import base64
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从环境变量获取API密钥
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')
NUTRITIONIX_APP_ID = os.getenv('NUTRITIONIX_APP_ID')
NUTRITIONIX_APP_KEY = os.getenv('NUTRITIONIX_APP_KEY')

# 添加验证
if not all([BAIDU_API_KEY, BAIDU_SECRET_KEY, NUTRITIONIX_APP_ID, NUTRITIONIX_APP_KEY]):
    raise ValueError("Missing required API keys in environment variables")

def get_access_token():
    """获取百度API的access token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": BAIDU_API_KEY,
        "client_secret": BAIDU_SECRET_KEY
    }
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            logger.error(f"获取access token失败: {response.text}")
            return None
    except Exception as e:
        logger.error(f"获取access token时发生错误: {str(e)}")
        return None

def get_nutrition_info(food_name):
    """从Nutritionix API获取营养信息"""
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_APP_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # 构建查询，添加更多关键词以提高匹配度
        query = f"1 serving of {food_name}"
        data = {
            "query": query,
            "locale": "en_US",  # 使用英文查询以获得更好的结果
            "timezone": "US/Eastern"
        }
        
        logger.debug(f"正在查询营养信息: {query}")
        response = requests.post(url, headers=headers, json=data)
        logger.debug(f"Nutritionix API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.debug(f"Nutritionix API返回结果: {result}")
            
            if 'foods' in result and len(result['foods']) > 0:
                food = result['foods'][0]
                nutrition = {
                    'calories': food.get('nf_calories', 0),
                    'protein': food.get('nf_protein', 0),
                    'carbs': food.get('nf_total_carbohydrate', 0),
                    'fat': food.get('nf_total_fat', 0),
                    'fiber': food.get('nf_dietary_fiber', 0),
                    'serving_weight_grams': food.get('serving_weight_grams', 100),
                    'serving_unit': food.get('serving_unit', 'serving'),
                    'serving_qty': food.get('serving_qty', 1)
                }
                logger.debug(f"获取到营养信息: {nutrition}")
                return nutrition
        
        logger.warning(f"未找到{food_name}的营养信息，使用默认值")
        # 如果API调用失败或没有找到结果，返回估计值
        return {
            'calories': 200,
            'protein': 5,
            'carbs': 25,
            'fat': 8,
            'fiber': 2,
            'serving_weight_grams': 100,
            'serving_unit': 'g',
            'serving_qty': 1
        }
        
    except Exception as e:
        logger.error(f"获取营养信息时发生错误: {str(e)}")
        return None

def process_food_image(image_file):
    """使用百度AI识别食物图片并获取营养信息"""
    try:
        # 获取access token
        access_token = get_access_token()
        if not access_token:
            logger.error("无法获取access token")
            return {
                'success': False,
                'message': 'Failed to get access token'
            }

        # 读取图片并转换为base64
        image_bytes = image_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # 使用组合服务接口
        url = "https://aip.baidubce.com/api/v1/solution/direct/imagerecognition/combination"
        params = {"access_token": access_token}
        headers = {'Content-Type': 'application/json'}
        
        # 组合多个识别服务
        data = {
            "image": base64_image,
            "scenes": [
                "ingredient",     # 果蔬识别
                "dishs",         # 菜品识别
                "advanced_general"  # 通用物体识别
            ]
        }

        logger.debug("正在发送请求到百度API组合服务...")
        response = requests.post(url, params=params, headers=headers, json=data)
        logger.debug(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.debug(f"API返回结果: {result}")
            
            # 按优先级处理识别结果
            food_name = None
            probability = 0
            
            # 1. 先尝试果蔬识别结果
            if 'result' in result and 'ingredient' in result['result']:
                ingredient_result = result['result']['ingredient']
                if ingredient_result.get('result') and len(ingredient_result['result']) > 0:
                    top_result = ingredient_result['result'][0]
                    if top_result['name'] != "非果蔬食材" and float(top_result['score']) > probability:
                        food_name = top_result['name']
                        probability = float(top_result['score'])

            # 2. 再尝试菜品识别结果
            if not food_name and 'result' in result and 'dishs' in result['result']:
                dish_result = result['result']['dishs']
                if 'result' in dish_result and len(dish_result['result']) > 0:
                    top_result = dish_result['result'][0]
                    if float(top_result['probability']) > probability:
                        food_name = top_result['name']
                        probability = float(top_result['probability'])

            # 3. 最后尝试通用识别结果
            if not food_name and 'result' in result and 'advanced_general' in result['result']:
                general_result = result['result']['advanced_general']
                if 'result' in general_result and len(general_result['result']) > 0:
                    for item in general_result['result']:
                        # 只选择食物相关的结果
                        if 'root' in item and item['root'] in ['食物', '商品-食品', '果蔬', '食材']:
                            if float(item['score']) > probability:
                                food_name = item['keyword']
                                probability = float(item['score'])

            if food_name:
                # 获取营养信息
                nutrition_info = get_nutrition_info(food_name)
                
                # 构建返回数据
                food_data = {
                    'food_name': food_name,
                    'has_calorie': True,
                    'probability': probability,
                    'nutrition': nutrition_info
                }
                
                logger.debug(f"识别成功: {food_data}")
                return {
                    'success': True,
                    'foods': [food_data]
                }
            else:
                logger.warning("未检测到食物")
                return {
                    'success': False,
                    'message': 'No food detected in the image'
                }
        else:
            logger.error(f"API请求失败: {response.text}")
            return {
                'success': False,
                'message': f'API request failed with status code: {response.status_code}'
            }

    except Exception as e:
        logger.error(f"处理图片时发生错误: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }