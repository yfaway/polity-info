import typing


def format_countries(countries: typing.List[str], data: typing.List[typing.Dict]) -> str:
    """
    Returns a string contains all the data.
    :param countries the list of country; must match with the size of data.
    :param data a list of data retrieved from polity_parser#parse_country
    """
    result = ''
    max_key_length = max(map(len, data[0].keys()))

    format_string = "{:<" + str(max_key_length + 1) + "}"
    for _ in countries:
        format_string = format_string + " {:>20}"

    # Display row heading
    result = result + format_string.format('', *countries) + '\n'

    # Now display the actual data
    for key in data[0].keys():
        display_key = key + ":"

        display_data = []
        for col in data:
            if col[key] is not None:
                display_data.append(col[key])
            else:
                display_data.append('')

        result = result + format_string.format(display_key, *display_data) + '\n'

    return result
