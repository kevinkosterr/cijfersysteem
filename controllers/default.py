"""In deze uitleg ga ik er van uit dat je deze applicatie op je lokale machine draait.

Basis concept:

    Web2py is een Python web framework die gebaseerd is op Model View Controller. Web2py is gericht
    op Rapid Application Development (RAD).

    Controllers:
        Dit is de default controller, elke controller die wordt hierin gedefinieerd als een functie.
        Elke functie is dus een controller. Via een controller kun je data teruggeven aan de view,
        denk aan bijvoorbeeld een lijst met leerlingen. Dit doe je door het in een dictionary terug te geven,
        met als sleutel de naam die je de variabele wilt geven en als value de lijst met leerlingen.
        e.g. return dict(leerlingen=[])

    Views:
        Elke controller heeft ook een view, deze view moet ook dezelfde naam hebben als de controller.
        e.g. de index controller moet dus index.html als view hebben. Om deze pagina dus te bezoeken ga je
        naar https://127.0.0.1:8000/cijfersysteem/default/index. `cijfersysteem` is hier de applicatie, `default`
        is de controller in de controllers map en `index` is de functie in deze `default` controller.

        Om een variabele in een view aan te roepen, doe je het volgende: {{=leerlingen}}. `=` zorgt ervoor dat
        de variabele op het scherm wordt laten zien. `leerlingen` is hier de variabele vanuit het voorbeeld van
        de controller.

    Models:
        Models worden eigenlijk het meest gebruikt om databases en database tabellen in te definiëren.
        Het wordt ook gebruikt om bijvoorbeeld handige functies of objecten in te maken. Deze objecten zijn
        vanaf elke controller beschikbaar om te gebruiken. Om een database te definiëren doe je het volgende:

        database = DAL("sqlite:memory")
        hier is `database` de naam van de database, dit is een DAL object. "sqlite:memory" is dus een in memory database.
        andere voorbeelden zijn: "sqlite://storage.sqlite" & "postgres://postgres:postgres@localhost/postgres".

        om een tabel te definiëren doe je het volgende:
        database.define_table('foo',
                            Field('bar')
        )
        nu heb je een simpele tabel `foo` gemaakt met een veld `bar`.

    Request.args & request.vars:
        https://127.0.0.1:8000/cijfersysteem/default/index/1/2?message=hello
        applicatie: cijfersysteem
        controller: default
        functie: index
        request.args[0]: 1
        request.args[1]: 2
        request.vars.get('message') of request.vars['message']: hello


"""


@auth.requires_login()
def index():
    """Controller voor het overzicht van leerlingen.
    De grid zorgt ervoor dat er ook gelijk nieuwe leerlingen toegevoegd kunnen worden, verwijderd kunnen worden
    en bewerkt kunnen worden.

    :return: grid van leerlingen.
    """

    # definiëren van extra links die toegevoegd worden aan het grid.
    links = [
        # dict() is een dictionary object. dit is dus gelijk aan bijvoorbeeld _dict = {}
        dict(
            header="Dossier",
            # https://www.w3schools.com/python/python_lambda.asp
            body=lambda row: DIV(
                A(
                    "Dossier bekijken",  # de tekst die in de link moet verschijnen.
                    _href=URL(
                        "leerling", args=[row.id]
                    ),  # de href attribute van de link.
                    # hier voegen we html classes toe aan het DIV object.
                    _class="btn btn-default",
                )
            ),
        )
    ]

    # hier maken we een zogenoemde `grid` van een tabel in de database.
    # in dit geval is dat de leerling tabel uit db.
    leerlingen = SQLFORM.grid(
        db.leerling,
        # we hoeven geen details te kunnen zien over de leerlingen, hier hebben we een custom controller voor.
        details=False,
        # links is in dit geval de variabele die we bovenin de controller aangemaakt hebben.
        # of wel, links is een lijst met extra knoppen/links voor in het grid.
        links=links,
        # we hoeven de data niet te kunnen exporteren, daarom is dit False.
        csv=False,
        # advanced_search is onnodig, te gecompliceerd voor een kleine selectie van rows.
        advanced_search=False,
    )
    return dict(grid=leerlingen)


