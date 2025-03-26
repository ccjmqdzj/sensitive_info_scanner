# Sensitive Info Scanner

<p align="center">
  <img src="https://raw.githubusercontent.com/ccjmqdzj/sensitive_info_scanner/refs/heads/main/image.png" alt="Sensitive Info Scanner Logo" width="200"/>
</p>

<p align="center">
  <a href="#简介">简介</a> •
  <a href="#功能特点">功能特点</a> •
  <a href="#安装指南">安装指南</a> •
  <a href="#使用方法">使用方法</a> •
  <a href="#技术实现">技术实现</a> •
  <a href="#隐私声明">隐私声明</a> •
  <a href="#贡献指南">贡献指南</a> •
  <a href="#许可证">许可证</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/yourusername/sensitive_info_scanner" alt="License"/>
  <img src="https://img.shields.io/github/stars/yourusername/sensitive_info_scanner" alt="Stars"/>
  <img src="https://img.shields.io/github/forks/yourusername/sensitive_info_scanner" alt="Forks"/>
  <img src="https://img.shields.io/github/issues/yourusername/sensitive_info_scanner" alt="Issues"/>
</p>

## 简介

Sensitive Info Scanner 是一个强大的开源工具，专为自动扫描图片中的敏感信息而设计。在当今信息爆炸的时代，我们经常在不经意间分享包含敏感信息的图片，如身份证照片、银行卡信息、个人地址等，这些都可能导致隐私泄露和安全风险。

本工具利用先进的图像处理和文本识别技术，能够自动检测图片中的多种敏感信息，帮助用户在分享图片前识别并处理这些潜在风险，保护个人隐私和数据安全。

## 功能特点

### 多种敏感信息检测
- **手机号码**：识别中国大陆手机号码，支持可选的+86前缀
- **座机号码**：识别固定电话号码，包括区号
- **身份证号**：识别18位身份证号码，并验证其有效性
- **家庭住址**：识别包含省市区县、路街道等信息的地址
- **电子邮箱**：识别标准电子邮箱格式
- **密码信息**：识别可能的密码字段
- **银行卡号**：识别16-19位银行卡号，并使用Luhn算法验证
- **IP地址**：识别标准IPv4地址格式

### 高级图像处理
- **多格式支持**：支持JPG、PNG、BMP、TIFF等多种图像格式
- **智能预处理**：自动应用灰度转换、二值化、降噪和倾斜校正等技术
- **高精度OCR**：集成Tesseract OCR引擎，支持中英文识别

### 用户友好界面
- **图形界面**：提供简洁直观的图形用户界面
- **命令行界面**：支持命令行操作，便于批处理和自动化
- **自定义选项**：用户可选择要检测的敏感信息类型
- **批量处理**：支持同时处理多个图像文件
- **结果导出**：支持将扫描结果保存为文本文件

### 安全与隐私
- **本地处理**：所有图像和文本数据在本地处理，不会上传到外部服务器
- **上下文验证**：使用上下文验证机制减少误报
- **置信度评分**：为检测结果提供置信度评分，帮助用户判断

## 安装指南

### 系统要求
- Python 3.6 或更高版本
- 操作系统：Windows、macOS 或 Linux

### 步骤1：安装Python
如果您的系统中尚未安装Python，请从[Python官网](https://www.python.org/downloads/)下载并安装Python 3.6或更高版本。

### 步骤2：安装Tesseract OCR

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

### 步骤3：安装Sensitive Info Scanner

#### 方法1：使用pip安装
```bash
pip install sensitive-info-scanner
```

#### 方法2：从源代码安装
```bash
# 克隆仓库
git clone https://github.com/yourusername/sensitive_info_scanner.git
cd sensitive_info_scanner

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 图形界面版本

1. 启动程序：
   ```bash
   python -m sensitive_info_scanner
   ```
   或者如果您使用pip安装：
   ```bash
   sensitive-info-scanner
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
sensitive-info-scanner -f <图像文件路径> -t <敏感信息类型> -o <输出文件路径>
```

或者：
```bash
sensitive-info-scanner -d <图像文件夹路径> -t <敏感信息类型> -o <输出文件路径>
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
sensitive-info-scanner -f image.jpg

# 扫描文件夹中的所有图像，仅检测手机号和身份证号
sensitive-info-scanner -d images_folder -t phone id_card

# 扫描文件，将结果保存到文件
sensitive-info-scanner -f image.jpg -o results.txt -v
```

## 技术实现

Sensitive Info Scanner 采用模块化设计，主要包含以下三个核心模块：

### 1. 图像处理模块 (image_processor.py)
- 负责图像的加载、预处理和文本提取
- 使用OpenCV进行图像处理，包括灰度转换、二值化、降噪和倾斜校正
- 集成Tesseract OCR引擎进行文本识别，支持中英文

### 2. 敏感信息检测模块 (sensitive_info_detector.py)
- 负责分析文本内容，识别其中的敏感信息
- 使用精确的正则表达式匹配各类敏感信息
- 实现上下文验证机制，减少误报
- 为检测结果提供置信度评分

### 3. 用户界面模块 (ui.py)
- 提供图形用户界面，基于Tkinter实现
- 允许用户选择文件和敏感信息类型
- 展示扫描结果，支持结果导出

## 应用场景

- **个人隐私保护**：在分享照片前检查是否包含敏感信息
- **企业数据安全**：帮助企业检查文档图像中的敏感信息，防止数据泄露
- **开发者工具**：集成到图像处理流程中，自动化敏感信息检测
- **教育与培训**：提高用户对信息安全的意识

## 隐私声明

本程序在本地处理所有图像和文本数据，不会将任何数据上传到外部服务器。扫描结果仅保存在用户指定的位置，用户对自己的数据拥有完全控制权。

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 报告问题和提出建议
- 提交代码改进和新功能
- 改进文档和示例
- 添加新的敏感信息类型支持

如果您想贡献代码，请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

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

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目维护者：Your Name
- 电子邮箱：your.email@example.com
- GitHub：https://github.com/yourusername/sensitive_info_scanner

---

<p align="center">
  如果您觉得这个项目有用，请给它一个星标 ⭐️
</p>
