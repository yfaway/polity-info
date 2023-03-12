import typing


# The terminal colors; add prefix padding to ensure they are of the same length (for str.format()).
GREEN_COLOR = '\033[32m'
WHITE_COLOR = ' \033[0m'


def format_countries(countries: typing.List[str], data: typing.List[typing.Dict]) -> str:
    """
    Returns a string contains all the data.
    :param countries the list of country; must match with the size of data.
    :param data a list of data retrieved from polity_parser#parse_country
    """

    groups = {
        'Area': [
            {
                'label': 'Total',
                'format': "{} km\u00B2 ({})",
                'keys': ['area_km2', 'area_rank']
            },
            {
                'label': 'Water (%)',
                'format': "{}",
                'keys': ['percent_water']
            },
        ],
        'Population': [
            {
                'label': 'Estimate',
                'format': "{} ({})",
                'keys': ['population_estimate', 'population_estimate_rank']
            },
            {
                'label': 'Census',
                'format': "{}",
                'keys': ['population_census']
            },
            {
                'label': 'Density',
                'format': "{}/km\u00B2 ({})",
                'keys': ['population_density_km2', 'population_density_rank']
            },
        ],
        'GDP (PPP)': [
            {
                'label': 'Total',
                'format': "${} ({})",
                'keys': ['GDP_PPP', 'GDP_PPP_rank']
            },
            {
                'label': 'Per capita',
                'format': "${} ({})",
                'keys': ['GDP_PPP_per_capita', 'GDP_PPP_per_capita_rank']
            },
        ],
        'GDP (nominal)': [
            {
                'label': 'Total',
                'format': "${} ({})",
                'keys': ['GDP_nominal', 'GDP_nominal_rank']
            },
            {
                'label': 'Per capita',
                'format': "${} ({})",
                'keys': ['GDP_nominal_per_capita', 'GDP_nominal_per_capita_rank']
            },
        ],
        'GINI': [
            {
                'label': 'GINI',
                'format': "{} ({})",
                'keys': ['Gini', 'Gini_rank']
            },
        ],
        'HDI': [
            {
                'label': 'HDI',
                'format': "{} ({})",
                'keys': ['HDI', 'HDI_rank']
            },
        ],
    }

    result = ''

    # Rendering by rows (values) and columns (heading and countries). Each cell value always has the console color
    # coding (white by default). Highlighted cell value has special color.

    max_key_length = max(map(len, groups.keys())) + len(WHITE_COLOR) + 2  # padding for group members

    format_string = "{:<" + str(max_key_length + len(WHITE_COLOR) + 1) + "}"
    for _ in countries:
        format_string = format_string + " {:>30}"

    # Display row heading
    colored_country_names = [WHITE_COLOR + c for c in countries]
    result = result + format_string.format(WHITE_COLOR, *colored_country_names) + '\n'

    # Now display the actual data
    for group_name in groups.keys():
        rows = groups[group_name]

        if len(rows) > 1:
            result = result + WHITE_COLOR + group_name + "\n"

        for row in rows:
            display_data = []
            keys = row['keys']

            # Find the highlighted value using the gt function based on the first key.
            first_key = keys[0]
            highlight_value = data[0][first_key]
            for col in data:
                if col[first_key] > highlight_value:
                    highlight_value = col[first_key]

            for col in data:
                values = []

                color = GREEN_COLOR if col[keys[0]] == highlight_value else WHITE_COLOR
                for key in keys:
                    if col[key] is not None:
                        values.append(str(col[key].value))
                    else:
                        values.append(color)  # empty value

                cell_value = color + row['format'].format(*values)
                display_data.append(cell_value)

            label = WHITE_COLOR + row['label']
            if len(rows) > 1:
                label = '  ' + label  # padding for group member
            result = result + format_string.format(label, *display_data) + '\n'

    """
    for key in data[0].keys():
        display_key = key + ":"
        display_data = []
        for col in data:
            if col[key] is not None:
                display_data.append(col[key])
            else:
                display_data.append('')

        result = result + format_string.format(display_key, *display_data) + '\n'
    """

    return result
