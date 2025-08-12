#!/usr/bin/env python3
"""
Скрипт перевірки готовності SpotiSplit MVP до запуску
Використання: python3 check_ready.py або make check
"""

import os
import sys
import importlib

def check_python_version():
    """Перевіряє версію Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} не підтримується")
        print("📋 Потрібен Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Перевіряє наявність залежностей"""
    required_packages = [
        'spotipy',
        'pandas', 
        'numpy',
        'matplotlib',
        'sklearn'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Відсутні пакети: {', '.join(missing)}")
        print("💡 Встановіть: pip install -r requirements.txt")
        return False
    
    return True

def check_config():
    """Перевіряє конфігурацію"""
    try:
        from config import CLIENT_ID, CLIENT_SECRET
        if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
            print("⚠️ config.py не налаштовано")
            print("📝 Заповніть CLIENT_ID та CLIENT_SECRET в config.py")
            return False
        print("✅ config.py налаштовано")
        return True
    except ImportError:
        print("❌ config.py не знайдено")
        print("💡 Створіть: cp config.example.py config.py")
        return False

def check_files():
    """Перевіряє наявність необхідних файлів"""
    required_files = [
        'requirements.txt',
        'config.py', 
        'run_spotisplit.py',
        'spotisplit_mvp.ipynb'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing.append(file)
    
    if missing:
        print(f"\n📁 Відсутні файли: {', '.join(missing)}")
        return False
    
    return True

def main():
    """Основна функція перевірки"""
    print("🔍 SpotiSplit MVP - Перевірка готовності")
    print("=" * 40)
    
    checks = [
        ("🐍 Версія Python", check_python_version),
        ("📦 Залежності", check_dependencies),
        ("⚙️ Конфігурація", check_config),
        ("📁 Файли проекту", check_files)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Помилка перевірки: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    
    if all(results):
        print("🎉 Всі перевірки пройдені! Проект готовий до запуску.")
        print("\n🚀 Способи запуску:")
        print("  • Python: python run_spotisplit.py")
        print("  • Jupyter: jupyter notebook spotisplit_mvp.ipynb")
        print("  • Make: make run")
    else:
        print("❌ Деякі перевірки не пройдені.")
        print("\n🔧 Виправлення:")
        print("  • Встановлення: make setup")
        print("  • Конфігурація: make config")
        print("  • Довідка: make help")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
