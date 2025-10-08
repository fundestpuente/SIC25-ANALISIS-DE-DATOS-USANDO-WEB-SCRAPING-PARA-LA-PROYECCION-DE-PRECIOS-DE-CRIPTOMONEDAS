from enum import Enum

class ListaOperadoresCondicionales(Enum):
    EQUAL = "$eq"  # ==
    NOT_EQUAL = "$ne"  # <>
    GREATER_THAN = "$gt"  # >
    GREATER_THAN_OR_EQUAL_TO = "$gte"  # >=
    LESS_THAN = "$lt"  # <
    LESS_THAN_OR_EQUAL_TO = "$lte"  # <=
    LIKE = "$regex"  # like
    IN = "$in"  # in
    NOT_IN = "$nin"  # not in
    EXISTS = "$exists"  # exists
    NOT_EXISTS = "$exists"  # not exists

class ListaCollecciones(Enum):
    ScrappingResults = "scrapping_results"

class CamposPrincipales(Enum):
    pass