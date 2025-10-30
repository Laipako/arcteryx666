#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
缓存清理脚本 - 用于部署前清除所有缓存
在Streamlit部署前运行此脚本确保新代码生效
"""

import os
import shutil
import sys
from pathlib import Path

def clean_pycache():
    """清除所有__pycache__目录"""
    print("🧹 正在清理Python字节码缓存...")
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"  ✓ 已删除: {cache_path}")
            except Exception as e:
                print(f"  ✗ 删除失败: {cache_path} - {e}")

def clean_streamlit_cache():
    """清除Streamlit缓存目录"""
    print("\n🧹 正在清理Streamlit缓存...")
    cache_dir = os.path.expanduser("~/.streamlit/cache")
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
            print(f"  ✓ 已删除Streamlit缓存目录")
        except Exception as e:
            print(f"  ✗ 删除失败: {e}")

def clean_pyc_files():
    """删除所有.pyc文件"""
    print("\n🧹 正在清理.pyc文件...")
    count = 0
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    count += 1
                except Exception as e:
                    print(f"  ✗ 删除失败: {file_path} - {e}")
    if count > 0:
        print(f"  ✓ 已删除 {count} 个.pyc文件")

def main():
    """主函数"""
    print("=" * 50)
    print("Streamlit 缓存清理工具")
    print("=" * 50)
    
    try:
        clean_pycache()
        clean_streamlit_cache()
        clean_pyc_files()
        
        print("\n" + "=" * 50)
        print("✅ 缓存清理完成！")
        print("请重新部署Streamlit应用")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 清理过程出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
