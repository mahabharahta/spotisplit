# SpotiSplit MVP - Makefile з корисними командами
# Використання: make help

.PHONY: help install setup run clean test check

help: ## Показати цю довідку
	@echo "🎵 SpotiSplit MVP - Доступні команди:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Встановити залежності
	pip install -r requirements.txt

setup: ## Налаштувати проект (створення venv + встановлення)
	./setup.sh

run: ## Запустити SpotiSplit
	python run_spotisplit.py

notebook: ## Запустити Jupyter notebook
	jupyter notebook spotisplit_mvp.ipynb

clean: ## Очистити тимчасові файли
	rm -rf __pycache__/
	rm -rf .ipynb_checkpoints/
	rm -f *.csv
	rm -f .cache-*

test: ## Запустити тести (якщо є)
	@echo "🧪 Тести поки не реалізовані"

check: ## Перевірити готовність проекту
	python3 check_ready.py

config: ## Створити конфігурацію з прикладу
	cp config.example.py config.py
	@echo "✅ Створено config.py з прикладу"
	@echo "📝 Відредагуйте config.py та додайте свої Spotify API ключі"

venv: ## Створити віртуальне середовище
	python3 -m venv venv
	@echo "✅ Створено віртуальне середовище"
	@echo "💡 Активуйте його: source venv/bin/activate"

deps: ## Перевірити залежності
	@echo "📦 Перевірка залежностей..."
	@python3 -c "import spotipy, pandas, numpy, matplotlib, sklearn; print('✅ Всі залежності встановлені')" || echo "❌ Деякі залежності відсутні. Запустіть: make install"

status: ## Показати статус проекту
	@echo "🎵 SpotiSplit MVP - Статус проекту"
	@echo "=================================="
	@echo "📁 Файли проекту:"
	@ls -la
	@echo ""
	@echo "🐍 Python версія:"
	@python3 --version
	@echo ""
	@echo "📦 Залежності:"
	@make deps
