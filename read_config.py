from configparser import ConfigParser
import json
from inspect import getmembers
from pprint import pprint

project_path = '/git-projects/PriceNotifier/'


def read_parameters(section, filename=project_path + 'config/config.ini'):
    # create a parser
    parser = ConfigParser(interpolation=None)
    # read config file
    parser.read(filename)

    # get section
    output = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            output[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return output


def read_json(file=project_path + 'config/sites.json'):
    with open(file) as data:
        sites = json.load(data)

    return sites


if __name__ == '__main__':
    print(type(read_parameters('telegram')['token']))
