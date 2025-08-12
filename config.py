# Spotify API Configuration для SpotiSplit MVP
# Заповніть свої дані після створення Spotify Developer App
# Інструкції: https://developer.spotify.com/dashboard/

CLIENT_ID = "b7b8c75ab68d4397be30272f2e678090"
CLIENT_SECRET = "05457f6d857249328e4cb3be02c58df9"
REDIRECT_URI = "http://localhost:4000/callback"
USERNAME = "your_spotify_username"  # можна лишити порожнім

# Налаштування плейлістів
SOURCE_PLAYLIST_URL = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
N_CLUSTERS = 20  # скільки плейлістів створювати
MAKE_PUBLIC = False  # True -> публічні плейлісти

# Додаткові опції
PLAYLIST_NAME_PREFIX = "SpotiSplit"
RANDOM_STATE = 42
