import typing


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
    max_key_length = max(map(len, groups.keys())) + 2  # padding for group members

    format_string = "{:<" + str(max_key_length + 1) + "}"
    for _ in countries:
        format_string = format_string + " {:>25}"

    # Display row heading
    result = result + format_string.format('', *countries) + '\n'

    # Now display the actual data
    for group_name in groups.keys():
        rows = groups[group_name]

        if len(rows) > 1:
            result = result + group_name + "\n"

        for row in rows:
            display_data = []

            for col in data:
                keys = row['keys']
                values = []

                for key in keys:
                    if col[key] is not None:
                        values.append(col[key])
                    else:
                        values.append('')

                cell_value = row['format'].format(*values)
                display_data.append(cell_value)

            label = row['label']
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
