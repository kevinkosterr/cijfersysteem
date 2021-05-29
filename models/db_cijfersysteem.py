import datetime

db.define_table(
    "klas",
    Field("opleiding", required=True, requires=IS_NOT_EMPTY()),
    Field(
        "klassencode",
        required=True,
        requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, "klas.klassencode")],
    ),
    format=lambda row: row.klassencode,
    plural="Klassen",
)

db.define_table(
    "leerling",
    Field("foto", "upload"),
    Field("voornaam", required=True, requires=IS_NOT_EMPTY()),
    Field(
        "tussenvoegsel",
        default=None,
        represent=lambda value, row: value if value else "n.v.t.",
    ),
    Field("achternaam", required=True, requires=IS_NOT_EMPTY()),
    Field("klas", "reference klas", required=True),
    Field("geboortedatum", "date", required=True, requires=IS_NOT_EMPTY()),
    format=lambda row: f"{row.voornaam} {row.achternaam}",
    plural="Leerlingen",
)

db.define_table(
    "vak",
    Field("naam", requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, "vak.naam")]),
    Field(
        "vakcode", length=2, requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, "vak.vakcode")]
    ),
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