@auth.requires_login()
def leerling():
    """Controller voor een leerlingdossier.

    :return: leerling row met recente cijfers, gemiddelde cijfers en cijfers per vak.
    """
    if not request.args:
        # als er geen argument is meegegeven in de URL, dan redirecten we de gebruiker naar
        # de index pagina.
        # de URL ziet er dan zo uit https://127.0.0.1:800/cijfersysteem/default/leerling
        return redirect(URL("index"))

    # nu we zeker weten dat er een argument in de URL staat e.g. https://127.0.0.1:800/cijfersysteem/default/leerling/1
    # kunnen we verder met het uitvoeren van deze controller.

    # we willen hier de id van de leerling weten waarvan we het dossier gaan bekijken.
    leerling_id = request.args[0]
    # nu halen we de row op uit de database door simpelweg db.leerling[leerling_id] te doen.
    # hier is 'db' de naam van de database 'leerling' is de naam van de tabel. het record
    # halen we uit de database door het id (leerling_id) tussen blokhaken te zetten.
    cur_leerling = db.leerling[leerling_id]

    # hier wil ik de recente cijfers van de huidige leerling ophalen uit de database.
    # de regel hier onder zegt eigenlijk:
    # SELECT * FROM cijfer WHERE leerling == leerling_id
    # ORDER BY cijfer.ingevoerd_op LIMIT 0, 5;
    # de query staat tussen de db(), de `select` functie voert deze query daadwerkelijk uit.
    recente_cijfers = db(db.cijfer.leerling == leerling_id).select(
        limitby=(0, 5), orderby=~db.cijfer.ingevoerd_op
    )

    # hier wil ik alle klasgenoten van deze leerling opvragen, heel simpel eigenlijk.
    # onderstaande regel zegt eigenlijk het volgende:
    # SELECT * FROM leerling WHERE klas == cur_leerling.klas
    # ORDER BY leerling.achternaam LIMIT 0, 5;
    # cur_leerling is dus het row_object wat op line 92 opgevraagd is.
    klasgenoten = db(db.leerling.klas == cur_leerling.klas).select(
        limitby=(0, 5), orderby=db.leerling.achternaam
    )

    # gezien we een overzicht van alle cijfers willen maken, gaan we deze nu opvragen
    # uit de database. onderstaande regel zegt het volgende:
    # SELECT * FROM cijfer WHERE leerling == leerling_id
    # ORDER BY cijfer.vak;
    # zo krijgen we alle cijfers van deze persoon.
    cijfers = db(db.cijfer.leerling == leerling_id).select(orderby=db.cijfer.vak)

    # een dictionary kun je zien als een soort JSON object.
    # hier maken we een dictionary, dit doen we omdat we zo key, value pairs kunnen maken.
    # zo hebben we dan bijvoorbeeld {'NL': [8.0]} dit houdt in dat de key `NL` een lijst bevat met
    # het getal 8.0
    cijfers_per_vak = {}
    for cijfer in cijfers:
        try:
            # cijfer.vak.vakcode verwijst hier naar de vakcode het vak van dit cijfer hoort.
            # als de vakcode dus NL is, dan is cijfers_per_vak[cijfer.vak.vakcode] gelijk aan NL
            # hier voegen wij dus het cijfer aan toe.
            cijfers_per_vak[cijfer.vak.vakcode].append(cijfer.cijfer)
        except KeyError:
            # mocht deze vakcode nog niet bestaan als key in deze dictionary
            # dan zorgen we dat deze key een lege lijst krijgt als waarde.
            # vervolgens voegen we gelijk het cijfer van deze iteratie toe.
            cijfers_per_vak[cijfer.vak.vakcode] = []
            # de .append functie zorgt ervoor dat het cijfer toegevoegd wordt aan de lijst
            cijfers_per_vak[cijfer.vak.vakcode].append(cijfer.cijfer)

    # ook hier maken we weer een dictionary, zo kunnen we per vak het gemiddelde laten zien.
    gemiddelden = {}
    # cijfers_per_vak.items() geeft de items (keys en values) terug.
    # elke key uit cijfers_per_vak komt nu dus in de variabele vak terecht
    # elke value is een lijst met cijfers die gekoppeld zit aan de `vak` key.
    for vak, cijfers in cijfers_per_vak.items():
        # gemiddelde = opsomming van alle cijfers / de lengte van de cijfers.
        gemiddelde = sum(cijfers) / len(cijfers)
        # we ronden het gemiddelde wat hierboven berekent is af op 1 getal achter de komma.
        # e.g. gemiddelden = {'NL': 8.2}
        gemiddelden[vak] = round(gemiddelde, 1)

    return dict(
        leerling=cur_leerling,
        recente_cijfers=recente_cijfers,
        klasgenoten=klasgenoten,
        cijfers=cijfers_per_vak,
        gemiddelden=gemiddelden,
    )


@auth.requires_login()
def klassen():
    """Controller voor het laten zien van alle klassen in de database.
    De grid zorgt ervoor dat je ook gelijk een klas kunt toevoegen, verwijderen of bewerken.

    :return: grid van alle klassen.
    """
    links = [
        dict(
            header="Leerlingen",
            # https://www.w3schools.com/python/python_lambda.asp
            body=lambda row: DIV(
                A(
                    "Leerlingen",  # de tekst die in de link moet verschijnen.
                    _href=URL(
                        "klas", args=[row.id], vars=dict(came_from=request.function)
                    ),  # de href attribute van de link.
                    # hier voegen we html classes toe aan het DIV object.
                    _class="btn btn-default",
                )
            ),
        )
    ]

    klassen = SQLFORM.grid(
        db.klas, links=links, details=False, csv=False, advanced_search=False
    )
    return dict(grid=klassen)


