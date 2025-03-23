# ComfyUI Styles CSV Loader

这个扩展允许用户从CSV文件加载风格预设。

## 特点

- 加载风格CSV文件并在ComfyUI中使用
- 支持多风格合并
- 支持风格预览
- 支持自动将中文提示词转换为英文（免费，无需API密钥）

## 安装

1. 将此存储库克隆到ComfyUI的`custom_nodes`文件夹中
2. 重启ComfyUI

## 使用方法

1. 在ComfyUI中添加以下节点之一：
   - `Load Styles CSV` (加载风格CSV文件)
   - `Multi Styles CSV` (多风格合并节点)
   - `Styles Preview` (风格预览)

2. 在节点中选择您的CSV文件并选择所需的风格预设

3. 多风格合并节点中的中文自动翻译功能：
   - 在`positive_prefix`、`positive_suffix`、`negative_prefix`或`negative_suffix`字段中输入中文文本
   - 确保`auto_translate`选项设置为"自动翻译"（默认开启）
   - 系统将自动将中文翻译为英文，并与选择的风格预设合并

## 依赖

- 基本依赖: `requests`库用于网络请求：`pip install requests`
- 翻译功能依赖（可选，安装任意一个即可获得更好的翻译效果）:
  - `googletrans`库: `pip install googletrans==4.0.0-rc1`
  - `deep-translator`库: `pip install deep-translator`

## 翻译功能说明

该扩展使用三层翻译方案，按照以下优先级尝试：

1. 首先尝试使用`googletrans`库进行翻译（免费，无需API密钥）
2. 如果未安装`googletrans`，则尝试使用`deep-translator`库（免费，无需API密钥）
3. 如果两个翻译库都未安装，则使用内置的中英文词典映射表进行简单翻译

**注意**: 为获得最佳翻译效果，建议安装`googletrans`或`deep-translator`库。内置词典映射只能翻译一些常用词汇，对于复杂句子的翻译效果有限。

## 许可证

MIT
