import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import asyncio


class SpotifyHandler:
    def __init__(self):
        self.scope = "user-library-read user-library-modify playlist-modify-private playlist-modify-public"
        self.auth_manager = SpotifyClientCredentials()
        self.spotify_auth = self.authenticate_with_spotify()
        self.spotify_auth_oauth = self.authenticate_with_spotify_oauth()

    def authenticate_with_spotify(self):
        sp = spotipy.Spotify(auth_manager=self.auth_manager)
        return sp

    def authenticate_with_spotify_oauth(self):
        sp_auth = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        return sp_auth

    def get_current_user_id(self):
        return self.spotify_auth_oauth.current_user()["id"]

    def get_current_user_playlist(self):
        return self.spotify_auth_oauth.current_user_playlists()

    async def create_playlist_for_user(self, user_name, playlist_name ):
        self.spotify_auth_oauth.user_playlist_create(user=user_name, name=playlist_name)

    async def check_for_playlist_id(self, playlist_name):
        """
        Checks for the playlist to work on based on the playlist name provided.
        """
        playlists_res = self.get_current_user_playlist()
        user_playlists = []

        for playlist in playlists_res["items"]:
            user_playlists.append(
                {
                    "name": playlist["name"],
                    "id": playlist["id"]
                }
            )

        for playlist in user_playlists:
            if playlist["name"] == playlist_name:
                return playlist["id"]

    def search_trending_album_ids(self, albums):
        """
        Gets the list of crawled albums from Sputnik in the form of a map containing
        artist, album name and genres
        It inserts the album Spotify Ids into the input map for each album under the album_spotify_structure property.
        The property is a dict that will have the album id as the key and the list of track ids as value.
        This method only initializes the list.
        """

        print("Trending Albums")
        print(albums)

        for tr_album in albums:
            tr_limit = 10
            tr_offset = 0
            while tr_limit == 10:
                album_search = self.spotify_auth.search(q=tr_album["album"], type="album", offset=tr_offset)
                found_album_list = album_search["albums"]["items"]

                for sp_album in found_album_list:
                    """
                    print(sp_album["name"])
                    print(sp_album["artists"][0]["name"])
                    print(tr_album[1])
                    print(tr_album[0])
                    """
                    if sp_album["artists"][0]["name"].lower() == tr_album["artist"].lower():
                        # trending_album_ids.append(sp_album["id"])
                        tr_album["album_spotify_structure"] = {sp_album["id"]: []}
                        tr_limit += 1
                        break

                tr_offset += len(found_album_list)
                if tr_limit == 10:
                    tr_limit = len(found_album_list)

    def search_tracks_from_trending_albums(self, albums):
        """
        Gets the list of album objects that contain the album id.
        It appends the album tracks to the array value that's key is the album id
        """

        if albums:
            for trending_album in albums:
                trending_album_id = list(trending_album["album_spotify_structure"].keys())[0]
                album_tracks = self.spotify_auth.album_tracks(trending_album_id)["items"]
                for track in album_tracks:
                    trending_album["album_spotify_structure"].get(trending_album_id).append(track["id"])
        else:
            print("No album ids were passed.")

    async def get_tracks_from_playlist(self, playlist_id):
        """
        Gets the playlist id as input
        It queries the tracks already added to the playlist by batches of 100.
        It returns the list of track ids from the playlist
        """

        sputnik_tracks = []
        sputnik_tracks_offset = 0
        sputnik_limit = 100
        sputnik_track_ids = []

        while sputnik_limit == 100:
            sputnik_tracks_res = self.spotify_auth.playlist_items(playlist_id=playlist_id,
                                                                  offset=sputnik_tracks_offset)
            for tr in sputnik_tracks_res["items"]:
                sputnik_tracks.append(tr)
            sputnik_tracks_offset += len(sputnik_tracks_res["items"])
            if len(sputnik_tracks_res["items"]) != 100:
                sputnik_limit = len(sputnik_tracks_res["items"])

        for tr in sputnik_tracks:
            sputnik_track_ids.append(tr["track"]["id"])

        return sputnik_track_ids

    def add_tracks_to_playlist(self, playlist_track_ids, trending_album_to_track_id_map, playlist_id):
        """
        Gets the list of track ids already on the playlist, the dict of album track ids to album ids to add and the playlist id.
        It loops over the dict and checks if any of the tracks are already on the playlist based on track ids.
        If the track is not in the provided playlist, it gets added.
        """

        for album in trending_album_to_track_id_map:
            tracks_to_add = []

            for trending_track_id in trending_album_to_track_id_map[album]:
                if trending_track_id not in playlist_track_ids:
                    tracks_to_add.append(trending_track_id)

            if len(tracks_to_add):
                self.spotify_auth_oauth.playlist_add_items(playlist_id, tracks_to_add, 0)
