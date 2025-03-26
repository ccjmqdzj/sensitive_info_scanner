# 敏感信息扫描程序架构设计

## 整体架构

程序将采用模块化设计，主要包含以下三个核心模块：

1. **图像处理模块**：负责图像的加载、预处理和文本提取
2. **敏感信息检测模块**：负责对提取的文本进行分析，识别各类敏感信息
3. **用户界面模块**：提供简约的用户交互界面，允许用户选择扫描选项

这三个模块将通过明确的接口进行交互，保证程序的可维护性和可扩展性。

## 模块详细设计

### 1. 图像处理模块 (image_processor.py)

该模块负责处理图像并提取其中的文本内容。

**主要功能**：
- 图像加载：支持多种格式的图像文件（JPG、PNG、BMP等）
- 图像预处理：调整大小、增强对比度、降噪等，提高OCR识别率
- 文本提取：使用Tesseract OCR引擎从图像中提取文本

**主要类和方法**：
```python
class ImageProcessor:
    def __init__(self):
        # 初始化OCR引擎和其他必要组件
        
    def load_image(self, image_path):
        # 加载图像文件
        
    def preprocess_image(self, image):
        # 图像预处理，提高OCR识别率
        
    def extract_text(self, image):
        # 使用OCR从图像中提取文本
        
    def process_image(self, image_path):
        # 整合上述步骤，处理图像并返回提取的文本
```

### 2. 敏感信息检测模块 (sensitive_info_detector.py)

该模块负责分析文本内容，识别其中的敏感信息。

**主要功能**：
- 支持多种敏感信息类型的检测（手机号、家庭住址、身份证号、密码等）
- 允许用户自定义要检测的敏感信息类型
- 提供敏感信息的位置和上下文信息

**主要类和方法**：
```python
class SensitiveInfoDetector:
    def __init__(self):
        # 初始化各类敏感信息的正则表达式模式
        
    def detect_phone_numbers(self, text):
        # 检测文本中的手机号码
        
    def detect_addresses(self, text):
        # 检测文本中的家庭住址
        
    def detect_id_numbers(self, text):
        # 检测文本中的身份证号码
        
    def detect_passwords(self, text):
        # 检测文本中可能的密码信息
        
    def detect_sensitive_info(self, text, info_types):
        # 根据用户选择的信息类型，检测文本中的敏感信息
```

### 3. 用户界面模块 (ui.py)

该模块提供简约的用户界面，允许用户选择文件和敏感信息类型，并展示扫描结果。

**主要功能**：
- 文件选择：允许用户选择单个或多个图像文件
- 敏感信息类型选择：提供复选框让用户选择要检测的敏感信息类型
- 扫描结果展示：以清晰的方式展示检测到的敏感信息

**主要类和方法**：
```python
class SensitiveInfoScannerUI:
    def __init__(self, root):
        # 初始化UI组件
        
    def setup_ui(self):
        # 设置UI布局和组件
        
    def select_files(self):
        # 文件选择功能
        
    def start_scan(self):
        # 开始扫描过程
        
    def display_results(self, results):
        # 展示扫描结果
```

### 4. 主程序 (main.py)

主程序负责整合上述三个模块，协调它们的工作流程。

```python
# 主程序流程
def main():
    # 创建UI实例
    root = tk.Tk()
    app = SensitiveInfoScannerUI(root)
    
    # 创建图像处理器和敏感信息检测器实例
    image_processor = ImageProcessor()
    detector = SensitiveInfoDetector()
    
    # 将处理器和检测器传递给UI
    app.set_processor_and_detector(image_processor, detector)
    
    # 启动UI主循环
    root.mainloop()
```

## 数据流

1. 用户通过UI选择图像文件和要检测的敏感信息类型
2. UI模块将选择的文件传递给图像处理模块
3. 图像处理模块加载并处理图像，提取文本
4. 提取的文本传递给敏感信息检测模块
5. 敏感信息检测模块根据用户选择的类型检测敏感信息
6. 检测结果返回给UI模块
7. UI模块展示检测结果

## 扩展性考虑

- 支持添加新的敏感信息类型
- 支持批量处理多个图像文件
- 支持导出扫描结果
- 支持自定义敏感信息检测规则
