from SpotifyHandler import SpotifyHandler
from SputnikCrawler import SputnikCrawler

sputnik_crawler = SputnikCrawler()
spotify_handler = SpotifyHandler()

spotify_current_user = spotify_handler.get_current_user_id()
sputnik_playlist_name = sputnik_crawler.sputnik_playlist_name
base_url = sputnik_crawler.base_url

# MAIN LOGIC
sputnik_trending_albums = sputnik_crawler.get_trending_albums_from_sputnik()
spotify_trending_album_ids = spotify_handler.search_trending_album_ids(sputnik_trending_albums)
spotify_trending_sputnik_tracks = spotify_handler.search_tracks_from_trending_albums(spotify_trending_album_ids)

sputnik_playlist_id = spotify_handler.check_for_sputnik_playlist(sputnik_playlist_name)

if sputnik_playlist_id is None:
    spotify_handler.spotify_auth_oauth.user_playlist_create(user=spotify_current_user, name=sputnik_playlist_name)
else:
    print(f"Playlist found! Id: {sputnik_playlist_id}")
    sputnik_playlist_track_ids = spotify_handler.get_tracks_from_playlist(sputnik_playlist_id)
    spotify_handler.add_tracks_to_playlist(sputnik_playlist_track_ids, spotify_trending_sputnik_tracks, sputnik_playlist_id)
