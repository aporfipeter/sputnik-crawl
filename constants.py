phrases_to_remove = [
    "(album review )",
    "(album review 2)",
    "User Opinions",
    "Review: ",
    "|",
    "Sputnikmusic",
    " - sputnikmusic"
]

phrase_replace_map = {
    "&": "and"
}

release_year_search_pairs = [
    {"tag": "p", "regex": r"(\d{2})\/(\d{2})\/(\d{4})", "index_1": 0, "index_2": 2 },
    {"tag": "b", "regex": r"(\d{4})", "index_1": 0, "index_2": None}
]

collab_phrases = ["and", "/"]
