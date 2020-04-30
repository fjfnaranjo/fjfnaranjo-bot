from os import environ
from os.path import isfile


def pytest_generate_tests(metafunc):  # noqa
    if isfile('.env'):
        with open('.env', 'r') as env:
            lines = env.readlines()
            for line in lines:
                if len(line) > 0:
                    var, value = line.split('=')
                    environ[var] = value
