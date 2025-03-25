from .styles_csv_loader import *
import os

WEB_DIRECTORY = "./web"

# 添加中文节点显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "Load Styles CSV": "加载风格CSV文件",
    "Multi Styles CSV": "多风格合并节点",
    "Preview Text": "预览文本节点"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]