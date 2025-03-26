# 敏感信息扫描程序使用文档

## 简介

敏感信息扫描程序是一个用于自动扫描图片中包含的敏感信息的工具。它能够识别多种类型的敏感信息，包括手机号码、座机号码、身份证号、家庭住址、电子邮箱、密码、银行卡号和IP地址等。程序提供了简约的界面，允许用户自定义选择要扫描的敏感信息类型。

## 功能特点

- **多种敏感信息检测**：支持检测多种类型的敏感信息
- **自定义扫描选项**：用户可以选择要检测的敏感信息类型
- **批量处理**：支持同时处理多个图像文件
- **高精度识别**：采用多种图像预处理技术和上下文验证机制，提高识别准确率
- **简约界面**：提供简洁易用的图形界面和命令行界面
- **结果导出**：支持将扫描结果保存为文本文件

## 系统要求

- Python 3.6 或更高版本
- 操作系统：Windows、macOS 或 Linux
- 依赖库：
  - OpenCV
  - Tesseract OCR
  - pytesseract
  - NumPy
  - Pillow
  - Tkinter (GUI版本)

## 安装指南

### 1. 安装Python

如果您的系统中尚未安装Python，请从[Python官网](https://www.python.org/downloads/)下载并安装Python 3.6或更高版本。

### 2. 安装Tesseract OCR

#### Windows
1. 从[Tesseract官方GitHub页面](https://github.com/UB-Mannheim/tesseract/wiki)下载安装程序
2. 运行安装程序，记住安装路径
3. 将安装路径添加到系统环境变量PATH中

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # 安装语言包
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 安装中文支持
```

### 3. 安装Python依赖库

```bash
pip install opencv-python pytesseract pillow numpy
```

### 4. 下载程序

您可以通过以下方式获取程序：

1. 下载ZIP压缩包并解压
2. 或者使用Git克隆仓库：
   ```bash
   git clone https://github.com/yourusername/sensitive_info_scanner.git
   ```

## 使用方法

### 图形界面版本

1. 运行主程序：
   ```bash
   python main.py
   ```

2. 在程序界面中：
   - 点击"添加文件"或"添加文件夹"按钮选择要扫描的图像
   - 在"敏感信息类型"区域选择要检测的信息类型
   - 点击"开始扫描"按钮开始扫描
   - 扫描结果将显示在右侧区域
   - 可以使用"保存结果"按钮将结果保存为文本文件

### 命令行版本

命令行版本提供了更多的灵活性和自动化可能性。

基本用法：
```bash
python cli_main.py -f <图像文件路径> -t <敏感信息类型> -o <输出文件路径>
```

或者：
```bash
python cli_main.py -d <图像文件夹路径> -t <敏感信息类型> -o <输出文件路径>
```

参数说明：
- `-f, --file`：指定要扫描的图像文件路径
- `-d, --directory`：指定要扫描的图像文件夹路径
- `-t, --types`：指定要检测的敏感信息类型，可选值包括：
  - `phone`：手机号码
  - `landline`：座机号码
  - `id_card`：身份证号
  - `address`：家庭住址
  - `email`：电子邮箱
  - `password`：密码
  - `credit_card`：银行卡号
  - `ip_address`：IP地址
  - `all`：所有类型（默认）
- `-o, --output`：指定结果输出文件路径
- `-v, --verbose`：显示详细信息

示例：
```bash
# 扫描单个文件，检测所有类型的敏感信息
python cli_main.py -f image.jpg

# 扫描文件夹中的所有图像，仅检测手机号和身份证号
python cli_main.py -d images_folder -t phone id_card

# 扫描文件，将结果保存到文件
python cli_main.py -f image.jpg -o results.txt -v
```

## 程序结构

程序由以下几个主要模块组成：

1. **图像处理模块** (image_processor.py)：
   - 负责图像的加载、预处理和文本提取
   - 使用OpenCV和Tesseract OCR进行图像处理和文本识别

2. **敏感信息检测模块** (sensitive_info_detector.py)：
   - 负责分析文本内容，识别其中的敏感信息
   - 使用正则表达式和上下文验证机制进行敏感信息检测

3. **用户界面模块** (ui.py)：
   - 提供图形用户界面，允许用户选择文件和敏感信息类型
   - 展示扫描结果

4. **命令行界面** (cli_main.py)：
   - 提供命令行接口，支持批量处理和自动化

5. **主程序** (main.py)：
   - 整合上述模块，提供完整的程序功能

## 常见问题

### Q: 程序无法识别图像中的文本
A: 请确保：
   - 图像清晰，文本可读
   - 已正确安装Tesseract OCR
   - 如果是非英文文本，已安装相应的语言包

### Q: 图形界面无法启动
A: 请确保：
   - 已安装Tkinter库
   - 在有图形界面支持的环境中运行程序
   - 如果在远程服务器上，可以使用命令行版本

### Q: 如何提高识别准确率？
A: 可以尝试：
   - 使用更清晰的图像
   - 调整图像对比度和亮度
   - 在敏感信息检测模块中调整置信度阈值

## 隐私声明

本程序在本地处理所有图像和文本数据，不会将任何数据上传到外部服务器。扫描结果仅保存在用户指定的位置，用户对自己的数据拥有完全控制权。

## 许可证

本程序采用MIT许可证。详情请参阅LICENSE文件。

## 联系方式

如有任何问题或建议，请联系：

- 电子邮箱：your.email@example.com
- GitHub：https://github.com/yourusername/sensitive_info_scanner
