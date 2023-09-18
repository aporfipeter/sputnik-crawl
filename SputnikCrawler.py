from bs4 import BeautifulSoup
import requests


class SputnikCrawler:
    def __init__(self):
        self.base_url = "https://www.sputnikmusic.com/"
        self.sputnik_playlist_name = "Trending On Sputnik"

    def get_trending_albums_from_sputnik(self):
        res = requests.get(self.base_url)
        sputnik = res.text

        soup = BeautifulSoup(sputnik, "html.parser")

        albums = soup.select('a[href*="/album"]')
        trending_album_links = []

        for album in albums:
            album_link = album.get("href")
            if album_link[0:6] == "/album":
                trending_album_links.append(album_link)

        trending_album_links = trending_album_links[0:15]

        trending_albums = []

        for link in trending_album_links:
            album_res = requests.get(f"{self.base_url}{link}")
            album_res_text = album_res.text
            album_soup = BeautifulSoup(album_res_text, "html.parser")
            album_soup_array = album_soup.title.text.split()
            print(album_soup_array)

            if album_soup_array[0] == "Review:":
                album_soup_array.pop(0)
            album_soup_array.pop(-1)
            album_soup_array.pop(-1)
            clean_string = ' '.join(album_soup_array)

            clean_string = clean_string.replace("(album review )", "")
            clean_string = clean_string.replace("(album review 2)", "")
            clean_string = clean_string.replace("User Opinions", "")

            print(clean_string)

            artist_album = clean_string.split("-")
            artist_album[0] = artist_album[0].strip()
            artist_album[1] = artist_album[1].strip()

            artist_without_country = artist_album[0].split(" ")

            for index, word in enumerate(artist_without_country):
                print(f"{index}-{word}")
                if word[0] == "(" or word[-1] == ")":
                    artist_without_country.pop(index)

            artist_album[0] = ' '.join(artist_without_country).strip()

            for index, item in enumerate(artist_album):
                if "(" in item or ")" in item:
                    artist_album.pop(index)
            print(artist_album)

            trending_albums.append(artist_album)

        return trending_albums
