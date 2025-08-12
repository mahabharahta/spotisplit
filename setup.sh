#!/bin/bash
# SpotiSplit MVP - Автоматичне встановлення для Linux/Mac
# Використання: ./setup.sh

echo "🎵 SpotiSplit MVP - Швидке встановлення"
echo "========================================"

# Перевіряємо чи встановлений Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не знайдено. Встановіть Python 3.8+"
    exit 1
fi

echo "✅ Python $(python3 --version) знайдено"

# Створюємо віртуальне середовище
echo "🔧 Створення віртуального середовища..."
python3 -m venv venv

# Активуємо віртуальне середовище
echo "📦 Активація віртуального середовища..."
source venv/bin/activate

# Встановлюємо залежності
echo "📥 Встановлення залежностей..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Встановлення завершено!"
echo ""
echo "🚀 Наступні кроки:"
echo "1. Налаштуйте Spotify Developer App:"
echo "   - Перейдіть на https://developer.spotify.com/dashboard/"
echo "   - Створіть новий застосунок"
echo "   - Додайте Redirect URI: http://localhost:8080/callback"
echo ""
echo "2. Налаштуйте конфігурацію:"
echo "   - Відредагуйте config.py"
echo "   - Заповніть CLIENT_ID та CLIENT_SECRET"
echo ""
echo "3. Запустіть проект:"
echo "   - Jupyter: jupyter notebook spotisplit_mvp.ipynb"
echo "   - Python: python run_spotisplit.py"
echo ""
echo "📚 Детальні інструкції: README.md"
echo ""
echo "💡 Для активації віртуального середовища: source venv/bin/activate"
