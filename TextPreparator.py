from datetime import date


class TextPreparator:
    def __init__(self):
        self.subject = "SputnikCrawl: Your Summary for "

    def set_subject(self):
        today = date.today()
        return self.subject + str(today)

    def prepare_email_text(self, final_map):
        introduction = "Here is your summary of additions for today.\n"
        introduction2 = "The albums were added to the following playlists:\n"
        text = introduction + introduction2

        for playlist in final_map:
            text += "\n" + playlist + "\n"
            for album in final_map[playlist]:
                text += f"-{album['artist']}: {album['album']}\n"

        text += "\nHappy Listening!"

        return text
