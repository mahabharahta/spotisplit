#!/usr/bin/env python3
"""
SpotiSplit MVP - Версія без audio features
Використовує базову інформацію про треки для кластеризації
"""

import os
import sys
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

def track_row(item):
    """Створює рядок даних для треку без audio features"""
    t = item["track"]
    return {
        "track_id": t["id"],
        "track_name": t["name"],
        "artist": ", ".join([a["name"] for a in t["artists"]]),
        "album": t["album"]["name"] if t.get("album") else None,
        "added_at": item.get("added_at"),
        "duration_ms": t.get("duration_ms", 0),
        "popularity": t.get("popularity", 0),
        "explicit": t.get("explicit", False),
        "uri": t.get("uri"),
        "external_url": t.get("external_urls", {}).get("spotify"),
        "release_date": t.get("album", {}).get("release_date") if t.get("album") else None,
        "album_type": t.get("album", {}).get("album_type") if t.get("album") else None,
        "is_local": t.get("is_local", False),
        "track_number": t.get("track_number"),
        "disc_number": t.get("disc_number"),
        "available_markets": len(t.get("available_markets", [])),
    }

def create_playlist(sp, user_id: str, name: str, description: str = "", public: bool = False) -> str:
    """Створює новий плейліст"""
    try:
        result = sp.user_playlist_create(
            user_id, name, description=description, public=public
        )
        return result["id"]
    except Exception as e:
        print(f"❌ Помилка створення плейліста: {e}")
        return None

def add_tracks_to_playlist(sp, playlist_id: str, track_uris: List[str]):
    """Додає треки до плейліста"""
    try:
        for chunk in batched(track_uris, 100):
            sp.playlist_add_items(playlist_id, chunk)
    except Exception as e:
        print(f"❌ Помилка додавання треків: {e}")

