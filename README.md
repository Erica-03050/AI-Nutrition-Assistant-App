# AI Nutritionist Assistant 🥗

这是一个基于AI的智能营养师助手应用，可以帮助用户实现健康饮食和体重管理目标。

## 功能特点

- 💬 智能对话：与AI营养师进行自然对话，获取专业建议
- 📸 食物识别：上传食物图片自动识别营养成分
- 📊 健康追踪：实时监控BMI、基础代谢率等健康指标
- 🎯 个性化建议：根据用户目标提供定制化的饮食建议

## 主要功能

1. 个人信息管理
   - 设置年龄、性别、身高、体重等基本信息
   - 设定目标体重和期望达成时间
   - 选择日常活动水平

2. 健康指标追踪
   - BMI计算和分类
   - 基础代谢率(BMR)计算
   - 每日消耗热量估算
   - 推荐摄入热量计算

3. AI营养师对话
   - 智能理解用户需求
   - 提供专业营养建议
   - 回答健康饮食相关问题

4. 食物识别
   - 上传食物图片自动识别
   - 获取营养成分信息
   - 提供相关饮食建议

## 技术栈

- Frontend: Streamlit
- Backend: Python
- AI Services: 
  - 火山引擎 AI 对话服务
  - 百度 AI 图像识别
  - Nutritionix API

## 安装说明

1. 克隆项目：
```bash
git clone [your-repository-url]
cd ai-nutritionist-assistant
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 .env 文件并添加以下配置：
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

请确保替换上述配置中的占位符为实际的API密钥。

4. 运行应用：
```bash
streamlit run app.py
```

## 使用说明

1. 首次使用时，在侧边栏填写个人信息
2. 通过聊天框与AI营养师对话
3. 可以上传食物图片获取营养信息
4. 查看健康指标了解身体状况

## 注意事项

- 本应用提供的建议仅供参考，不能替代专业医生的意见
- 请确保提供真实的个人信息以获得更准确的建议
- 图片识别功能需要清晰的食物图片才能准确识别

## License

MIT License