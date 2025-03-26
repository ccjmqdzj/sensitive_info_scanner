#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令行主程序 (cli_main.py)
该模块提供命令行界面，允许用户通过命令行参数扫描图像文件。
"""

import os
import argparse
import sys
from image_processor import ImageProcessor
from sensitive_info_detector import SensitiveInfoDetector
import concurrent.futures
import time

def process_file(file_path, image_processor, detector, selected_types, verbose=False):
    """
    处理单个文件
    
    参数:
        file_path (str): 文件路径
        image_processor (ImageProcessor): 图像处理器
        detector (SensitiveInfoDetector): 敏感信息检测器
        selected_types (list): 要检测的敏感信息类型
        verbose (bool): 是否显示详细信息
        
    返回:
        dict: 检测结果
    """
    try:
        if verbose:
            print(f"正在处理: {file_path}")
        
        # 检查文件是否存在且可读
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"没有读取文件的权限: {file_path}")
            
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path.lower())
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        if ext not in supported_formats:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        # 提取文本
        text = image_processor.process_image(file_path)
        
        # 检测敏感信息
        results = detector.detect_sensitive_info(text, selected_types)
        
        return {
            'file': file_path,
            'results': results,
            'success': True
        }
    except Exception as e:
        print(f"处理图像时出错: {str(e)}")
        return {
            'file': file_path,
            'error': str(e),
            'success': False
        }

def main():
    """
    命令行主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='敏感信息扫描工具 - 命令行版本')
    
    # 文件或文件夹参数（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', '--file', help='要扫描的图像文件路径')
    group.add_argument('-d', '--directory', help='要扫描的图像文件夹路径')
    
    # 其他参数
    parser.add_argument('-t', '--types', nargs='+', help='要检测的敏感信息类型（空格分隔）')
    parser.add_argument('-o', '--output', help='输出结果文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-j', '--jobs', type=int, default=4, help='并行处理的任务数（默认为4）')
    
    args = parser.parse_args()
    
    # 初始化图像处理器和敏感信息检测器
    image_processor = ImageProcessor()
    detector = SensitiveInfoDetector()
    
    # 获取所有可用的敏感信息类型
    available_types = [t['id'] for t in detector.get_available_info_types()]
    
    # 确定要检测的敏感信息类型
    if args.types:
        # 验证类型是否有效
        for type_id in args.types:
            if type_id not in available_types:
                print(f"错误: 无效的敏感信息类型: {type_id}")
                print(f"可用的类型有: {', '.join(available_types)}")
                sys.exit(1)
        
        selected_types = args.types
    else:
        # 默认使用所有类型
        selected_types = available_types
    
    # 收集要扫描的文件
    files_to_scan = []
    
    if args.file:
        # 单个文件
        if not os.path.isfile(args.file):
            print(f"错误: 文件不存在: {args.file}")
            sys.exit(1)
        
        files_to_scan.append(args.file)
    else:
        # 文件夹
        if not os.path.isdir(args.directory):
            print(f"错误: 文件夹不存在: {args.directory}")
            sys.exit(1)
        
        # 支持的图像格式
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        
        # 遍历文件夹中的所有文件
        for root, _, files in os.walk(args.directory):
            for file in files:
                if file.lower().endswith(image_extensions):
                    file_path = os.path.join(root, file)
                    files_to_scan.append(file_path)
    
    if not files_to_scan:
        print("错误: 没有找到要扫描的图像文件")
        sys.exit(1)
    
    print(f"开始扫描 {len(files_to_scan)} 个图像文件...")
    start_time = time.time()
    
    # 使用线程池并行处理文件
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(
                process_file, file, image_processor, detector, selected_types, args.verbose
            ): file for file in files_to_scan
        }
        
        # 处理结果
        for i, future in enumerate(concurrent.futures.as_completed(future_to_file), 1):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                if not args.verbose:
                    print(f"[{i}/{len(files_to_scan)}] 正在处理: {os.path.basename(file)}")
                    if not result['success']:
                        print(f"处理图像时出错: {result.get('error', '未知错误')}")
            except Exception as e:
                print(f"处理文件时出错: {file}, 错误: {str(e)}")
    
    # 统计结果
    successful_results = [r for r in results if r['success']]
    files_with_sensitive_info = [r for r in successful_results if r['results']]
    
    # 格式化输出
    output_text = []
    output_text.append("扫描完成!\n")
    
    if not files_with_sensitive_info:
        output_text.append("未在任何图像中检测到敏感信息。")
    else:
        output_text.append(f"在 {len(files_with_sensitive_info)}/{len(successful_results)} 个文件中检测到敏感信息：\n")
        
        for result in files_with_sensitive_info:
            file_path = result['file']
            file_results = result['results']
            
            output_text.append(f"文件: {os.path.basename(file_path)}")
            output_text.append(detector.format_results(file_results))
            output_text.append("-" * 50 + "\n")
    
    # 计算总耗时
    elapsed_time = time.time() - start_time
    output_text.append(f"\n总耗时: {elapsed_time:.2f} 秒")
    
    # 输出结果
    output_content = "\n".join(output_text)
    print(output_content)
    
    # 保存结果到文件
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"结果已保存到: {args.output}")
        except Exception as e:
            print(f"保存结果时出错: {str(e)}")

if __name__ == "__main__":
    main()
