import re
from collections import OrderedDict
from typing import Any, Union, Callable

import requests
from io import StringIO
from html.parser import HTMLParser


def no_op_formatter(value: str) -> str:
    """ Returns the parameter value as is. """
    return value


def number_formatter(value: str) -> Union[int, float]:
    """
    Formats the given string to remove any ',' character and convert it to an integer or a float depending on if a
    comma exists.
    """
    value = value.replace(",", "")

    if value.find(".") != -1:
        return float(value)
    else:
        return int(value)


def no_op_greater_than_function(left: Any, right: Any) -> bool:
    if right is None:
        return True

    if left is None:
        return False

    return False


def number_greater_than_function(left: Any, right: Any) -> bool:
    """ Returns true if right is smaller than left. """
    if right is None:
        return True

    if left is None:
        return False

    return right < left


class Value:
    """
    Represents a value. Support the greater than (gt) comparison function.
    """

    def __init__(self, value: Any,
                 greater_than_function: Callable[["Value", "Value"], bool] = no_op_greater_than_function) -> None:
        self.value = value
        self._greater_than_function = greater_than_function

    def __gt__(self, other: "Value"):
        return self._greater_than_function(self.value, other.value)


class Field:
    """
    Contains information about a field including its name, extracting regular expression, and its post-extraction
    transformation.
    The 'format' function creates a Value by first formatting it and then wrap it in a object that also contains the
    greater-than function.
    """

    def __init__(self, key: str,
                 pattern: str,
                 formatter: Callable[[str], Any] = no_op_formatter,
                 greater_than_function: Callable[[Any, Any], bool] = no_op_greater_than_function) -> None:
        """
        Creates a new field
        :param key: the name of the field
        :param pattern: the regular expression to extract the data
        :param formatter: the function to format the value string into a concrete type
        """
        self.key = key
        self.pattern = pattern
        self._formatter = formatter
        self._greater_than_function = greater_than_function

    def format(self, value: str) -> Value:
        if value is None:
            return Value(None, self._greater_than_function)
        else:
            return Value(self._formatter(value), self._greater_than_function)


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

    def integer_field(name: str) -> Field:
        return Field(name, '[\\D]*([,\\d]+)', number_formatter, number_greater_than_function)

    def decimal_number_field(name: str) -> Field:
        return Field(name, '([.,\\d]+)', number_formatter, number_greater_than_function)

    def rank_field(name: str) -> Field:
        return Field(name, '(\\w+).*\\n')

    def change_indicator_field(name: str) -> Field:
        return Field(name, r'([\S]+)\n')

    def text_field(name: str) -> Field:
        # Match all non-newline char until end of the line.
        return Field(name, r'([^\n]+)\n')

    def dollar_field(name: str) -> Field:
        return Field(name,
                     '[\\D]*'
                     '([.,\\d]+'
                     '(?:&nbsp;){0,1}'
                     '(?:\\{\\{nbsp\\}\\}){0,1}'
                     '\\s*'
                     '(?:trillion){0,1}(?:billion){0,1}(?:million){0,1})',
                     no_op_formatter,
                     number_greater_than_function)

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
    for field in pattern_composites:
        pattern = f".*{field.key}\\s*=\\s*{field.pattern}"
        m = re.match(pattern, data, re.DOTALL)
        if m is not None:
            result[field.key] = field.format(_format_value(m.group(1)))
        else:
            # noinspection PyTypeChecker
            result[field.key] = field.format(None)

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
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
