#!/usr/bin/env python3
"""
SpotiSplit MVP - Скрипт для запуску без Jupyter notebook
Використання: python3 run_spotisplit.py або make run
"""

import os
import sys
import re
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    print("📦 Встановіть залежності: pip install -r requirements.txt")
    sys.exit(1)

def load_config():
    """Завантажує конфігурацію з config.py або використовує значення за замовчуванням"""
    try:
        import config
        print("✅ Завантажено конфігурацію з config.py")
        return {
            "CLIENT_ID": config.CLIENT_ID,
            "CLIENT_SECRET": config.CLIENT_SECRET,
            "REDIRECT_URI": config.REDIRECT_URI,
            "USERNAME": config.USERNAME,
            "SOURCE_PLAYLIST_URL": config.SOURCE_PLAYLIST_URL,
            "N_CLUSTERS": config.N_CLUSTERS,
            "MAKE_PUBLIC": config.MAKE_PUBLIC,
            "PLAYLIST_NAME_PREFIX": config.PLAYLIST_NAME_PREFIX,
            "RANDOM_STATE": config.RANDOM_STATE
        }
    except ImportError:
        print("⚠️ Файл config.py не знайдено. Використовую значення за замовчуванням.")
        return {
            "CLIENT_ID": "YOUR_CLIENT_ID",
            "CLIENT_SECRET": "YOUR_CLIENT_SECRET", 
            "REDIRECT_URI": "http://localhost:8080/callback",
            "USERNAME": "your_spotify_username",
            "SOURCE_PLAYLIST_URL": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "N_CLUSTERS": 5,
            "MAKE_PUBLIC": False,
            "PLAYLIST_NAME_PREFIX": "SpotiSplit",
            "RANDOM_STATE": 42
        }

def extract_playlist_id(url_or_id: str) -> str:
    """Витягує ID плейліста з URL або ID"""
    m = re.search(r"playlist/([a-zA-Z0-9]+)", url_or_id)
    if m:
        return m.group(1)
    return url_or_id.strip()

def get_all_playlist_tracks(sp, playlist_id: str) -> List[Dict[str, Any]]:
    """Отримує всі треки з плейліста"""
    results = sp.playlist_items(playlist_id, additional_types=["track"], market=None)
    items = results.get("items", [])
    while results.get("next"):
        results = sp.next(results)
        items.extend(results.get("items", []))
    # Фільтруємо треки (без episodes/local)
    items = [it for it in items if it.get("track") and it["track"].get("id")]
    return items

def get_all_liked_tracks(sp) -> List[Dict[str, Any]]:
    """Отримує всі Liked Songs"""
    results = sp.current_user_saved_tracks(limit=50)
    items = results.get("items", [])
    while results.get("next"):
        results = sp.next(results)
        items.extend(results.get("items", []))
    # Фільтруємо треки (без episodes/local)
    items = [it for it in items if it.get("track") and it["track"].get("id")]
    return items

def batched(iterable, n=100):
    """Розбиває ітерабельний об'єкт на батчі"""
    batch = []
    for x in iterable:
        batch.append(x)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch

