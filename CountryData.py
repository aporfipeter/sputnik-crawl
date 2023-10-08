import pycountry


class CountryData:
    def __init__(self):
        self.country_codes_2 = []
        self.country_codes_3 = []
        self.us_state_combos = []
        self.get_country_codes()
        self.get_us_state_combos()

    def get_country_codes(self):
        for country in list(pycountry.countries):
            self.country_codes_2.append(country.alpha_2)
            self.country_codes_3.append(country.alpha_3)

    def get_us_state_combos(self):
        for subdivision in list(pycountry.subdivisions):
            if subdivision.country_code == 'US':
                subdivision_code = subdivision.code
                self.us_state_combos.append(subdivision_code)
                subdivision_code_split = list(subdivision_code)
                subdivision_code_split.insert(2, "A")
                subdivision_code_amended = ''.join(subdivision_code_split)
                self.us_state_combos.append(subdivision_code_amended)