@auth.requires_login()
def klas():
    """
    Controller voor het laten zien van alle leerlingen in een klas.

    :return: klas row & leerlingen in de klas
    """

    if not request.args:
        # als er geen argumenten meegegeven zijn in de URL
        # dan redirecten we de gebruiker naar de index.
        return redirect(URL("index"))

    klas_id = request.args[0]
    if not klas_id:
        # als er geen klas_id is, laat dan verder ook niets zien behalve
        # dat er geen klas opgegeven is.
        return "Geen klas opgegeven."

    # came_from is in dit geval de controller/pagina waar de
    # 'terug' knop op de klas.html pagina naar toe gaat.
    if not request.vars["came_from"]:
        # gezien er geen came_from meegegeven is, brengt de 'terug'
        # knop je gewoon terug naar de index pagina.
        came_from = "index"
        # in dit geval zijn er dus ook geen cf_args (came_from_args)
        cf_args = None
    else:
        came_from = request.vars.get("came_from")
        # sommige controllers hebben argumenten nodig om juist te functioneren
        # en terug te gaan naar de juiste pagina. mocht dit niet nodig zijn, dan hoeven
        # we ook geen cf_args mee te geven in de URL.
        cf_args = request.vars.get("cf_args", None)

    # haal de `klas` row op uit de database die matcht met
    # het klas_id wat uit de request.args is opgehaald.
    klas_row = db.klas[klas_id]
    # klas_row.leerling geeft een Set object terug van alle leerlingen
    # die in deze klas_row zitten, of wel alle leerlingen die in deze
    # klas zitten. we voeren .select() uit om de daadwerkelijk rows te selecteren.
    leerlingen = klas_row.leerling.select()

    return dict(
        klas_row=klas_row,
        leerlingen=leerlingen,
        came_from=came_from,
        cf_args=cf_args,
    )


@auth.requires_login()
def vakken():
    """
    Controller voor het laten zien van alle vakken die aanwezig zijn in de database.
    De smartgrid geeft het ook de mogelijkheid om hier extra vakken aan toe te voegen, vakken te verwijderen en
    om vakken te bewerken.

    :return: smartgrid van vakken.
    """

    # een simpele smartgrid/overzicht van alle vakken die in de database staan.
    # http://www.web2py.com/books/default/chapter/29/07/forms-and-validators?search=smartgrid#SQLFORM-smartgrid
    vakken = SQLFORM.smartgrid(db.vak, csv=False, advanced_search=False)
    return dict(grid=vakken)


@auth.requires_login()
def cijfers_invoeren():
    if not request.args:
        # we verplichten de gebruiker om variabelen in de URL te hebben
        # staan deze niet in de URL? redirect dan naar de index.
        return redirect(URL("index"))

    # e.g. https://127.0.0.1/cijfersysteem/default/cijfers_invoeren/1, leerling_id is dan 1
    leerling_id = request.args[0]

    # de default value van het leerling veld voor dit cijfer is de leerling_id
    db.cijfer.leerling.default = leerling_id
    # de gebruiker mag vanuit het formulier de leerling niet aanpassen.
    db.cijfer.leerling.writable = False

    # formulier op basis van de tabel `cijfer` in database `db`.
    # .process() zorgt er voor dat de data ingevoerd wordt in de database.
    form = SQLFORM(db.cijfer).process()

    if form.accepted:
        # als er geen fouten zitten in het formulier, laat deze dan
        # records invoeren in de database en laat een bericht zien aan de gebruiker.
        response.flash = "Cijfer ingevoerd."

    return dict(form=form)


@auth.requires_login()
def cijfers_aanpassen():
    """Controller voor het aanpassen van een cijfer.

    :return: grid van cijfers van een leerling
    """
    if not request.vars:
        # we verplichten de gebruiker om variabelen in de URL te hebben
        # staan deze niet in de URL? redirect dan naar de index.
        return redirect(URL("index"))

    # dit moet altijd een integer zijn.
    leerling_id = request.vars.get("leerling", None)
    if not leerling_id:
        # als er geen leerling is opgegeven, dan laten we alleen een bericht zien.
        return "Geen leerling opgegeven."
    came_from = request.vars.get("came_from", None)

    # het id van dit record hoeft niet te lezen te zijn
    db.cijfer.id.readable = False
    # de leerling van dit record mag niet aangepast worden.
    db.cijfer.leerling.writable = False
    # het vak van dit record mag niet aangepast worden.
    db.cijfer.vak.writable = False

    # WHERE cijfer.leerling == leerling_id
    query = db.cijfer.leerling == leerling_id

    grid = SQLFORM.smartgrid(
        db.cijfer,
        # constraints zorgt ervoor dat er alleen maar cijfers worden
        # laten zien die aan de query voldoen.
        constraints=dict(cijfer=query),
        details=False,
        create=False,
        searchable=False,
        csv=False,
    )

    return dict(grid=grid, came_from=came_from if came_from else "index")


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
