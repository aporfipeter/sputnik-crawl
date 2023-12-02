from bs4 import BeautifulSoup
import requests
import constants
import re


def get_band_page_link(album_page_response):
    band_link_list = album_page_response.select('a[href*="bands"]')
    band_page_link = []

    for link in band_link_list:
        band_page_link.append(link.get("href"))

    return band_page_link[0]


def get_release_date(page_soup):
    for search_pair in constants.release_year_search_pairs:
        all_found_tags = page_soup.find_all(search_pair["tag"])
        for found_tag in all_found_tags:
            clean_text = found_tag.text.replace("\n", "")
            found_matches = re.findall(search_pair["regex"], clean_text)
            if len(found_matches):
                if len(found_matches[search_pair["index_1"]]) == 4:
                    release_date = found_matches[search_pair["index_1"]]
                else:
                    release_date = found_matches[search_pair["index_1"]][search_pair["index_2"]]

                return release_date


class SputnikCrawler:
    def __init__(self, text_helper):
        self.base_url = "https://www.sputnikmusic.com/"
        self.sputnik_playlist_name = "Trending On Sputnik"
        self.genre_playlist_prefix = "TreOS"
        self.text_helper = text_helper

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
            album_release_year = get_release_date(album_soup)
            band_page_link = get_band_page_link(album_soup)
            band_tags = self.get_band_genre_tags(band_page_link)

            artist_album = self.process_album_page_title(album_soup)
            trending_albums.append({
                "artist": artist_album[0],
                "album": artist_album[1],
                "tags": band_tags,
                "release_year": album_release_year
            })

        return trending_albums

    def get_band_genre_tags(self, band_page_link):
        link = f"{self.base_url}{band_page_link}"
        res = requests.get(link)
        band_page_content = res.text
        band_page_soup = BeautifulSoup(band_page_content, "html.parser")
        tag_list = [tag.getText() for tag in band_page_soup.select('a[href*="/genre"]')]
        print(f"Genres: {tag_list}")
        return tag_list

    def process_album_page_title(self, album_page_response):

        page_title = album_page_response.title.text

        clean_string = self.text_helper.remove_phrase_from_title(page_title)

        print(clean_string)

        artist_album = clean_string.split(" - ")
        for i in range(len(artist_album)):
            artist_album[i] = artist_album[i].strip()
        # print(f"after stripping: {artist_album}")

        return artist_album
