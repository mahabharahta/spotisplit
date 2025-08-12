# Приклад конфігурації для SpotiSplit MVP
# Скопіюйте цей файл як config.py та заповніть свої дані
# Команда: cp config.example.py config.py

# Spotify API налаштування
# Отримайте ці дані на https://developer.spotify.com/dashboard/
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://localhost:8080/callback"
USERNAME = "your_spotify_username"  # можна лишити порожнім

# Налаштування плейлістів
SOURCE_PLAYLIST_URL = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
N_CLUSTERS = 5  # скільки плейлістів створювати
MAKE_PUBLIC = False  # True -> публічні плейлісти

# Додаткові опції
PLAYLIST_NAME_PREFIX = "SpotiSplit"
RANDOM_STATE = 42

# Приклади налаштувань:
# 
# Для розбиття на 3 плейлісти:
# N_CLUSTERS = 3
# 
# Для публічних плейлістів:
# MAKE_PUBLIC = True
# 
# Для іншого плейліста:
# SOURCE_PLAYLIST_URL = "https://open.spotify.com/playlist/YOUR_PLAYLIST_ID"
