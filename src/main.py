from polity_info.polity_formater import format_countries
from polity_info.polity_parser import parse_country

if __name__ == '__main__':
    countries = ['Canada', 'France', 'Italy']
    data = []
    for country in countries:
        data.append(parse_country(country))

    print(format_countries(countries, data))

