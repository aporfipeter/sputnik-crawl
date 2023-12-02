from datetime import date
from constants import phrases_to_remove, phrase_replace_map
import unidecode


def switch_out_ambiguous_characters(string_to_clean):
    clean_string = string_to_clean

    for phrase in list(phrase_replace_map.keys()):
        if phrase in string_to_clean:
            clean_string = clean_string.replace(phrase, phrase_replace_map[phrase])

    return clean_string


class TextPreparator:
    def __init__(self, location_codes):
        self.subject = "SputnikCrawl: Your Summary for "
        self.codes = location_codes

    # EMAIL TEXT METHODS
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

    # TEXT MANIPULATION METHODS
    def remove_phrase_from_title(self, title_string):
        for phrase_to_remove in phrases_to_remove:
            title_string = title_string.replace(phrase_to_remove, "")
        for country_code in self.codes.country_codes_2:
            title_string = title_string.replace(f"({country_code})", "")
        for country_code in self.codes.country_codes_3:
            title_string = title_string.replace(f"({country_code})", "")
        for us_state_combo in self.codes.us_state_combos:
            title_string = title_string.replace(f"({us_state_combo})", "")
        return title_string

    def prepare_entity_string_for_compare(self, entity_string):
        return_string = entity_string.lower()
        return_string = switch_out_ambiguous_characters(return_string)
        return_string = unidecode.unidecode(return_string)
        return_string = return_string.replace(" ", "")
        return return_string
