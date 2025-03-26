#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户界面模块 (ui.py)
该模块负责创建图形用户界面，允许用户选择文件和敏感信息类型，并展示扫描结果。
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from image_processor import ImageProcessor
from sensitive_info_detector import SensitiveInfoDetector
import threading
from queue import Queue
import time
import gc

class UI:
    """
    用户界面类，负责创建和管理图形界面
    """
    
    def __init__(self, root):
        """
        初始化用户界面
        
        参数:
            root (tk.Tk): Tkinter根窗口
        """
        self.root = root
        self.root.title("敏感信息扫描工具")
        self.root.geometry("1000x600")
        
        # 初始化图像处理器和敏感信息检测器
        self.image_processor = ImageProcessor()
        self.detector = SensitiveInfoDetector()
        
        # 存储敏感信息类型的复选框变量
        self.type_vars = {}
        
        # 创建界面组件
        self.create_widgets()
        
        # 扫描状态
        self.scanning = False
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧框架（文件选择和敏感信息类型）
        left_frame = ttk.Frame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建右侧框架（结果显示）
        right_frame = ttk.Frame(main_frame, width=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文件选择部分
        file_frame = ttk.LabelFrame(left_frame, text="文件选择")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 按钮框架
        self.button_frame = ttk.Frame(file_frame)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加文件按钮
        self.add_file_button = ttk.Button(self.button_frame, text="添加文件", command=self.add_files)
        self.add_file_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 添加文件夹按钮
        self.add_folder_button = ttk.Button(self.button_frame, text="添加文件夹", command=self.add_folder)
        self.add_folder_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 清空列表按钮
        self.clear_list_button = ttk.Button(self.button_frame, text="清空列表", command=self.clear_file_list)
        self.clear_list_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 开始扫描按钮
        self.scan_button = ttk.Button(self.button_frame, text="开始扫描", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 敏感信息类型部分
        type_frame = ttk.LabelFrame(left_frame, text="敏感信息类型")
        type_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 获取可用的敏感信息类型
        info_types = self.detector.get_available_info_types()
        
        # 创建复选框
        for info_type in info_types:
            var = tk.BooleanVar(value=True)
            self.type_vars[info_type['id']] = var
            
            checkbox = ttk.Checkbutton(
                type_frame,
                text=f"{info_type['name']} - {info_type['description']}",
                variable=var
            )
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
        
        # 结果显示部分
        result_frame = ttk.LabelFrame(right_frame, text="扫描结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 结果文本框
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 结果操作按钮框架
        self.result_button_frame = ttk.Frame(result_frame)
        self.result_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 清空结果按钮
        self.clear_result_button = ttk.Button(self.result_button_frame, text="清空结果", command=self.clear_result)
        self.clear_result_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 保存结果按钮
        self.save_result_button = ttk.Button(self.result_button_frame, text="保存结果", command=self.save_result)
        self.save_result_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.result_button_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
    
    def add_files(self):
        """添加文件到列表"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        filetypes = (
            ("图像文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("所有文件", "*.*")
        )
        
        files = filedialog.askopenfilenames(
            title="选择图像文件",
            filetypes=filetypes
        )
        
        if files:
            for file in files:
                self.file_listbox.insert(tk.END, file)
    
    def add_folder(self):
        """添加文件夹中的所有图像文件到列表"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            # 支持的图像格式
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
            
            # 遍历文件夹中的所有文件
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(image_extensions):
                        file_path = os.path.join(root, file)
                        self.file_listbox.insert(tk.END, file_path)
    
    def clear_file_list(self):
        """清空文件列表"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        self.file_listbox.delete(0, tk.END)
    
    def clear_result(self):
        """清空结果文本框"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        self.result_text.delete(1.0, tk.END)
    
    def save_result(self):
        """保存结果到文件"""
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        result_text = self.result_text.get(1.0, tk.END)
        
        if not result_text.strip():
            messagebox.showwarning("警告", "没有结果可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".txt",
            filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                messagebox.showinfo("成功", f"结果已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存结果时出错: {str(e)}")
    
    def start_scan(self):
        """开始扫描所选文件"""
        # 防止重复扫描
        if self.scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待扫描完成")
            return
            
        # 获取所选文件
        files = self.file_listbox.get(0, tk.END)
        if not files:
            messagebox.showwarning("警告", "请先添加要扫描的文件")
            return
        
        # 获取所选敏感信息类型
        selected_types = []
        for type_id, var in self.type_vars.items():
            if var.get():
                selected_types.append(type_id)
        
        if not selected_types:
            messagebox.showwarning("警告", "请至少选择一种敏感信息类型")
            return
        
        # 清空结果
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "开始扫描...\n\n")
        self.root.update()
        
        # 设置扫描状态
        self.scanning = True
        
        # 禁用按钮，防止重复操作
        self.scan_button.config(state=tk.DISABLED)
        self.add_file_button.config(state=tk.DISABLED)
        self.add_folder_button.config(state=tk.DISABLED)
        self.clear_list_button.config(state=tk.DISABLED)
        self.clear_result_button.config(state=tk.DISABLED)
        self.save_result_button.config(state=tk.DISABLED)
        
        # 重置进度条
        self.progress_var.set(0)
        
        # 使用线程池限制并发线程数
        max_workers = min(10, len(files))  # 最多10个线程或文件数量
        
        # 添加取消扫描按钮
        self.cancel_button = ttk.Button(self.result_button_frame, text="取消扫描", command=self.stop_scan)
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 创建结果队列和工作线程
        result_queue = Queue()
        total_files = len(files)
        processed_count = [0]  # 使用列表以便在线程中修改
        
        # 用于保存所有扫描结果的列表
        all_results = []
        
        # 进度更新函数
        def update_progress():
            while processed_count[0] < total_files and self.scanning:
                # 更新进度条
                progress = (processed_count[0] / total_files) * 100
                self.progress_var.set(progress)
                
                # 检查队列中是否有结果
                while not result_queue.empty():
                    result = result_queue.get()
                    if result['type'] == 'progress':
                        self.result_text.delete(1.0, tk.END)
                        self.result_text.insert(tk.END, f"扫描进度: [{result['index']}/{total_files}]\n")
                        self.result_text.insert(tk.END, f"正在处理: {os.path.basename(result['file'])}\n\n")
                        self.result_text.insert(tk.END, "请等待，扫描完成后将显示完整结果...\n")
                    elif result['type'] == 'error':
                        # 记录错误但不立即显示
                        all_results.append({
                            'is_error': True,
                            'file': result.get('file', '未知文件'),
                            'error': result['error']
                        })
                    elif result['type'] == 'result':
                        # 记录结果但不立即显示
                        all_results.append({
                            'is_error': False,
                            'file': result['file'],
                            'results': result['results']
                        })
                
                self.root.update()
                time.sleep(0.1)
            
            # 所有文件处理完成，显示所有结果
            if self.scanning:  # 如果不是因为取消而结束
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "扫描完成!\n\n")
                
                # 统计有敏感信息的文件数量
                files_with_sensitive_info = [r for r in all_results if not r['is_error'] and r['results']]
                
                if not files_with_sensitive_info:
                    self.result_text.insert(tk.END, "未在任何图像中检测到敏感信息。\n")
                else:
                    self.result_text.insert(tk.END, f"在 {len(files_with_sensitive_info)}/{len(all_results)} 个文件中检测到敏感信息：\n\n")
                    
                    # 显示所有发现敏感信息的文件
                    for result in files_with_sensitive_info:
                        file_path = result['file']
                        file_results = result['results']
                        
                        self.result_text.insert(tk.END, f"文件: {os.path.basename(file_path)}\n")
                        self.result_text.insert(tk.END, self.detector.format_results(file_results))
                        self.result_text.insert(tk.END, "\n" + "-"*50 + "\n\n")
                    
                    # 显示错误信息
                    errors = [r for r in all_results if r['is_error']]
                    if errors:
                        self.result_text.insert(tk.END, f"\n处理过程中出现 {len(errors)} 个错误：\n\n")
                        for error in errors:
                            self.result_text.insert(tk.END, f"文件: {os.path.basename(error['file'])}\n")
                            self.result_text.insert(tk.END, f"错误: {error['error']}\n\n")
            
            # 重新启用按钮
            self.scan_button.config(state=tk.NORMAL)
            self.add_file_button.config(state=tk.NORMAL)
            self.add_folder_button.config(state=tk.NORMAL)
            self.clear_list_button.config(state=tk.NORMAL)
            self.clear_result_button.config(state=tk.NORMAL)
            self.save_result_button.config(state=tk.NORMAL)
            
            # 移除取消按钮
            if hasattr(self, 'cancel_button'):
                self.cancel_button.destroy()
            
            # 重置扫描状态
            self.scanning = False
            
            # 进度条设为100%
            self.progress_var.set(100)
        
        # 工作线程函数
        def worker():
            for i, file_path in enumerate(files, 1):
                if not self.scanning:
                    break
                    
                # 发送进度更新
                result_queue.put({
                    'type': 'progress',
                    'index': i,
                    'file': file_path
                })
                
                try:
                    # 提取文本
                    text = self.image_processor.process_image(file_path)
                    
                    # 检测敏感信息
                    file_results = self.detector.detect_sensitive_info(text, selected_types)
                    
                    # 发送结果
                    result_queue.put({
                        'type': 'result',
                        'file': file_path,
                        'results': file_results
                    })
                except Exception as e:
                    # 发送错误
                    result_queue.put({
                        'type': 'error',
                        'file': file_path,
                        'error': str(e)
                    })
                
                # 更新处理计数
                processed_count[0] += 1
                
                # 主动释放内存
                gc.collect()
        
        # 启动工作线程和进度更新线程
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.progress_thread = threading.Thread(target=update_progress, daemon=True)
        
        self.worker_thread.start()
        self.progress_thread.start()
    
    def stop_scan(self):
        """停止扫描"""
        if self.scanning:
            self.scanning = False
            self.result_text.insert(tk.END, "\n扫描已停止!\n")
            
            # 等待线程完成
            if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=1.0)
            
            if hasattr(self, 'progress_thread') and self.progress_thread.is_alive():
                self.progress_thread.join(timeout=1.0)
            
            # 重新启用按钮
            self.scan_button.config(state=tk.NORMAL)
            self.add_file_button.config(state=tk.NORMAL)
            self.add_folder_button.config(state=tk.NORMAL)
            self.clear_list_button.config(state=tk.NORMAL)
            self.clear_result_button.config(state=tk.NORMAL)
            self.save_result_button.config(state=tk.NORMAL)
            
            # 移除取消按钮
            if hasattr(self, 'cancel_button'):
                self.cancel_button.destroy()
