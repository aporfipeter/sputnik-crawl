from SpotifyHandler import SpotifyHandler
from SputnikCrawler import SputnikCrawler
from EmailService import EmailService
from TextPreparator import TextPreparator
from CountryData import CountryData
import asyncio


async def main(test=False):
    country_data = CountryData()
    tp = TextPreparator(country_data)
    sputnik_crawler = SputnikCrawler(tp)
    spotify_handler = SpotifyHandler(tp)
    user_playlists = []

    spotify_current_user = spotify_handler.get_current_user_id()
    sputnik_playlist_name = sputnik_crawler.sputnik_playlist_name
    user_playlists = await spotify_handler.get_user_playlists()

    final_stats = {}

    def create_genre_to_album_map(album_map):
        genre_to_album_map = {}

        for album in album_map:
            for genre in album["tags"]:

                if genre not in genre_to_album_map.keys():
                    genre_to_album_map[genre] = []

                genre_to_album_map[genre].append({
                    "artist": album["artist"],
                    "album": album["album"],
                    "album_spotify_structure": album["album_spotify_structure"]
                })

        return genre_to_album_map

    def add_to_final_stats_map(playlist, artist, album):
        if not final_stats.get(playlist):
            final_stats[playlist] = []
        final_stats[playlist].append({
            "artist": artist,
            "album": album
        })

    def check_for_missing_albums(album_map):
        clean_album_map = []

        for album_dict in album_map:
            if "album_spotify_structure" in album_dict:
                clean_album_map.append(album_dict)
            else:
                print(f"Search result for album not available: {album_dict['artist']} - {album_dict['album']}"
                      f" - removing from list.")

        return clean_album_map

    # MAIN LOGIC
    if not test:
        sputnik_trending_albums = sputnik_crawler.get_trending_albums_from_sputnik()
        spotify_handler.search_trending_album_ids(sputnik_trending_albums)
        sputnik_trending_albums = check_for_missing_albums(sputnik_trending_albums)
        spotify_handler.search_tracks_from_trending_albums(sputnik_trending_albums)
        genre_map = create_genre_to_album_map(sputnik_trending_albums)

        # Adding to the main list
        sputnik_playlist_id = spotify_handler.check_for_playlist_id(sputnik_playlist_name, user_playlists)

        if sputnik_playlist_id is None:
            await spotify_handler.spotify_auth_oauth.user_playlist_create(user=spotify_current_user,
                                                                          name=sputnik_playlist_name)
            user_playlists = await spotify_handler.get_user_playlists()
            sputnik_playlist_id = spotify_handler.check_for_playlist_id(sputnik_playlist_name, user_playlists)
            user_playlists.append({
                "name": sputnik_playlist_name,
                "id": sputnik_playlist_id
            })
            print(f"Playlist Created: {sputnik_playlist_name} - Id: {sputnik_playlist_id}")

        print(f"Playlist Found: {sputnik_playlist_name} - Id: {sputnik_playlist_id}")
        sputnik_playlist_track_ids = await spotify_handler.get_tracks_from_playlist(sputnik_playlist_id)
        for album_object in sputnik_trending_albums:
            response = spotify_handler.add_tracks_to_playlist(sputnik_playlist_track_ids,
                                                              album_object["album_spotify_structure"],
                                                              sputnik_playlist_id)
            if response == 1:
                add_to_final_stats_map(sputnik_playlist_name, album_object["artist"], album_object["album"])

        # Handling genre-specific playlists:
        for genre_tag in list(genre_map.keys()):
            genre_playlist_name = f"{sputnik_crawler.genre_playlist_prefix}: {genre_tag}"
            genre_playlist_id = spotify_handler.check_for_playlist_id(genre_playlist_name, user_playlists)

            if genre_playlist_id is None:
                print(f"Playlist not found: {genre_playlist_name} - creating...")
                await spotify_handler.create_playlist_for_user(spotify_current_user,
                                                               genre_playlist_name)

                user_playlists = await spotify_handler.get_user_playlists()
                genre_playlist_id = spotify_handler.check_for_playlist_id(genre_playlist_name, user_playlists)

                user_playlists.append({
                    "name": genre_playlist_name,
                    "id": genre_playlist_id
                })
                print(f"Playlist Created: {genre_playlist_name} - Id: {genre_playlist_id}")

            print(f"Playlist Found: {genre_playlist_name} - Id: {genre_playlist_id}")
            genre_playlist_track_ids = await spotify_handler.get_tracks_from_playlist(genre_playlist_id)
            for genre_album_object in genre_map.get(genre_tag):
                response = spotify_handler.add_tracks_to_playlist(genre_playlist_track_ids,
                                                                  genre_album_object["album_spotify_structure"],
                                                                  genre_playlist_id)
                if response == 1:
                    add_to_final_stats_map(genre_playlist_name, genre_album_object["artist"],
                                           genre_album_object["album"])

        print("Final Map")
        print(final_stats)

        # if there are new albums, prepare the email and send it
        if len(final_stats) != 0:
            es = EmailService()
            subject = tp.set_subject()
            body = tp.prepare_email_text(final_stats)
            es.send_email(subject, body)
    else:
        print("Running test mode")
        collab_title = "Full of Hell and Nothing"
        print(tp.separate_collab_artists(collab_title))



if __name__ == "__main__":
    asyncio.run(main())
