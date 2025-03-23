import os
import re
import folder_paths
import csv
import codecs
import json
import shutil
from server import PromptServer

# 将上传处理函数注册到PromptServer的API系统
try:
    server = PromptServer.instance
    @server.routes.post("/upload/upload_csv_file")
    async def upload_csv_file_handler(request):
        try:
            data = await request.post()
            file = data.get('file')
            if not file or not file.filename:
                return server.create_error_response("没有找到上传的文件")

            # 保存文件
            target_dir = os.path.join(folder_paths.base_path, "csv_styles")
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            file_name = file.filename
            target_path = os.path.join(target_dir, file_name)
            
            # 保存上传的文件
            with open(target_path, 'wb') as f:
                while True:
                    chunk = await file.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)
            
            print(f"成功上传CSV文件: {file_name}")
            return {"ui": {"text": [f"成功上传CSV文件: {file_name}"]}}
        except Exception as e:
            print(f"上传CSV文件时出错: {e}")
            return server.create_error_response(f"上传失败: {str(e)}")
    
    print("成功注册CSV文件上传处理程序")
except Exception as e:
    print(f"注册CSV文件上传处理程序时出错: {e}")
    
# 添加用户选择上传文件的JavaScript代码
WEB_DIRECTORY = "./js"
class UploadCSVButton:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
        }
    
    FUNCTION = "execute"
    CATEGORY = "loaders"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    
    def execute(self):
        return {}
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True
    


