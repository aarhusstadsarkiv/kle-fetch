from json import dump
from pathlib import Path

from .fetch import fetch_emner
from .fetch import fetch_facetter


def __main__():
    with Path.cwd().joinpath("emner.json").open("w") as fh:
        dump(fetch_emner(), fh)

    with Path.cwd().joinpath("facetter.json").open("w") as fh:
        dump(fetch_facetter(), fh)


if __name__ == '__main__':
    __main__()
