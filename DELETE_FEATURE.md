# 🗑️ SpotiSplit Delete Feature

## Overview

The delete feature allows you to easily remove all playlists created by SpotiSplit that contain a specific prefix in their name. This is useful for cleaning up after testing or when you want to start fresh with new clustering.

## Usage

### Basic Delete Command

```bash
# Delete all playlists with "SpotiSplit" in the name (default)
python run_spotisplit.py --delete

# Delete all playlists with "SpotiSplit" in the name (no-audio version)
python run_spotisplit_no_audio.py --delete
```

### Custom Prefix Delete

```bash
# Delete playlists with custom prefix
python run_spotisplit.py --delete --prefix "MyPrefix"

# Delete playlists with custom prefix (no-audio version)
python run_spotisplit_no_audio.py --delete --prefix "MyPrefix"
```

### Command Line Options

- `--delete`: Enable delete mode (required)
- `--prefix PREFIX`: Custom prefix to search for (default: "SpotiSplit")
- `--help`: Show help message

## How It Works

1. **Authentication**: The script authenticates with Spotify using your credentials
2. **Playlist Discovery**: Searches through all your playlists to find ones matching the prefix
3. **Confirmation**: Shows you exactly which playlists will be deleted and asks for confirmation
4. **Deletion**: Removes each playlist one by one, providing progress feedback
5. **Summary**: Reports how many playlists were successfully deleted

## Safety Features

- **Confirmation Required**: You must type "yes" (or "y", "так", "т") to confirm deletion
- **Preview**: Shows all playlists that will be deleted before asking for confirmation
- **Error Handling**: Continues deletion even if some playlists fail to delete
- **Progress Tracking**: Shows real-time progress of deletion process

## Example Output

```
🗑️ Пошук плейлістів з 'SpotiSplit' в назві...
🔍 Знайдено 45 плейлістів для видалення:
   • SpotiSplit: Liked Songs (No Audio) · Cluster 19 / 20 (ID: 4Qvd4rdD5251joEqmvAnlB)
   • SpotiSplit: Liked Songs (No Audio) · Cluster 18 / 20 (ID: 4dDLG6PNnamdlPzKLgPZ5L)
   ...

⚠️ Ви впевнені, що хочете видалити 45 плейлістів? (yes/no): yes
🗑️ Видалено: SpotiSplit: Liked Songs (No Audio) · Cluster 19 / 20
🗑️ Видалено: SpotiSplit: Liked Songs (No Audio) · Cluster 18 / 20
...
✅ Успішно видалено 45/45 плейлістів
```

## ⚠️ Important Notes

- **Irreversible**: Deleted playlists cannot be recovered
- **All Matching Playlists**: Deletes ALL playlists containing the specified prefix
- **Case Insensitive**: Search is case-insensitive (e.g., "spotisplit" will match "SpotiSplit")
- **Requires Authentication**: You must be logged into Spotify to use this feature

## Use Cases

- **Testing**: Clean up playlists after testing different clustering parameters
- **Fresh Start**: Remove old clusters before creating new ones
- **Cleanup**: Remove playlists created with different prefixes
- **Maintenance**: Regular cleanup of old clustering results

## Troubleshooting

### No Playlists Found
If you see "Плейлісти з 'X' в назві не знайдено", it means:
- No playlists exist with that prefix
- The prefix is misspelled
- You don't have access to those playlists

### Authentication Errors
If you get authentication errors:
- Make sure your Spotify credentials are correct in `config.py`
- Try running the normal clustering script first to refresh authentication
- Check that your Spotify app has the necessary permissions

### Partial Deletion
If some playlists fail to delete:
- The script will continue with the remaining playlists
- Check the error messages for specific issues
- You may need to manually delete problematic playlists
