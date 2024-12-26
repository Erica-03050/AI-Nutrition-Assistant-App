import pandas as pd
import numpy as np
import re

class DataProcessor:
    def __init__(self):
        """初始化数据处理器"""
        # 定义特征提取的正则表达式模式
        self.patterns = {
            'Mfg_Year': r'(\d{4})年',
            'KM': r'(\d+)(?:万|k|公里)',
            'HP': r'(\d+)马力',
            'Doors': r'(\d+)门',
            'Weight': r'(\d+)(?:kg|公斤)',
            'Fuel_Type': r'(汽油|柴油)',
        }
        
        # 特征映射
        self.fuel_type_map = {
            '汽油': 'Petrol',
            '柴油': 'Diesel'
        }

    def extract_features_from_text(self, text):
        """从文本中提取车辆特征"""
        features = {}
        
        # 使用正则表达式提取特征
        for feature, pattern in self.patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                
                # 特殊处理
                if feature == 'KM' and '万' in text:
                    value = float(value) * 10000
                elif feature == 'Fuel_Type':
                    value = self.fuel_type_map.get(value, 'Petrol')
                
                features[feature] = value
        
        # 检查是否提取到足够的特征
        required_features = ['Mfg_Year', 'KM', 'HP', 'Doors', 'Weight']
        if not all(feature in features for feature in required_features):
            return None
            
        # 转换数据类型
        features = self._convert_types(features)
        
        return features

    def preprocess_dataframe(self, df):
        """预处理数据框"""
        # 复制数据框
        processed_df = df.copy()
        
        # 处理缺失值
        processed_df = self._handle_missing_values(processed_df)
        
        # 转换数据类型
        processed_df = self._convert_dataframe_types(processed_df)
        
        # 特征工程
        processed_df = self._feature_engineering(processed_df)
        
        return processed_df

    def _convert_types(self, features):
        """转换特征的数据类型"""
        # 数值型特征
        numeric_features = ['Mfg_Year', 'KM', 'HP', 'Doors', 'Weight']
        
        for feature in numeric_features:
            if feature in features:
                features[feature] = float(features[feature])
        
        return features

    def _handle_missing_values(self, df):
        """处理缺失值"""
        # 数值型特征使用中位数填充
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df[col].fillna(df[col].median(), inplace=True)
        
        # 分类特征使用众数填充
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            df[col].fillna(df[col].mode()[0], inplace=True)
        
        return df

    def _convert_dataframe_types(self, df):
        """转换数据框的数据类型"""
        # 定义每列的数据类型
        type_dict = {
            'Mfg_Year': 'int64',
            'KM': 'float64',
            'HP': 'float64',
            'Doors': 'int64',
            'Weight': 'float64',
            'Fuel_Type': 'category'
        }
        
        # 转换数据类型
        for col, dtype in type_dict.items():
            if col in df.columns:
                df[col] = df[col].astype(dtype)
        
        return df

    def _feature_engineering(self, df):
        """特征工程"""
        # 添加车龄特征
        current_year = pd.Timestamp.now().year
        df['Age'] = current_year - df['Mfg_Year']
        
        # 添加每公里价值特征
        if 'Price' in df.columns:
            df['Value_per_km'] = df['Price'] / df['KM']
        
        # 添加功率重量比特征
        df['Power_Weight_Ratio'] = df['HP'] / df['Weight']
        
        return df 