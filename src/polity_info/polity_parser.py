import re
from collections import OrderedDict
import requests
from io import StringIO
from html.parser import HTMLParser


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
        return [name, '[\\D]*([,\\d]+)']

    def decimal_number_field(name: str):
        return [name, '([.,\\d]+)']

    def rank_field(name: str):
        return [name, '(\\w+).*\\n']

    def change_indicator_field(name: str):
        return [name, r'([\S]+)\n']

    def text_field(name: str):
        # Match all non-newline char until end of the line.
        return [name, r'([^\n]+)\n']

    def dollar_field(name: str):
        return [name, '[\\D]*'
                      '([.,\\d]+'
                      '(?:&nbsp;){0,1}'
                      '(?:\\{\\{nbsp\\}\\}){0,1}'
                      '\\s*'
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
            result[key] = _format_value(m.group(1))
        else:
            result[key] = None

    return result


def _format_value(text: str) -> str:
    """" Remove HTML tag, comment tag, and some Wikimedia specific tags. """
    text = strip_html_tags(text)
    text = text.replace("{{nbsp}}", ' ')

    # replace wiki link in the format '[[Link|Label]]' with just 'Label'
    pattern = re.compile(r'(.*)\[\[.*\|([.*]]+)\]\](.*)')
    while pattern.match(text):
        text = pattern.sub(r"\1\2\3", text)

    # replace wiki link in the format '[[Label]]' with just 'Label'
    pattern = re.compile(r'(.*)\[\[(.*)\]\](.*)')
    while pattern.match(text):
        text = pattern.sub(r"\1\2\3", text)

    return text


class MLStripper(HTMLParser):
    """ @see https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

