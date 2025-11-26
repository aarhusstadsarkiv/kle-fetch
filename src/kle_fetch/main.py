from functools import lru_cache
from pydantic import BaseModel

from kle_fetch.fetch import KLEHandler


kle_handler = KLEHandler(cache=True)


class Emne(BaseModel):
    JournalNr: str
    HovedGruppeNr: str
    HovedGruppeTxt: str
    GruppeNr: str
    GruppeTxt: str
    EmneNr: str
    EmneTxt: str

    def contains(self, txt: str) -> bool:
        txt = txt.lower()
        return (
            txt in self.HovedGruppeTxt.lower()
            or txt in self.GruppeTxt.lower()
            or txt in self.EmneTxt.lower()
        )


@lru_cache
def get_emner() -> list[Emne]:
    fetched_emner = kle_handler.get_emner().content
    # grupper = [
    #     (f"{g['GruppeNr']} {g['GruppeTitel']}", list(map(int, g["GruppeNr"].split("."))))
    #     for hg in all_emner["KLE-Emneplan"]["Hovedgruppe"]
    #     for g in (hg["Gruppe"] if isinstance(hg["Gruppe"], list) else [hg["Gruppe"]])
    # ]

    emner: list[Emne] = []

    for hg in fetched_emner["KLE-Emneplan"]["Hovedgruppe"]:
        for g in hg["Gruppe"] if isinstance(hg["Gruppe"], list) else [hg["Gruppe"]]:
            for e in g["Emne"] if isinstance(g["Emne"], list) else [g["Emne"]]:
                kle_nums = e["EmneNr"].split(".")
                emner.append(
                    Emne(
                        JournalNr=e["EmneNr"],
                        HovedGruppeNr=kle_nums[0],
                        HovedGruppeTxt=hg["HovedgruppeTitel"],
                        GruppeNr=kle_nums[1],
                        GruppeTxt=g["GruppeTitel"],
                        EmneNr=kle_nums[2],
                        EmneTxt=e["EmneTitel"],
                    )
                )

    return sorted(emner, key=lambda e: e.JournalNr)


@lru_cache
def get_facetter() -> list[tuple[str, str]]:
    all_facetter = kle_handler.get_facetter().content
    facetter = [
        (f"{f['HandlingsfacetNr']} {f['HandlingsfacetTitel']}", f["HandlingsfacetNr"])
        for fk in all_facetter["KLE-Handlingsfacetter"]["HandlingsfacetKategori"]
        for f in fk["Handlingsfacet"]
    ]
    return sorted(facetter, key=lambda e: e[0])


if __name__ == "__main__":
    emner = get_emner()
    filtered = list(filter(lambda x: x.contains("virksomhed"), emner))
    print(filtered[10])
