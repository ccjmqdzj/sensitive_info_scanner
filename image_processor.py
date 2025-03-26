#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图像处理模块 (image_processor.py)
该模块负责图像的加载、预处理和OCR文本提取。
"""

import os
import numpy as np
from PIL import Image
import pytesseract
import cv2
import gc
import platform

# 根据操作系统设置Tesseract路径
#if platform.system() == 'Windows':
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux和macOS通常将tesseract添加到PATH中，无需设置

class ImageProcessor:
    """
    图像处理类，负责图像的加载、预处理和OCR文本提取
    """
    
    def __init__(self):
        """
        初始化图像处理器
        """
        # 支持的图像格式
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        
        # OCR语言设置（默认使用英文和简体中文）
        self.ocr_lang = 'eng+chi_sim'
        
        # 图像预处理参数
        self.preprocessing_methods = {
            'none': self._no_preprocessing,
            'grayscale': self._grayscale,
            'binarization': self._binarization,
            'noise_removal': self._noise_removal,
            'deskew': self._deskew
        }
        
        # 默认使用的预处理方法
        self.default_preprocessing = ['grayscale', 'binarization']
        
        # 性能优化参数
        self.max_image_dimension = 1800  # 最大图像尺寸，超过此尺寸将被缩放
    
    def load_image(self, image_path):
        """
        加载图像文件
        
        参数:
            image_path (str): 图像文件路径
            
        返回:
            numpy.ndarray: 加载的图像
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        # 检查文件格式是否支持
        _, ext = os.path.splitext(image_path.lower())
        if ext not in self.supported_formats:
            raise ValueError(f"不支持的图像格式: {ext}，支持的格式有: {', '.join(self.supported_formats)}")
        
        try:
            # 使用PIL/Pillow加载图像
            pil_image = Image.open(image_path)
            
            # 检查图像是否有效
            pil_image.verify()  # 添加这行以验证图像是否有效
            
            # 重新打开图像（verify后需要重新打开）
            pil_image = Image.open(image_path)
            
            # 转换为NumPy数组（OpenCV格式）
            image = np.array(pil_image)
            
            # 如果图像是RGB格式，转换为BGR（OpenCV使用BGR）
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
            return image
        except Exception as e:
            raise IOError(f"无法加载图像: {image_path}, 错误: {str(e)}")
    
    def _preprocess_for_ocr(self, image):
        """为OCR优化图像大小和格式"""
        # 处理图像通道问题
        if len(image.shape) == 2:
            # 单通道图像（灰度），转换为3通道
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # 4通道图像（RGBA），转换为3通道
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        elif len(image.shape) == 3 and image.shape[2] == 2:
            # 2通道图像，转换为3通道
            # 创建一个3通道图像
            height, width = image.shape[:2]
            bgr_image = np.zeros((height, width, 3), dtype=np.uint8)
            # 复制前两个通道到BGR图像
            bgr_image[:, :, 0] = image[:, :, 0]
            bgr_image[:, :, 1] = image[:, :, 1]
            image = bgr_image
        
        # 缩放大图像以提高处理速度
        h, w = image.shape[:2]
        if max(h, w) > self.max_image_dimension:
            scale = self.max_image_dimension / max(h, w)
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        
        return image
    
    def process_image(self, image_path, preprocessing_methods=None):
        """
        处理图像并提取文本
        
        参数:
            image_path (str): 图像文件路径
            preprocessing_methods (list, optional): 要应用的预处理方法列表
            
        返回:
            str: 提取的文本
        """
        try:
            # 加载图像
            image = self.load_image(image_path)
            
            # 为OCR优化图像大小
            image = self._preprocess_for_ocr(image)
            
            # 如果未指定预处理方法，则使用默认方法
            if preprocessing_methods is None:
                preprocessing_methods = self.default_preprocessing
            
            # 应用预处理方法
            for method in preprocessing_methods:
                if method in self.preprocessing_methods:
                    image = self.preprocessing_methods[method](image)
            
            # 使用OCR提取文本
            text = self._extract_text(image)
            
            # 主动释放内存
            del image
            gc.collect()
            
            return text
        except Exception as e:
            raise Exception(f"处理图像时出错: {str(e)}")
    
    def _no_preprocessing(self, image):
        """不进行预处理，直接返回原始图像"""
        return image
    
    def _grayscale(self, image):
        """将图像转换为灰度图"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def _binarization(self, image):
        """将图像二值化"""
        # 确保图像是灰度图
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用自适应阈值二值化
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
    
    def _noise_removal(self, image):
        """去除图像噪点"""
        # 确保图像是灰度图
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用中值滤波去噪
        return cv2.medianBlur(image, 3)
    
    def _deskew(self, image):
        """校正图像倾斜"""
        # 确保图像是灰度图
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算图像的倾斜角度
        coords = np.column_stack(np.where(image > 0))
        if len(coords) <= 10:  # 如果有效像素太少，跳过校正
            return image
            
        try:
            angle = cv2.minAreaRect(coords)[-1]
            
            # 如果角度小于-45度，加上90度
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # 旋转图像
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h), 
                flags=cv2.INTER_CUBIC, 
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return rotated
        except Exception:
            # 如果校正失败，返回原始图像
            return image
    
    def _extract_text(self, image):
        """
        从图像中提取文本
        
        参数:
            image (numpy.ndarray): 预处理后的图像
            
        返回:
            str: 提取的文本
        """
        # 将OpenCV图像转换为PIL图像
        if len(image.shape) == 3:
            # 彩色图像，BGR转RGB
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            # 灰度图像
            pil_image = Image.fromarray(image)
        
        # 使用Tesseract OCR提取文本
        try:
            text = pytesseract.image_to_string(pil_image, lang=self.ocr_lang)
        except Exception as e:
            raise Exception(f"OCR文本提取失败: {str(e)}")
        finally:
            # 释放PIL图像内存
            del pil_image
        
        return text


# 测试代码
if __name__ == "__main__":
    processor = ImageProcessor()
    
    # 测试图像路径
    image_path = "test_image.png"
    
    # 处理图像并提取文本
    text = processor.process_image(image_path)
    
    # 打印提取的文本
    print("提取的文本:")
    print(text)
