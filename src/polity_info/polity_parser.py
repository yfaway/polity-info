import re
from collections import OrderedDict
import requests


def query(page: str) -> str:
    """ Queries the wikipedia page and returns the content. """

    url = "https://en.wikipedia.org/w/api.php"

    session = requests.Session()
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": page,
        "rvslots": "*",
        "rvprop": "content",
        "format": "json",
        "formatversion": "2"
    }

    response = session.get(url=url, params=params)
    json = response.json()

    return json["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]


def parse_country(country: str) -> OrderedDict:
    data = query(country)

    def integer_field(name: str):
        return [name, '([,\\d]+)']

    def decimal_number_field(name: str):
        return [name, '([.,\\d]+)']

    def rank_field(name: str):
        return [name, '([\\S]+)\\n']

    def change_indicator_field(name: str):
        return [name, '([\\S]+)\\n']

    def text_field(name: str):
        # Match all non-newline char until end of the line.
        return [name, '([^\\n]+)\\n']

    def dollar_field(name: str):
        return [name, '(?:\\{\\{increase\\}\\}){0,1}'
                      '(?:\\{\\{decrease\\}\\}){0,1}'
                      '\\s+\\$'
                      '([.,\\d]+'
                      '(?:&nbsp;){0,1}'
                      '(?:trillion){0,1}(?:billion){0,1}(?:million){0,1})']

    # ".*population_estimate\\s*=\\s*([,\\d]+)"]
    pattern_composites = [
        integer_field('area_km2'),
        rank_field('area_rank'),
        decimal_number_field('percent_water'),

        integer_field('population_estimate'),
        integer_field('population_estimate_year'),
        rank_field('population_estimate_rank'),
        integer_field('population_census'),
        integer_field('population_census_year'),
        decimal_number_field('population_density_km2'),
        rank_field('population_density_rank'),

        dollar_field('GDP_PPP'),
        integer_field('GDP_PPP_year'),
        rank_field('GDP_PPP_rank'),
        dollar_field('GDP_PPP_per_capita'),
        rank_field('GDP_PPP_per_capita_rank'),

        dollar_field('GDP_nominal'),
        integer_field('GDP_nominal_year'),
        rank_field('GDP_nominal_rank'),
        dollar_field('GDP_nominal_per_capita'),
        rank_field('GDP_nominal_per_capita_rank'),

        decimal_number_field('Gini'),
        integer_field('Gini_year'),
        change_indicator_field('Gini_change'),
        rank_field('Gini_rank'),

        decimal_number_field('HDI'),
        integer_field('HDI_year'),
        change_indicator_field('HDI_change'),
        rank_field('HDI_rank'),

        text_field('currency'),
        text_field('currency_code'),
        text_field('utc_offset'),
        text_field('date_format'),
        text_field('drives_on'),
        text_field('calling_code'),
        text_field('cctld'),
    ]

    result = OrderedDict()
    for composite in pattern_composites:
        key = composite[0]
        captured_pattern = composite[1]
        pattern = f".*{key}\\s*=\\s*{captured_pattern}"
        m = re.match(pattern, data, re.DOTALL)
        if m is not None:
            result[key] = m.group(1)
        else:
            result[key] = None

    return result
