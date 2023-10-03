from SpotifyHandler import SpotifyHandler
from SputnikCrawler import SputnikCrawler
from EmailService import EmailService
from TextPreparator import TextPreparator
import asyncio


async def main():
    sputnik_crawler = SputnikCrawler()
    spotify_handler = SpotifyHandler()

    spotify_current_user = spotify_handler.get_current_user_id()
    sputnik_playlist_name = sputnik_crawler.sputnik_playlist_name

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
                else:
                    genre_to_album_map[genre].append({
                        "artist": album["artist"],
                        "album": album["album"],
                        "album_spotify_structure": album["album_spotify_structure"]
                    })
        # print(genre_to_album_map)
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
                print(f"Album not found: {album_dict['artist']} - {album_dict['album']}")

        return clean_album_map

    # MAIN LOGIC
    sputnik_trending_albums = sputnik_crawler.get_trending_albums_from_sputnik()
    spotify_handler.search_trending_album_ids(sputnik_trending_albums)
    sputnik_trending_albums = check_for_missing_albums(sputnik_trending_albums)
    spotify_handler.search_tracks_from_trending_albums(sputnik_trending_albums)
    genre_map = create_genre_to_album_map(sputnik_trending_albums)

    # Adding to the main list
    sputnik_playlist_id = await spotify_handler.check_for_playlist_id(sputnik_playlist_name)

    if sputnik_playlist_id is None:
        await spotify_handler.spotify_auth_oauth.user_playlist_create(user=spotify_current_user,
                                                                      name=sputnik_playlist_name)
        sputnik_playlist_id = await spotify_handler.check_for_playlist_id(sputnik_playlist_name)
        print(f"Playlist created: {sputnik_playlist_name}")

    print(f"Playlist found! Id: {sputnik_playlist_id}")
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
        genre_playlist_id = await spotify_handler.check_for_playlist_id(genre_playlist_name)

        if genre_playlist_id is None:
            await spotify_handler.create_playlist_for_user(spotify_current_user, genre_playlist_name)
            genre_playlist_id = await spotify_handler.check_for_playlist_id(genre_playlist_name)
            print(f"Playlist created: {genre_playlist_name}")

        print(f"Playlist found! Id: {genre_playlist_id}")
        genre_playlist_track_ids = await spotify_handler.get_tracks_from_playlist(genre_playlist_id)
        for genre_album_object in genre_map.get(genre_tag):
            response = spotify_handler.add_tracks_to_playlist(genre_playlist_track_ids,
                                                              genre_album_object["album_spotify_structure"],
                                                              genre_playlist_id)
            if response == 1:
                add_to_final_stats_map(genre_playlist_name, genre_album_object["artist"], genre_album_object["album"])

    print("Final Map")
    print(final_stats)

    # if there are new albums, prepare the email and send it
    if len(final_stats) != 0:
        tp = TextPreparator()
        es = EmailService()
        subject = tp.set_subject()
        body = tp.prepare_email_text(final_stats)
        es.send_email(subject, body)


if __name__ == "__main__":
    asyncio.run(main())