class StylesCSVLoader:
    """
    Loads csv file with styles. For migration purposes from automatic11111 webui.
    """
    
    @staticmethod
    def load_styles_csv(styles_path: str):
        """Loads csv file with styles. It has only one column.
        Ignore the first row (header).
        positive_prompt are strings separated by comma. Each string is a prompt.
        negative_prompt are strings separated by comma. Each string is a prompt.

        Returns:
            list: List of styles. Each style is a dict with keys: style_name and value: [positive_prompt, negative_prompt]
        """
        styles = {"Error loading styles.csv, check the console": ["",""]}
        if not os.path.exists(styles_path):
            print(f"""Error. No styles.csv found at path: {styles_path}. Select a valid CSV file.
                  Your current root directory is: {folder_paths.base_path}
            """)
            return styles
        
        try:
            # 尝试不同编码方式读取文件
            encodings = ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030", "big5"]
            loaded = False
            
            for encoding in encodings:
                try:
                    # 使用csv模块解析，这样可以更好地处理引号和逗号的问题
                    with open(styles_path, "r", encoding=encoding, newline='') as f:
                        reader = csv.reader(f)
                        rows = list(reader)
                        if len(rows) <= 1:  # 只有标题行或空文件
                            continue
                            
                        # 跳过标题行，处理剩余行
                        data = rows[1:]
                        styles_dict = {}
                        
                        for row in data:
                            if len(row) >= 3:  # 确保行至少有3列
                                style_name = row[0].strip()
                                positive = row[1].strip()
                                negative = row[2].strip() if len(row) > 2 else ""
                                styles_dict[style_name] = [positive, negative]
                        
                        # 只有当成功解析至少一个样式时才更新styles
                        if styles_dict:
                            styles = styles_dict
                            loaded = True
                            print(f"Successfully loaded CSV file using {encoding} encoding. Found {len(styles)} styles.")
                            break
                
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error with {encoding} encoding: {e}")
                    continue
            
            # 如果所有编码都失败，尝试使用二进制模式读取并强制解码
            if not loaded:
                try:
                    with open(styles_path, 'rb') as f:
                        content = f.read()
                        # 尝试检测BOM头
                        if content.startswith(codecs.BOM_UTF8):
                            content = content[len(codecs.BOM_UTF8):]
                            encoding = 'utf-8'
                        elif content.startswith(codecs.BOM_UTF16_LE):
                            content = content[len(codecs.BOM_UTF16_LE):]
                            encoding = 'utf-16-le'
                        elif content.startswith(codecs.BOM_UTF16_BE):
                            content = content[len(codecs.BOM_UTF16_BE):]
                            encoding = 'utf-16-be'
                        else:
                            # 没有BOM头，尝试用替换模式解码
                            encoding = 'utf-8'
                        
                        text = content.decode(encoding, errors='replace')
                        
                        # 使用字符串处理CSV内容
                        lines = text.splitlines()
                        if len(lines) <= 1:  # 只有标题行或空文件
                            raise Exception("File has no data rows")
                            
                        # 解析CSV内容
                        styles_dict = {}
                        for line in lines[1:]:  # 跳过标题行
                            # 处理CSV行，考虑引号内的逗号
                            parts = re.split(',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
                            if len(parts) >= 3:
                                style_name = parts[0].replace('"', '').strip()
                                positive = parts[1].replace('"', '').strip()
                                negative = parts[2].replace('"', '').strip() if len(parts) > 2 else ""
                                styles_dict[style_name] = [positive, negative]
                        
                        if styles_dict:
                            styles = styles_dict
                            print(f"Successfully loaded CSV file using binary mode and {encoding} decoding. Found {len(styles)} styles.")
                            loaded = True
                
                except Exception as e:
                    print(f"Error in binary mode: {e}")
            
            # 如果所有尝试都失败
            if not loaded:
                print(f"""Error loading CSV file. Failed to decode with all attempted encodings.
                      Make sure it is a valid CSV file with the required columns.
                      Your current root directory is: {folder_paths.base_path}
                """)
                
        except Exception as e:
            print(f"""Error loading CSV file. 
                    Your current root directory is: {folder_paths.base_path}
                    Error: {e}
            """)
            
        return styles
    
    # 添加CSV文件路径获取函数
    @staticmethod
    def find_csv_files():
        # 获取基本路径
        base_path = folder_paths.base_path
        # 获取当前节点的路径
        node_path = os.path.dirname(os.path.abspath(__file__))
        
        csv_paths = {}
        
        # 首先添加默认的styles.csv
        default_csv = os.path.join(base_path, "styles.csv")
        if os.path.exists(default_csv):
            csv_paths["styles.csv (默认)"] = default_csv
        
        # 检查自定义CSV存储目录
        csv_dir = os.path.join(base_path, "csv_styles")
        if os.path.exists(csv_dir):
            for file in os.listdir(csv_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(csv_dir, file)
                    csv_paths[f"csv_styles/{file}"] = file_path
        
        # 添加自定义节点目录下的CSV文件
        custom_nodes_path = os.path.join(base_path, "custom_nodes")
        if os.path.exists(custom_nodes_path):
            for root, dirs, files in os.walk(custom_nodes_path):
                for file in files:
                    if file.endswith('.csv'):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, base_path)
                        csv_paths[relative_path] = file_path
        
        # 如果没有找到任何CSV文件，添加一个默认选项
        if not csv_paths:
            csv_paths["未找到CSV文件"] = ""
        
        return csv_paths
        
    @classmethod
    def INPUT_TYPES(cls):
        # 找到所有可用的CSV文件
        cls.csv_files = cls.find_csv_files()
        csv_file_names = list(cls.csv_files.keys())
        
        # 默认使用第一个CSV文件
        default_csv = csv_file_names[0] if csv_file_names else ""
        cls.current_csv_path = cls.csv_files.get(default_csv, "")
        
        # 加载样式数据
        cls.styles_csv = cls.load_styles_csv(cls.current_csv_path)
        
        return {
            "required": {
                "csv_file": (csv_file_names, {"default": default_csv}),
                "refresh": ("BOOLEAN", {"default": False, "label_on": "刷新", "label_off": "刷新"}),
                "styles": (list(cls.styles_csv.keys()),),
            }
        }
    
    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("positive prompt", "negative prompt")
    FUNCTION = "execute"
    CATEGORY = "loaders"   

    def execute(self, csv_file, refresh, styles):
        # 如果选择了新的CSV文件或者请求刷新
        if csv_file in self.csv_files and (self.current_csv_path != self.csv_files[csv_file] or refresh):
            self.current_csv_path = self.csv_files[csv_file]
            self.styles_csv = self.load_styles_csv(self.current_csv_path)
            # 如果styles不在新加载的styles_csv中，返回空字符串
            if styles not in self.styles_csv:
                return ("", "")
        
        return (self.styles_csv[styles][0], self.styles_csv[styles][1])


class MultiStylesCSVLoader:
    """
    加载多个风格并合并提示词
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 找到所有可用的CSV文件
        cls.csv_files = StylesCSVLoader.find_csv_files()
        csv_file_names = list(cls.csv_files.keys())
        
        # 默认使用第一个CSV文件
        default_csv = csv_file_names[0] if csv_file_names else ""
        cls.current_csv_path = cls.csv_files.get(default_csv, "")
        
        # 加载样式数据
        cls.styles_csv = StylesCSVLoader.load_styles_csv(cls.current_csv_path)
        styles_list = list(cls.styles_csv.keys())
        
        # 添加"无"选项到风格列表
        styles_list_with_none = ["无"] + styles_list
        
        return {
            "required": {
                "csv_file": (csv_file_names, {"default": default_csv}),
                "refresh": ("BOOLEAN", {"default": False, "label_on": "刷新", "label_off": "刷新"}),
                "style1": (styles_list,),
                "style2": (styles_list_with_none, {"default": "无"}),
                "style3": (styles_list_with_none, {"default": "无"}),
                "style4": (styles_list_with_none, {"default": "无"}),
                "style5": (styles_list_with_none, {"default": "无"}),
            },
            "optional": {
                "positive_prefix": ("STRING", {"default": "", "multiline": True}),
                "positive_suffix": ("STRING", {"default": "", "multiline": True}),
                "negative_prefix": ("STRING", {"default": "", "multiline": True}),
                "negative_suffix": ("STRING", {"default": "", "multiline": True}),
                "separator": (["逗号", "空格", "换行"], {"default": "逗号"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("combined positive", "combined negative")
    FUNCTION = "execute"
    CATEGORY = "loaders"   

    def execute(self, csv_file, refresh, style1, style2="无", style3="无", style4="无", style5="无", 
               positive_prefix="", positive_suffix="", negative_prefix="", negative_suffix="", 
               separator="逗号"):
        # 如果选择了新的CSV文件或者请求刷新
        if csv_file in self.csv_files and (self.current_csv_path != self.csv_files[csv_file] or refresh):
            self.current_csv_path = self.csv_files[csv_file]
            self.styles_csv = StylesCSVLoader.load_styles_csv(self.current_csv_path)
        
        # 收集所有选择的有效风格
        selected_styles = [style1]
        if style2 != "无" and style2 in self.styles_csv:
            selected_styles.append(style2)
        if style3 != "无" and style3 in self.styles_csv:
            selected_styles.append(style3)
        if style4 != "无" and style4 in self.styles_csv:
            selected_styles.append(style4)
        if style5 != "无" and style5 in self.styles_csv:
            selected_styles.append(style5)
        
        # 获取所有正向和负向提示词
        positive_prompts = []
        negative_prompts = []
        
        for style in selected_styles:
            if style in self.styles_csv:
                pos, neg = self.styles_csv[style]
                
                if pos and pos.strip():
                    pos = pos.strip()
                    positive_prompts.append(pos)
                if neg and neg.strip():
                    negative_prompts.append(neg.strip())
        
        # 设置分隔符
        sep = ", "
        if separator == "空格":
            sep = " "
        elif separator == "换行":
            sep = "\n"
        
        # 合并提示词
        combined_positive = positive_prefix
        if positive_prompts:
            if combined_positive and combined_positive[-1] not in [" ", "\n", ",", "，"]:
                combined_positive += " "
            combined_positive += sep.join(positive_prompts)
        if positive_suffix:
            if combined_positive and combined_positive[-1] not in [" ", "\n", ",", "，"]:
                combined_positive += " "
            combined_positive += positive_suffix
        
        combined_negative = negative_prefix
        if negative_prompts:
            if combined_negative and combined_negative[-1] not in [" ", "\n", ",", "，"]:
                combined_negative += " "
            combined_negative += sep.join(negative_prompts)
        if negative_suffix:
            if combined_negative and combined_negative[-1] not in [" ", "\n", ",", "，"]:
                combined_negative += " "
            combined_negative += negative_suffix
        
        return (combined_positive, combined_negative)


class StylesPreview:
    """
    预览选择的风格内容
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 找到所有可用的CSV文件
        cls.csv_files = StylesCSVLoader.find_csv_files()
        csv_file_names = list(cls.csv_files.keys())
        
        # 默认使用第一个CSV文件
        default_csv = csv_file_names[0] if csv_file_names else ""
        cls.current_csv_path = cls.csv_files.get(default_csv, "")
        
        # 加载样式数据
        cls.styles_csv = StylesCSVLoader.load_styles_csv(cls.current_csv_path)
        styles_list = list(cls.styles_csv.keys())
        
        return {
            "required": {
                "csv_file": (csv_file_names, {"default": default_csv}),
                "refresh": ("BOOLEAN", {"default": False, "label_on": "刷新", "label_off": "刷新"}),
                "style": (styles_list,),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive prompt", "negative prompt")
    FUNCTION = "execute"
    CATEGORY = "loaders"   

    def execute(self, csv_file, refresh, style):
        # 如果选择了新的CSV文件或者请求刷新
        if csv_file in self.csv_files and (self.current_csv_path != self.csv_files[csv_file] or refresh):
            self.current_csv_path = self.csv_files[csv_file]
            self.styles_csv = StylesCSVLoader.load_styles_csv(self.current_csv_path)
        
        if style in self.styles_csv:
            positive, negative = self.styles_csv[style]
            return (positive, negative)
        return ("", "")


NODE_CLASS_MAPPINGS = {
    "Load Styles CSV": StylesCSVLoader,
    "Multi Styles CSV": MultiStylesCSVLoader,
    "Styles Preview": StylesPreview
}
# 节点显示名称已移至__init__.py文件中
# NODE_DISPLAY_NAME_MAPPINGS = {
#     "StylesCSVLoader": "Load Styles CSV Node"
# }
