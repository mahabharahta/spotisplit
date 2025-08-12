@echo off
REM SpotiSplit MVP - Автоматичне встановлення для Windows
REM Використання: setup.bat
chcp 65001 >nul
echo 🎵 SpotiSplit MVP - Швидке встановлення для Windows
echo ===================================================

REM Перевіряємо чи встановлений Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не знайдено. Встановіть Python 3.8+
    echo 📥 Завантажте з: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python знайдено
python --version

REM Створюємо віртуальне середовище
echo 🔧 Створення віртуального середовища...
python -m venv venv

REM Активуємо віртуальне середовище
echo 📦 Активація віртуального середовища...
call venv\Scripts\activate.bat

REM Встановлюємо залежності
echo 📥 Встановлення залежностей...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Встановлення завершено!
echo.
echo 🚀 Наступні кроки:
echo 1. Налаштуйте Spotify Developer App:
echo    - Перейдіть на https://developer.spotify.com/dashboard/
echo    - Створіть новий застосунок
echo    - Додайте Redirect URI: http://localhost:8080/callback
echo.
echo 2. Налаштуйте конфігурацію:
echo    - Відредагуйте config.py
echo    - Заповніть CLIENT_ID та CLIENT_SECRET
echo.
echo 3. Запустіть проект:
echo    - Python: python run_spotisplit.py
echo    - Jupyter: jupyter notebook spotisplit_mvp.ipynb
echo.
echo 📚 Детальні інструкції: README.md
echo.
echo 💡 Для активації віртуального середовища: venv\Scripts\activate.bat
pause
