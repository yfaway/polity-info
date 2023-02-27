# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from polity_info.polity_parser import parse_country

if __name__ == '__main__':
    data = parse_country('Canada')

    for key in data.keys():
        print(f"{key}: {data[key]}")

