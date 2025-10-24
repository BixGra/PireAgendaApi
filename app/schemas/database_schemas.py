from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Categories(Enum):
    angledroit = "AngleDroit"
    animaux = "Animaux"
    art = "Art"
    cinema_series = "Cinéma/Séries"
    conflit = "Conflit"
    culture = "Culture"
    divers = "Divers"
    droit_justice = "Droit/Justice"
    ecologie_environnement = "Écologie/Environnement"
    economie = "Économie"
    education = "Éducation"
    fete_nationale = "Fête nationale"
    feminisme = "Féminisme"
    gaming = "Gaming"
    gastronomie = "Gastronomie"
    geographie = "Géographie"
    histoire = "Histoire"
    humour = "Humour"
    information = "Information"
    innovation = "Innovation"
    internet = "Internet"
    jeunesse = "Jeunesse"
    jeux = "Jeux"
    langues = "Langues"
    lgbt = "LGBTQIA+"
    litterature = "Littérature"
    loisirs = "Loisirs"
    medias = "Médias"
    musique = "Musique"
    pire_commu = "Pire Commu"
    politique = "Politique"
    religions = "Religions"
    sante = "Santé"
    sciences = "Sciences"
    sciences_sociales = "Sciences sociales"
    societe = "Société"
    solidarite = "Solidarité"
    sports = "Sports"
    technologies = "Technologies"
    television = "Télévision"
    travail = "Travail"
    twitch = "Twitch"
    vegetaux = "Végétaux"

    sans_categorie = "Sans catégorie"

    none = None

    @classmethod
    def _missing_(cls, value):
        return cls.none


class CategoryMapping(BaseModel):
    name: str
    value: str


class CategoriesMapping(BaseModel):
    items: list[CategoryMapping]


class AgendaItem(BaseModel):
    id: int
    date: datetime
    title: str
    description: str
    category1: str = "sans_categorie"
    category2: str | None = None
    category3: str | None = None
    link: str | None = None
    link_title: str | None = None

    @field_validator("category2", "category3", mode="before")
    @classmethod
    def validate(cls, value):
        if value == "none":
            return None
        return value


class AgendaList(BaseModel):
    items: list[AgendaItem]


class GetByCategoriesInput(BaseModel):
    categories: list[Categories] = Field(max_length=3)


class GetByDateInput(BaseModel):
    date: datetime


class SearchInput(BaseModel):
    query: str
    in_title: bool = True
    in_description: bool = False

    @model_validator(mode="after")
    def validate(self):
        if not (self.in_title or self.in_description):
            raise ValueError("Search must be done in at least one field")
        return self
