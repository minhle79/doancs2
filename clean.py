#!/usr/bin/env python
"""
Script để làm sạch dự án Django
Xóa các file cache, __pycache__, và các file tạm
"""
import os
import shutil
from pathlib import Path


def clean_project():
    """Làm sạch dự án"""
    project_root = Path(__file__).parent
    
    # Các pattern cần xóa
    patterns_to_delete = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd',
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/*.log',
    ]
    
    deleted_count = 0
    
    for pattern in patterns_to_delete:
        for path in project_root.glob(pattern):
            # Bỏ qua .venv folder
            if '.venv' in str(path) or 'venv' in str(path):
                continue
                
            try:
                if path.is_file():
                    path.unlink()
                    print(f"Deleted file: {path}")
                    deleted_count += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"Deleted dir: {path}")
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {path}: {e}")
    
    print(f"\n✅ Cleaned {deleted_count} items")


if __name__ == '__main__':
    clean_project()
