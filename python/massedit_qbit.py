ls
import qbittorrentapi
import sys

# --- CONFIGURATION ---
conn_info = dict(
    host='http://0.0.0.0:8080',
    username='username',
    password='password'
)

# The specific tracker URL you want to find and remove
old_tracker_url = "http://old.tracker.url/announce"

# The new tracker URL to put in its place
new_tracker_url = "http://new.tracker.url/announce"

# Initialize Client
qb = qbittorrentapi.Client(**conn_info)

# Attempt to log in
try:
    qb.auth_log_in()
    print(f"Logged in to qBittorrent: {qb.app.version}")
except qbittorrentapi.LoginFailed as e:
    print(f"Connection error: {e}")
    sys.exit(1)

# Retrieve the list of all torrents
try:
    torrents = qb.torrents_info()
except qbittorrentapi.APIError as e:
    print(f"Error retrieving torrents: {e}")
    qb.auth_log_out()
    sys.exit(1)

# Initialize counters
total_count = len(torrents)
changed_count = 0
found_count = 0

print(f"Scanning {total_count} torrents for tracker: {old_tracker_url}...\n")

# Iterate over each torrent
for torrent in torrents:
    try:
        # Get the list of trackers for the current torrent
        trackers = qb.torrents_trackers(torrent.hash)
        
        for tracker in trackers:
            # Check if the current tracker matches the OLD tracker we want to replace
            if tracker.url == old_tracker_url:
                found_count += 1
                print(f"Match found in: {torrent.name}")
                
                try:
                    # Execute the replacement
                    qb.torrents_edit_tracker(
                        torrent_hash=torrent.hash, 
                        original_url=old_tracker_url, 
                        new_url=new_tracker_url
                    )
                    print(f"  SUCCESS: Replaced '{old_tracker_url}' with '{new_tracker_url}'")
                    changed_count += 1
                except qbittorrentapi.APIError as e:
                    print(f"  FAILED to edit tracker: {e}")

    except qbittorrentapi.APIError as e:
        print(f"Error processing torrent {torrent.name}: {e}")

# Display summary
print("-" * 30)
print(f"Total torrents scanned: {total_count}")
print(f"Matches found: {found_count}")
print(f"Trackers replaced: {changed_count}")

# Log out
qb.auth_log_out()