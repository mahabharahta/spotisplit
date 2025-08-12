# 🚀 Швидкий старт SpotiSplit MVP

## ⚡ За 5 хвилин до першого запуску

### 1. Встановлення (1 хв)
```bash
# Клонуйте репозиторій
git clone <your-repo-url>
cd spotisplit

# Запустіть автоматичне встановлення
./setup.sh          # Linux/Mac
setup.bat           # Windows
```

**Або використовуйте Make:**
```bash
make setup
```

### 2. Spotify Developer App (2 хв)
1. Перейдіть на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Натисніть **"Create App"**
3. Заповніть:
   - **App name:** SpotiSplit
   - **App description:** Split playlists by audio similarity
   - **Website:** http://localhost:8080
   - **Redirect URI:** http://localhost:8080/callback
4. Скопіюйте **Client ID** та **Client Secret**

**💡 Детальні інструкції:** README.md → "Налаштування Spotify API"

### 3. Налаштування (1 хв)
```bash
# Скопіюйте приклад конфігурації
cp config.example.py config.py

# Відредагуйте config.py
nano config.py  # або відкрийте в любому редакторі
```

**Або використовуйте Make:**
```bash
make config
```

**Замініть в config.py:**
```python
CLIENT_ID = "ваш_client_id_тут"
CLIENT_SECRET = "ваш_client_secret_тут"
```

### 4. Запуск (1 хв)
```bash
# Активуйте віртуальне середовище
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows

# Запустіть
python run_spotisplit.py
```

**Або використовуйте Make:**
```bash
make run
```

## 🎯 Готово!

- ✅ Створяться N плейлістів з треками
- ✅ Треки розподілені за спорідненістю
- ✅ Результати збережені в CSV
- ✅ Візуалізація кластерів (PCA)
- ✅ Метрика якості кластеризації
- ✅ Автоматичне встановлення та налаштування
- ✅ Перевірка готовності проекту

## 🔧 Альтернативні способи запуску

### Make команди (рекомендовано)
```bash
make check      # Перевірити готовність
make run        # Запустити SpotiSplit
make notebook   # Запустити Jupyter
make help       # Показати всі команди
make setup      # Автоматичне встановлення
make config     # Створити конфігурацію
```

### Jupyter Notebook
```bash
jupyter notebook spotisplit_mvp.ipynb
```

### Google Colab
1. Завантажте `spotisplit_mvp.ipynb` в Colab
2. Встановіть залежності (клітинка 1)
3. Налаштуйте конфігурацію (клітинка 2)

## 🚨 Якщо щось не працює

### Помилка авторизації
- Перевірте CLIENT_ID та CLIENT_SECRET
- Переконайтеся що REDIRECT_URI співпадає з налаштуваннями

### Помилка імпорту
```bash
pip install -r requirements.txt
```

### Помилка прав доступу
- Переконайтеся що у вас є права на плейлісти
- Для приватних плейлістів потрібні права `playlist-read-private`

## 📞 Підтримка

- 📚 **Документація:** README.md та QUICKSTART.md
- 🔍 **Перевірка:** `make check` або `python3 check_ready.py`
- 🛠️ **Довідка:** `make help`
- 🐛 **Проблеми:** створіть issue в репозиторії

---

**Приємного використання! 🎧✨**
