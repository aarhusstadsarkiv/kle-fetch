from __future__ import annotations

import typing as t

from functools import lru_cache
from pydantic import BaseModel

from kle_fetch.fetch import KLEHandler


kle_handler = KLEHandler(cache=True)


class KLEPart(BaseModel):
    nr: str
    txt: str
    oprettetdato: str
    udgaaetdato: t.Optional[str] = None

    @classmethod
    def build(cls, part_dict: dict, part_name: str, kle_num: str) -> KLEPart:
        return cls(
            nr=kle_num,
            txt=part_dict[part_name + "Titel"],
            oprettetdato=part_dict[part_name + "AdministrativInfo"]["OprettetDato"],
            udgaaetdato=part_dict[part_name + "AdministrativInfo"]
            .get("Historisk", {})
            .get("UdgaaetDato", None),
        )


class KLE(BaseModel):
    journalnr: str

    hovedgruppe: KLEPart
    gruppe: KLEPart
    emne: KLEPart

    @classmethod
    def build(cls, hg: dict, g: dict, e: dict, kle_nums: list[str]) -> KLE:
        return cls(
            journalnr=e["EmneNr"],
            hovedgruppe=KLEPart.build(hg, "Hovedgruppe", kle_nums[0]),
            gruppe=KLEPart.build(g, "Gruppe", kle_nums[1]),
            emne=KLEPart.build(e, "Emne", kle_nums[2]),
        )

    def contains(self, txt: str) -> bool:
        txt = txt.lower()
        return (
            txt in self.hovedgruppe.txt.lower()
            or txt in self.gruppe.txt.lower()
            or txt in self.emne.txt.lower()
        )

    def flatten(self) -> t.Dict[str, str]:
        flattened = {"journalnr": self.journalnr}

        for model_field in KLE.model_fields.keys():
            if isinstance(model_field, KLEPart):
                dumped_model: KLEPart = getattr(self, model_field).model_dump(mode="json")
                keys_fixed_model_field = {f"{model_field}{key}": value for key, value in dumped_model.items()}
                flattened.update(keys_fixed_model_field)
        return flattened


@lru_cache
def get_emner() -> list[KLE]:
    fetched_emner = kle_handler.get_emner().content
    emner: list[KLE] = []

    for hg in fetched_emner["KLE-Emneplan"]["Hovedgruppe"]:
        for g in hg["Gruppe"] if isinstance(hg["Gruppe"], list) else [hg["Gruppe"]]:
            for e in g["Emne"] if isinstance(g["Emne"], list) else [g["Emne"]]:
                kle_nums = e["EmneNr"].split(".")
                emner.append(KLE.build(hg, g, e, kle_nums))

    return sorted(emner, key=lambda e: e.journalnr)


@lru_cache
def get_facetter() -> list[tuple[str, str]]:
    all_facetter = kle_handler.get_facetter().content
    facetter = [
        (f"{f['HandlingsfacetNr']} {f['HandlingsfacetTitel']}", f["HandlingsfacetNr"])
        for fk in all_facetter["KLE-Handlingsfacetter"]["HandlingsfacetKategori"]
        for f in fk["Handlingsfacet"]
    ]
    return sorted(facetter, key=lambda e: e[0])
