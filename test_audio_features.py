#!/usr/bin/env python3
"""
Test script to debug Spotify audio features access
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set environment variables
os.environ["SPOTIPY_CLIENT_ID"] = "b7b8c75ab68d4397be30272f2e678090"
os.environ["SPOTIPY_CLIENT_SECRET"] = "05457f6d857249328e4cb3be02c58df9"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:4000/callback"

# Try different scope combinations
SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative", 
    "playlist-modify-private",
    "user-library-read",
    "user-read-private",
    "user-read-email",
]

print("Testing with scopes:", " ".join(SCOPES))

auth_manager = SpotifyOAuth(
    scope=" ".join(SCOPES), 
    show_dialog=True, 
    cache_path=".cache-spotisplit",
    open_browser=True
)

sp = spotipy.Spotify(auth_manager=auth_manager)

# Test 1: Get user info
print("\nTesting user access...")
try:
    me = sp.me()
    print(f"✅ User: {me['display_name']} ({me['id']})")
except Exception as e:
    print(f"❌ User access error: {e}")

# Test 2: Get liked tracks
print("\nTesting liked tracks access...")
try:
    results = sp.current_user_saved_tracks(limit=5)
    tracks = results.get("items", [])
    print(f"✅ Got {len(tracks)} liked tracks")
    
    if tracks:
        track_id = tracks[0]["track"]["id"]
        track_name = tracks[0]["track"]["name"]
        artist = tracks[0]["track"]["artists"][0]["name"]
        print(f"First track: {track_name} by {artist}")
        print(f"Track ID: {track_id}")
        
        # Test 3: Try to get basic track info
        print(f"\nTesting basic track info for: {track_name}")
        try:
            track_info = sp.track(track_id)
            print(f"✅ Track info: {track_info['name']} by {track_info['artists'][0]['name']}")
            print(f"   Popularity: {track_info.get('popularity', 'N/A')}")
            print(f"   Duration: {track_info.get('duration_ms', 'N/A')} ms")
        except Exception as e:
            print(f"❌ Track info error: {e}")
        
        # Test 4: Try to get audio features with different method
        print(f"\nTesting audio features for: {track_name}")
        try:
            # Try the direct method
            features = sp.audio_features([track_id])
            if features and features[0]:
                print(f"✅ Audio features: {features[0]}")
            else:
                print("❌ No audio features returned")
        except Exception as e:
            print(f"❌ Audio features error: {e}")
            
        # Test 5: Try to get audio analysis (different endpoint)
        print(f"\nTesting audio analysis for: {track_name}")
        try:
            analysis = sp.audio_analysis(track_id)
            if analysis:
                print(f"✅ Audio analysis: {len(analysis)} sections")
            else:
                print("❌ No audio analysis returned")
        except Exception as e:
            print(f"❌ Audio analysis error: {e}")
            
except Exception as e:
    print(f"❌ Liked tracks error: {e}")

# Test 6: Try to get audio features for a known public track
print("\nTesting audio features for a known public track...")
try:
    # Use a well-known track ID (Billie Jean by Michael Jackson)
    public_track_id = "5ChkMS8OtdzJeqyybCc9R5"
    features = sp.audio_features([public_track_id])
    if features and features[0]:
        print(f"✅ Public track audio features: {features[0]}")
    else:
        print("❌ No public track audio features returned")
except Exception as e:
    print(f"❌ Public track audio features error: {e}")

# Test 7: Check what scopes we actually have
print("\nChecking actual scopes...")
try:
    # Try to get the current token info
    token_info = auth_manager.get_cached_token()
    if token_info:
        print(f"✅ Cached token scopes: {token_info.get('scope', 'No scope info')}")
    else:
        print("❌ No cached token")
except Exception as e:
    print(f"❌ Token info error: {e}")

# Test 8: Try to get recommendations (this uses audio features internally)
print("\nTesting recommendations (uses audio features)...")
try:
    # Get recommendations based on a seed track
    recommendations = sp.recommendations(seed_tracks=[track_id], limit=1)
    if recommendations and recommendations.get('tracks'):
        print(f"✅ Got recommendations: {recommendations['tracks'][0]['name']}")
    else:
        print("❌ No recommendations returned")
except Exception as e:
    print(f"❌ Recommendations error: {e}")

# Test 9: Check app configuration
print("\nChecking app configuration...")
try:
    # Try to get the app's client credentials
    client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"]
    )
    sp_public = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Try to get audio features with client credentials
    features = sp_public.audio_features([public_track_id])
    if features and features[0]:
        print(f"✅ Client credentials audio features: {features[0]}")
    else:
        print("❌ No client credentials audio features")
except Exception as e:
    print(f"❌ Client credentials error: {e}")