# Constants
SPOTIFY_SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative", 
    "playlist-modify-private",
    "user-library-read",  # Для доступу до Liked Songs
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
        auth_manager = SpotifyOAuth(scope=" ".join(scopes), show_dialog=True, cache_path=".cache-spotisplit-no-audio")
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
        # 1) Завантажуємо треки
        print("\n📥 Завантаження треків...")
        print("🎧 Джерело: Liked Songs")
        items = get_all_liked_tracks(sp)
        
        df = pd.DataFrame([track_row(it) for it in items])
        print(f"✅ Отримано {len(df)} треків.")

        # 2) Підготовка даних для кластеризації
        print("\n🔍 Підготовка даних для кластеризації...")
        
        # Створюємо розширені числові характеристики для 20-вимірного простору
        print("🔧 Створення розширених характеристик...")
        
        # Базові числові характеристики
        df["explicit"] = df["explicit"].astype(int)
        df["is_local"] = df["is_local"].astype(int)
        
        # Заповнюємо відсутні значення
        df = df.fillna(0)
        
        # Створюємо додаткові характеристики
        df["duration_minutes"] = df["duration_ms"] / 60000
        df["popularity_normalized"] = df["popularity"] / 100.0
        df["track_position_ratio"] = df["track_number"] / df["disc_number"].replace(0, 1)
        df["market_coverage"] = df["available_markets"] / 100.0  # Нормалізуємо кількість ринків
        
        # Створюємо часові характеристики з release_date
        df["release_year"] = pd.to_datetime(df["release_date"], errors='coerce').dt.year.fillna(2024)
        df["age_years"] = 2024 - df["release_year"]
        df["age_normalized"] = df["age_years"] / 50.0  # Нормалізуємо вік треку
        
        # Створюємо розмірні характеристики
        df["album_type_numeric"] = df["album_type"].map({
            'album': 3, 'single': 1, 'compilation': 2, 'ep': 1.5
        }).fillna(1)
        
        # Використовуємо всі доступні характеристики для 20-вимірного простору
        feature_cols = [
            "duration_minutes", "popularity_normalized", "explicit", "is_local",
            "track_position_ratio", "market_coverage", "age_normalized", 
            "album_type_numeric", "track_number", "disc_number", "available_markets",
            "duration_ms", "popularity", "release_year", "age_years"
        ]
        
        # Додаємо взаємодії між характеристиками для розширення простору
        df["popularity_duration"] = df["popularity_normalized"] * df["duration_minutes"]
        df["age_popularity"] = df["age_normalized"] * df["popularity_normalized"]
        df["explicit_popularity"] = df["explicit"] * df["popularity_normalized"]
        df["market_popularity"] = df["market_coverage"] * df["popularity_normalized"]
        df["duration_age"] = df["duration_minutes"] * df["age_normalized"]
        
        # Оновлюємо список характеристик
        feature_cols = [
            "duration_minutes", "popularity_normalized", "explicit", "is_local",
            "track_position_ratio", "market_coverage", "age_normalized", 
            "album_type_numeric", "track_number", "disc_number", "available_markets",
            "duration_ms", "popularity", "release_year", "age_years",
            "popularity_duration", "age_popularity", "explicit_popularity", 
            "market_popularity", "duration_age"
        ]
        
        print(f"📊 Використовуємо {len(feature_cols)} характеристик для кластеризації")
        
        X = df[feature_cols].copy()
        
        if len(X) < config["N_CLUSTERS"]:
            print(f"⚠️ Треків менше, ніж N_CLUSTERS={config['N_CLUSTERS']}")
            config["N_CLUSTERS"] = max(1, len(X))

        # Нормалізація даних
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # 3) Кластеризація
        print("\n🔍 Кластеризація...")
        kmeans = KMeans(n_clusters=int(config["N_CLUSTERS"]), random_state=config["RANDOM_STATE"], n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        df["cluster"] = labels

        # Оцінка якості кластеризації
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
        # 4) Аналіз кластерів
        print("\n📊 Аналіз кластерів...")
        print("=" * 80)
        
        for c in sorted(df["cluster"].unique()):
            cluster_df = df[df["cluster"] == c]
            print(f"\n🎯 Кластер {c}: {len(cluster_df)} треків")
            print("-" * 40)
            
            # Базові статистики
            print(f"📈 Популярність: {cluster_df['popularity'].mean():.1f} ± {cluster_df['popularity'].std():.1f}")
            print(f"⏱️  Тривалість: {cluster_df['duration_minutes'].mean():.1f} хв ± {cluster_df['duration_minutes'].std():.1f}")
            print(f"📅 Вік треків: {cluster_df['age_years'].mean():.1f} років ± {cluster_df['age_years'].std():.1f}")
            
            # Явний контент
            explicit_count = cluster_df['explicit'].sum()
            explicit_pct = (explicit_count / len(cluster_df)) * 100
            print(f"🔞 Явний контент: {explicit_count}/{len(cluster_df)} ({explicit_pct:.1f}%)")
            
            # Локальні треки
            local_count = cluster_df['is_local'].sum()
            local_pct = (local_count / len(cluster_df)) * 100
            print(f"🏠 Локальні треки: {local_count}/{len(cluster_df)} ({local_pct:.1f}%)")
            
            # Ринкове покриття
            avg_markets = cluster_df['available_markets'].mean()
            print(f"🌍 Середнє ринкове покриття: {avg_markets:.0f} ринків")
            
            # Тип альбому
            album_types = cluster_df['album_type'].value_counts()
            main_type = album_types.index[0] if len(album_types) > 0 else "unknown"
            main_count = album_types.iloc[0] if len(album_types) > 0 else 0
            print(f"💿 Основний тип: {main_type} ({main_count}/{len(cluster_df)})")
            
            # Топ треки за популярністю
            top_tracks = cluster_df.nlargest(3, 'popularity')[['track_name', 'artist', 'popularity']]
            print("🎵 Топ треки:")
            for _, track in top_tracks.iterrows():
                print(f"   • {track['track_name']} - {track['artist']} (популярність: {track['popularity']:.0f})")
        
        # 5) Створення плейлістів
        print("\n📦 Створення плейлістів...")
        created = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        base_name = f"{config['PLAYLIST_NAME_PREFIX']}: Liked Songs (No Audio)"

        for c in sorted(df["cluster"].unique()):
            name = f"{base_name} · Cluster {int(c)} / {int(config['N_CLUSTERS'])}"
            desc = f"Створено SpotiSplit {timestamp}. Джерело: Liked Songs (без audio features)"
            pl_id = create_playlist(sp, user_id, name=name, description=desc, public=config["MAKE_PUBLIC"])
            if pl_id:
                created[int(c)] = pl_id
                cluster_uris = df.loc[df["cluster"] == c, "uri"].dropna().tolist()
                add_tracks_to_playlist(sp, pl_id, cluster_uris)
                print(f"📦 {name}: додано {len(cluster_uris)} треків")

        total_assigned = len(df)
        print(f"\n🎉 Готово! Розкладено {total_assigned}/{len(df)} треків у {len(created)} плейлістів.")

        # 6) Експорт результатів
        out_csv = "spotisplit_clusters_no_audio.csv"
        df.to_csv(out_csv, index=False)
        print(f"💾 Збережено результати: {out_csv}")
        
    except Exception as e:
        print(f"❌ Помилка створення плейлістів: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основна функція"""
    # Парсимо аргументи командного рядка
    parser = argparse.ArgumentParser(description="SpotiSplit MVP - Кластеризація Spotify плейлістів (без audio features)")
    parser.add_argument("--delete", action="store_true", help="Видалити всі плейлісти з 'SpotiSplit' в назві")
    parser.add_argument("--prefix", type=str, default="SpotiSplit", help="Префікс для пошуку плейлістів (за замовчуванням: SpotiSplit)")
    args = parser.parse_args()
    
    print("🎵 SpotiSplit MVP - Версія без audio features")
    print("Використовує базову інформацію про треки для кластеризації")
    
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
