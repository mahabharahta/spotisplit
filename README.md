# SpotiSplit MVP 🎵

Інструмент для автоматичного розбиття Spotify плейлістів на кластери за спорідненістю аудіо характеристик.

## 🚀 Що робить

1. **Завантажує треки** з вихідного плейліста Spotify
2. **Отримує audio features** для кожного треку (danceability, energy, tempo, тощо)
3. **Кластеризує** треки у N груп за допомогою K-Means алгоритму
4. **Створює N нових плейлістів** та розкладає треки по них
5. **Експортує результати** у CSV форматі
6. **Візуалізує кластери** за допомогою PCA проекції
7. **Надає метрики якості** кластеризації (Silhouette score)

## 📋 Вимоги

- **Python 3.8+** (перевірка: `python3 --version`)
- **Spotify Premium акаунт** (для доступу до audio features)
- **Spotify Developer App** (для API ключів)
- **Git** (для клонування репозиторію)

## 🛠️ Встановлення

### Автоматичне встановлення (рекомендовано)

**Linux/Mac:**
```bash
git clone <your-repo-url>
cd spotisplit
./setup.sh
```

**Windows:**
```bash
git clone <your-repo-url>
cd spotisplit
setup.bat
```

### Ручне встановлення

1. **Клонуйте репозиторій:**
```bash
git clone <your-repo-url>
cd spotisplit
```

2. **Встановіть залежності:**
```bash
pip install -r requirements.txt
```

## ⚙️ Налаштування Spotify API

### 1. Створіть Spotify Developer App

1. Перейдіть на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
2. Натисніть "Create App"
3. Заповніть форму:
   - **App name:** SpotiSplit
   - **App description:** Split playlists by audio similarity
   - **Website:** http://localhost:8080
   - **Redirect URI:** http://localhost:8080/callback
   - **API/SDKs:** Web API

### 2. Отримайте ключі

1. Після створення додатку, скопіюйте:
   - **Client ID**
   - **Client Secret**

### 3. Налаштуйте конфігурацію

1. Відкрийте `config.py`
2. Заповніть свої дані:
```python
CLIENT_ID = "ваш_client_id"
CLIENT_SECRET = "ваш_client_secret"
REDIRECT_URI = "http://localhost:8080/callback"
```

## 🚀 Запуск

### Швидкий старт (рекомендовано)
```bash
# 1. Автоматичне встановлення
./setup.sh          # Linux/Mac
setup.bat           # Windows

# 2. Перевірка готовності
make check

# 3. Запуск
make run
```

### Видалення створених плейлістів

Якщо потрібно видалити всі створені SpotiSplit плейлісти:

```bash
# Видалити всі плейлісти з "SpotiSplit" в назві
python run_spotisplit.py --delete

# Видалити плейлісти з іншим префіксом
python run_spotisplit.py --delete --prefix "MyPrefix"

# Версія без audio features
python run_spotisplit_no_audio.py --delete
```

**⚠️ Увага:** Ця операція незворотна! Всі плейлісти з вказаним префіксом будуть видалені.

### Альтернативні способи

1. **Make команди (рекомендовано):**
```bash
make check      # Перевірити готовність
make run        # Запустити SpotiSplit
make notebook   # Запустити Jupyter
make help       # Показати всі команди
```

2. **Jupyter notebook:**
```bash
jupyter notebook spotisplit_mvp.ipynb
```

3. **Python скрипт:**
```bash
python3 run_spotisplit.py
```

4. **Google Colab:**
   - Завантажте `spotisplit_mvp.ipynb` в Colab
   - Встановіть залежності (клітинка 1)
   - Налаштуйте конфігурацію (клітинка 2)

## 📝 Використання

1. **Налаштуйте параметри** у клітинці 2:
   - `SOURCE_PLAYLIST_URL` - посилання на плейліст для розбиття
   - `N_CLUSTERS` - кількість плейлістів для створення
   - `MAKE_PUBLIC` - чи робити плейлісти публічними

2. **Запустіть всі клітинки** по порядку

3. **Результат:**
   - Створяться N нових плейлістів
   - Треки будуть розподілені за спорідненістю
   - Експортовано CSV з результатами

## 🔧 Налаштування

### Параметри кластеризації

- **danceability** - танцювальність
- **energy** - енергійність  
- **speechiness** - наявність мови
- **acousticness** - акустичність
- **instrumentalness** - інструментальність
- **liveness** - живостість
- **valence** - позитивність
- **tempo** - темп
- **loudness** - гучність

### Кількість кластерів

Рекомендовано 3-7 кластерів для кращого розділення. При більшій кількості може бути важко розрізнити різницю між плейлістами.

## 📊 Результати

- **CSV файл** з усіма треками та їх кластерами
- **Візуалізація** кластерів (PCA 2D проекція)
- **Метрика якості** кластеризації (Silhouette score)

## 🚨 Усунення проблем

### Помилка авторизації
- Перевірте правильність `CLIENT_ID` та `CLIENT_SECRET`
- Переконайтеся, що `REDIRECT_URI` співпадає з налаштуваннями в Spotify Dashboard

### Помилка прав доступу
- Переконайтеся, що у вас є права на читання та модифікацію плейлістів
- Для приватних плейлістів потрібні права `playlist-read-private`

### Недостатньо треків
- Перевірте, що плейліст містить достатньо треків для кластеризації
- Мінімум: N_CLUSTERS + 1 трек

### Помилка імпорту
```bash
pip install -r requirements.txt
# або
make install
```

### Перевірка готовності
```bash
make check
# або
python3 check_ready.py
```

## 📁 Структура проекту

```
spotisplit/
├── 📓 spotisplit_mvp.ipynb    # Основний Jupyter notebook
├── 🐍 run_spotisplit.py       # Python скрипт для запуску
├── ⚙️ config.py               # Конфігурація (створюється з config.example.py)
├── 📋 config.example.py       # Приклад конфігурації
├── 📦 requirements.txt        # Залежності Python
├── 🐧 setup.sh               # Скрипт встановлення для Linux/Mac
├── 🪟 setup.bat              # Скрипт встановлення для Windows
├── 🔍 check_ready.py         # Перевірка готовності проекту
├── 🛠️ Makefile               # Команди для зручності
├── 🚫 .gitignore             # Git ігнорування
├── 📚 README.md              # Детальна документація
└── 🚀 QUICKSTART.md          # Швидкий старт гід
```

## 🛠️ Корисні команди

```bash
make help      # Показати всі команди
make setup     # Автоматичне встановлення
make check     # Перевірити готовність
make run       # Запустити SpotiSplit
make clean     # Очистити тимчасові файли
make config    # Створити конфігурацію з прикладу
make deps      # Перевірити залежності
make status    # Показати статус проекту
make venv      # Створити віртуальне середовище
```

## 📄 Ліцензія

MIT License

## 🤝 Внесок

Вітаються pull requests та issues!

## 🆘 Підтримка

- 📚 **Документація:** README.md та QUICKSTART.md
- 🔍 **Перевірка:** `make check` або `python3 check_ready.py`
- 🛠️ **Довідка:** `make help`
- 🐛 **Проблеми:** створіть issue в репозиторії

---

**Приємного використання! 🎧✨**
# spotisplit