def fetch_audio_features(sp, track_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Отримує audio features для треків"""
    feats = {}
    for chunk in batched(track_ids, 100):
        af = sp.audio_features(chunk)
        for t_id, f in zip(chunk, af):
            if f:
                feats[t_id] = f
    return feats

def track_row(item, features_map):
    """Створює рядок даних для треку"""
    t = item["track"]
    t_id = t["id"]
    f = features_map.get(t_id, {})
    return {
        "track_id": t_id,
        "track_name": t["name"],
        "artist": ", ".join([a["name"] for a in t["artists"]]),
        "album": t["album"]["name"] if t.get("album") else None,
        "added_at": item.get("added_at"),
        "duration_ms": t.get("duration_ms"),
        "popularity": t.get("popularity"),
        # audio features:
        "danceability": f.get("danceability"),
        "energy": f.get("energy"),
        "speechiness": f.get("speechiness"),
        "acousticness": f.get("acousticness"),
        "instrumentalness": f.get("instrumentalness"),
        "liveness": f.get("liveness"),
        "valence": f.get("valence"),
        "tempo": f.get("tempo"),
        "loudness": f.get("loudness"),
        "key": f.get("key"),
        "mode": f.get("mode"),
        "time_signature": f.get("time_signature"),
        "uri": t.get("uri"),
        "external_url": t.get("external_urls", {}).get("spotify"),
    }

def create_playlist(sp, user_id: str, name: str, description: str = "", public: bool = False) -> str:
    """Створює новий плейліст"""
    pl = sp.user_playlist_create(user=user_id, name=name, public=public, description=description)
    return pl["id"]

def add_tracks_to_playlist(sp, playlist_id: str, uris: List[str]):
    """Додає треки до плейліста"""
    for chunk in batched(uris, 100):
        sp.playlist_add_items(playlist_id, chunk)

# Constants
SPOTIFY_SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative", 
    "playlist-modify-private",
    "user-library-read",  # Для доступу до Liked Songs
    "user-read-private",  # Для доступу до audio features
]

FEATURE_COLUMNS = [
    "danceability", "energy", "acousticness", "tempo"
]

def delete_spotisplit_playlists(sp, user_id: str, prefix: str = "SpotiSplit"):
    """Видаляє всі плейлісти з 'SpotiSplit' в назві"""
    print(f"🗑️ Пошук плейлістів з '{prefix}' в назві...")
    
    # Отримуємо всі плейлісти користувача
    playlists = []
    results = sp.user_playlists(user_id, limit=50)
    playlists.extend(results.get("items", []))
    
    while results.get("next"):
        results = sp.next(results)
        playlists.extend(results.get("items", []))
    
    # Фільтруємо плейлісти з SpotiSplit в назві
    spotisplit_playlists = [pl for pl in playlists if prefix.lower() in pl["name"].lower()]
    
    if not spotisplit_playlists:
        print(f"✅ Плейлісти з '{prefix}' в назві не знайдено")
        return
    
    print(f"🔍 Знайдено {len(spotisplit_playlists)} плейлістів для видалення:")
    for pl in spotisplit_playlists:
        print(f"   • {pl['name']} (ID: {pl['id']})")
    
    # Підтвердження видалення
    confirm = input(f"\n⚠️ Ви впевнені, що хочете видалити {len(spotisplit_playlists)} плейлістів? (yes/no): ")
    if confirm.lower() not in ['yes', 'y', 'так', 'т']:
        print("❌ Видалення скасовано")
        return
    
    # Видаляємо плейлісти
    deleted_count = 0
    for pl in spotisplit_playlists:
        try:
            sp.user_playlist_unfollow(user_id, pl["id"])
            print(f"🗑️ Видалено: {pl['name']}")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Помилка видалення '{pl['name']}': {e}")
    
    print(f"✅ Успішно видалено {deleted_count}/{len(spotisplit_playlists)} плейлістів")

def authenticate_spotify(config):
    """Spotify authentication logic"""
    # Перевіряємо налаштування
    if config["CLIENT_ID"] == "YOUR_CLIENT_ID":
        print("❌ Помилка: Не налаштовано CLIENT_ID")
        print("📝 Створіть Spotify Developer App та налаштуйте config.py")
        return None, None
    
    print(f"🎯 Кількість кластерів: {config['N_CLUSTERS']}")
    print(f"🔗 Джерело: {config['SOURCE_PLAYLIST_URL']}")
    
    # Налаштування Spotify API
    scopes = SPOTIFY_SCOPES.copy()
    if config["MAKE_PUBLIC"]:
        scopes.append("playlist-modify-public")

    os.environ["SPOTIPY_CLIENT_ID"] = config["CLIENT_ID"]
    os.environ["SPOTIPY_CLIENT_SECRET"] = config["CLIENT_SECRET"]
    os.environ["SPOTIPY_REDIRECT_URI"] = config["REDIRECT_URI"]

    try:
        auth_manager = SpotifyOAuth(scope=" ".join(scopes), show_dialog=True, cache_path=".cache-spotisplit", open_browser=True)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        me = sp.me()
        user_id = me["id"]
        print(f"✅ Увійшли як: {me['display_name']} ({user_id})")
        return sp, user_id
        
    except Exception as e:
        print(f"❌ Помилка авторизації: {e}")
        return None, None

def load_and_cluster_tracks(sp, config):
    """Load tracks and perform clustering"""
    try:
        # 1) Завантажуємо треки та audio features
        print("\n📥 Завантаження треків...")
        
        # Використовуємо Liked Songs замість плейліста
        print("🎧 Джерело: Liked Songs")
        items = get_all_liked_tracks(sp)
        track_ids = [it["track"]["id"] for it in items]
        features_map = fetch_audio_features(sp, track_ids)

        df = pd.DataFrame([track_row(it, features_map) for it in items])
        print(f"✅ Отримано {len(df)} треків з features.")

        # 2) Кластеризація
        print("\n🔍 Кластеризація...")
        X = df[FEATURE_COLUMNS].dropna().copy()
        valid_idx = X.index
        
        if len(X) < config["N_CLUSTERS"]:
            print(f"⚠️ Треків з валідними features менше, ніж N_CLUSTERS={config['N_CLUSTERS']}")
            config["N_CLUSTERS"] = max(1, len(X))

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=int(config["N_CLUSTERS"]), random_state=config["RANDOM_STATE"], n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        df["cluster"] = -1
        df.loc[valid_idx, "cluster"] = labels

        sil = None
        if int(config["N_CLUSTERS"]) > 1 and len(np.unique(labels)) > 1:
            sil = silhouette_score(X_scaled, labels)
        print(f"✅ Кластерів: {config['N_CLUSTERS']} | Silhouette: {sil:.3f}" if sil is not None else f"✅ Кластерів: {config['N_CLUSTERS']}")
        
        return df
        
    except Exception as e:
        print(f"❌ Помилка завантаження/кластеризації: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_playlists_from_clusters(sp, df, config, user_id):
    """Create playlists from clustering results"""
    try:
        # 3) Створення плейлістів
        print("\n📦 Створення плейлістів...")
        created = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        base_name = f"{config['PLAYLIST_NAME_PREFIX']}: Liked Songs"

        for c in sorted(df["cluster"].unique()):
            if c == -1:
                continue
            name = f"{base_name} · Cluster {int(c)} / {int(config['N_CLUSTERS'])}"
            desc = f"Створено SpotiSplit {timestamp}. Джерело: Liked Songs"
            pl_id = create_playlist(sp, user_id, name=name, description=desc, public=config["MAKE_PUBLIC"])
            created[int(c)] = pl_id
            cluster_uris = df.loc[df["cluster"] == c, "uri"].dropna().tolist()
            add_tracks_to_playlist(sp, pl_id, cluster_uris)
            print(f"📦 {name}: додано {len(cluster_uris)} треків")

        total_assigned = (df["cluster"] != -1).sum()
        print(f"\n🎉 Готово! Розкладено {total_assigned}/{len(df)} треків у {len(created)} плейлістів.")

        # 4) Експорт результатів
        out_csv = "spotisplit_clusters.csv"
        df.to_csv(out_csv, index=False)
        print(f"💾 Збережено результати: {out_csv}")
        
    except Exception as e:
        print(f"❌ Помилка створення плейлістів: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основна функція"""
    # Парсимо аргументи командного рядка
    parser = argparse.ArgumentParser(description="SpotiSplit MVP - Кластеризація Spotify плейлістів")
    parser.add_argument("--delete", action="store_true", help="Видалити всі плейлісти з 'SpotiSplit' в назві")
    parser.add_argument("--prefix", type=str, default="SpotiSplit", help="Префікс для пошуку плейлістів (за замовчуванням: SpotiSplit)")
    args = parser.parse_args()
    
    print("🎵 SpotiSplit MVP - Запуск...")
    
    # Завантажуємо конфігурацію
    config = load_config()
    
    # Аутентифікація Spotify
    sp, user_id = authenticate_spotify(config)
    if sp is None:
        return
    
    # Якщо передано --delete, видаляємо плейлісти та виходимо
    if args.delete:
        delete_spotisplit_playlists(sp, user_id, args.prefix)
        return
    
    # Завантаження та кластеризація треків
    df = load_and_cluster_tracks(sp, config)
    if df is None:
        return
    
    # Створення плейлістів з кластерів
    create_playlists_from_clusters(sp, df, config, user_id)

if __name__ == "__main__":
    main()
