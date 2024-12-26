import pandas as pd
import io

class ExcelHandler:
    def __init__(self):
        """初始化Excel处理器"""
        self.required_columns = [
            'Mfg_Year', 'KM', 'HP', 'Doors', 'Weight',
            'Fuel_Type', 'Quarterly_Tax', 'Mfr_Guarantee',
            'BOVAG_Guarantee', 'Guarantee_Period', 'Airco',
            'Automatic_airco', 'Metallic_Rim', 'Tow_Bar'
        ]

    def validate_excel(self, df):
        """验证Excel文件格式"""
        # 检查必需列
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel文件缺少以下必需列: {', '.join(missing_columns)}")
        
        return True

    def create_excel_file(self, df):
        """创建包含预测结果的Excel文件"""
        # 创建一个字节流
        output = io.BytesIO()
        
        # 创建Excel写入器
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 写入预测结果
            df.to_excel(writer, sheet_name='预测结果', index=False)
            
            # 获取工作簿和工作表
            workbook = writer.book
            worksheet = writer.sheets['预测结果']
            
            # 设置列宽
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        # 获取字节流的值
        excel_data = output.getvalue()
        
        return excel_data

    def read_excel_file(self, file):
        """读取Excel文件"""
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 验证文件格式
            self.validate_excel(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"读取Excel文件时出错: {str(e)}") 