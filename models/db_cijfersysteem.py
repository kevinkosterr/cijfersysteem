import datetime
import os

db.define_table(
    "klas",
    Field("opleiding", required=True, requires=IS_NOT_EMPTY()),
    Field("klassencode", required=True, requires=IS_NOT_EMPTY()),
    format=lambda row: row.klassencode,
    plural="Klassen",
)

db.define_table(
    "leerling",
    Field("foto", "upload"),
    Field("voornaam", required=True, requires=IS_NOT_EMPTY()),
    Field("tussenvoegsel", default=None),
    Field("achternaam", required=True, requires=IS_NOT_EMPTY()),
    Field("klas", "reference klas", required=True),
    Field("geboortedatum", "date", required=True, requires=IS_NOT_EMPTY()),
    format=lambda row: f"{row.achternaam}, {row.voornaam}",
    plural="Leerlingen",
)

db.define_table(
    "vak",
    Field("naam", requires=IS_NOT_EMPTY()),
    Field("vakcode", length=2, requires=IS_NOT_EMPTY()),
    format=lambda row: row.naam,
    plural="Vakken",
)

db.define_table(
    "cijfer",
    Field("cijfer", "float"),
    Field("vak", "reference vak", required=True),
    Field("leerling", "reference leerling", required=True),
    Field(
        "ingevoerd_op",
        default=datetime.datetime.now(),
        required=True,
        writable=False,
        readable=False,
    ),
    format=lambda row: row.cijfer,
    plural="Cijfers",
)