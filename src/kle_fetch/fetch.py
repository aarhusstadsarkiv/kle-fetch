import pickle
import typing as t
import logging

from dataclasses import dataclass
from pathlib import Path

from http.client import HTTPException
from http.client import HTTPResponse
from urllib.request import urlopen

import xmltodict as xml  # type: ignore[import-untyped]


T = t.TypeVar("T", bound="KLEResult")
fetch_log = logging.Logger("fetch_log")


@dataclass
class KLEResult:
    content: dict


class Emner(KLEResult):
    """
    Emner KLE fetch results
    """


class Facetter(KLEResult):
    """
    Facetter KLE fetch results
    """


KLE_URLS = {
    Emner: "https://api.kle-online.dk/resources/kle/emneplan?udgaaede=true",
    Facetter: "https://api.kle-online.dk/resources/kle/handlingsfacetter?udgaaede=true",
}


def fetch_xml(url: str) -> dict:
    response: HTTPResponse = urlopen(url)
    if response.status != 200:
        raise HTTPException(response.geturl(), response.status)
    return xml.parse(response.read())


class KLECache:
    cache_dir: Path

    def __init__(self, pickle_root: Path):
        self.cache_dir = pickle_root

    def path(self, item: t.Type[T]) -> Path:
        return self.cache_dir.joinpath(f"{item.__name__}.dat")

    def load(self, item: t.Type[T]) -> t.Optional[T]:
        if self.path(item).exists():
            with open(self.path(item), "rb") as f:
                fetch_log.info("loading pickled object")
                return pickle.load(f)
        return None

    def save(self, kle: T):
        fetch_log.info("saving pickled object")
        with open(
            self.path(type(kle)),
            "wb",
        ) as f:
            pickle.dump(kle, f)


class KLEHandler:
    cache: bool
    kle_pickler: KLECache

    def __init__(self, cache=False):
        self.cache = cache
        self.kle_pickler = KLECache(Path.cwd())

    def _load(self, load_type: t.Type[T]) -> T:
        fetch_log.info(f"getting object {load_type.__name__}")
        kle: t.Optional[T] = self.kle_pickler.load(load_type)
        if kle is None:
            fetch_log.info(f"saving fetched object {load_type.__name__}")
            kle = load_type(fetch_xml(KLE_URLS[load_type]))
            self.kle_pickler.save(kle)

        return kle

    def get_emner(self) -> Emner:
        return self._load(Emner)

    def get_facetter(self) -> Facetter:
        return self._load(Facetter)
