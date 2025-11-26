import json

from functools import lru_cache

from kle_fetch.fetch import KLEHandler


kle_handler = KLEHandler(cache=True)


@lru_cache
def get_emner() -> list[tuple[str, list[int]]]:
    all_emner = kle_handler.get_emner().content
    grupper = [
        (f"{g['GruppeNr']} {g['GruppeTitel']}", list(map(int, g["GruppeNr"].split("."))))
        for hg in all_emner["KLE-Emneplan"]["Hovedgruppe"]
        for g in (hg["Gruppe"] if isinstance(hg["Gruppe"], list) else [hg["Gruppe"]])
    ]
    emner = [
        (f"{e['EmneNr']} {e['EmneTitel']}", list(map(int, e["EmneNr"].split("."))))
        for hg in all_emner["KLE-Emneplan"]["Hovedgruppe"]
        for g in (hg["Gruppe"] if isinstance(hg["Gruppe"], list) else [hg["Gruppe"]])
        for e in (g["Emne"] if isinstance(g["Emne"], list) else [g["Emne"]])
    ]
    return sorted(grupper + emner, key=lambda e: e[0])


@lru_cache
def get_facetter() -> list[tuple[str, str]]:
    all_facetter = kle_handler.get_facetter().content
    facetter = [
        (f"{f['HandlingsfacetNr']} {f['HandlingsfacetTitel']}", f["HandlingsfacetNr"])
        for fk in all_facetter["KLE-Handlingsfacetter"]["HandlingsfacetKategori"]
        for f in fk["Handlingsfacet"]
    ]
    return sorted(facetter, key=lambda e: e[0])



if __name__ == '__main__':
    print(json.dumps(kle_handler.get_emner().content, indent=4)[:5000])
