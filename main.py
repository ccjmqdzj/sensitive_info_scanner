#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主程序 (main.py)
该模块是程序的入口点，负责启动图形用户界面。
"""

import tkinter as tk
from ui import UI

def main():
    """
    程序入口函数
    """
    # 创建Tkinter根窗口
    root = tk.Tk()
    
    # 创建用户界面
    app = UI(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()
