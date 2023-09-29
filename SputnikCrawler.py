from bs4 import BeautifulSoup
import requests


def process_album_page_title(album_page_response):
    album_soup_array = album_page_response.title.text.split()
    # print(album_soup_array)

    if album_soup_array[0] == "Review:":
        album_soup_array.pop(0)
    album_soup_array.pop(-1)
    album_soup_array.pop(-1)
    clean_string = ' '.join(album_soup_array)

    clean_string = clean_string.replace("(album review )", "")
    clean_string = clean_string.replace("(album review 2)", "")
    clean_string = clean_string.replace("User Opinions", "")

    # print(clean_string)

    artist_album = clean_string.split("-")
    artist_album[0] = artist_album[0].strip()
    artist_album[1] = artist_album[1].strip()

    artist_without_country = artist_album[0].split(" ")

    for index, word in enumerate(artist_without_country):
        # print(f"{index}-{word}")
        if word[0] == "(" or word[-1] == ")":
            artist_without_country.pop(index)

    artist_album[0] = ' '.join(artist_without_country).strip()

    for index, item in enumerate(artist_album):
        if "(" in item or ")" in item:
            artist_album.pop(index)
    print(artist_album)
    return artist_album


def get_band_page_link(album_page_response):
    band_link_list = album_page_response.select('a[href*="bands"]')
    band_page_link = []

    for link in band_link_list:
        band_page_link.append(link.get("href"))

    return band_page_link[0]


class SputnikCrawler:
    def __init__(self):
        self.base_url = "https://www.sputnikmusic.com/"
        self.sputnik_playlist_name = "Trending On Sputnik"
        self.genre_playlist_prefix = "TreOS"

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
            band_page_link = get_band_page_link(album_soup)
            band_tags = self.get_band_genre_tags(band_page_link)

            artist_album = process_album_page_title(album_soup)
            trending_albums.append({
                "artist": artist_album[0],
                "album": artist_album[1],
                "tags": band_tags
            })

        return trending_albums

    def get_band_genre_tags(self, band_page_link):
        link = f"{self.base_url}{band_page_link}"
        res = requests.get(link)
        band_page_content = res.text
        band_page_soup = BeautifulSoup(band_page_content, "html.parser")
        tag_list = [tag.getText() for tag in band_page_soup.select('a[href*="/genre"]')]
        print(tag_list)
        return tag_list



