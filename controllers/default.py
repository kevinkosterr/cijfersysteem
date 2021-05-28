@auth.requires_login()
def index():
    links = [
        dict(
            header="Bekijken",
            body=lambda row: DIV(A("Bekijken", _href=URL("leerling", args=[row.id]), _class='btn btn-default')),
        )
    ]

    leerlingen = SQLFORM.grid(
        db.leerling,
        details=False,
        links=links,
        csv=False,
        advanced_search=False,
    )
    return dict(grid=leerlingen)


@auth.requires_login()
def leerling():
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
    # cur_leerling is dus het row_object wat op line 36 opgevraagd is.
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
    klassen = SQLFORM.smartgrid(db.klas, csv=False, advanced_search=False)
    return dict(grid=klassen)


@auth.requires_login()
def vakken():
    vakken = SQLFORM.smartgrid(db.vak, csv=False, advanced_search=False)
    return dict(grid=vakken)


@auth.requires_login()
def cijfers_invoeren():
    if not request.args:
        return redirect(URL("index"))
    leerling = request.args[0]

    db.cijfer.leerling.default = leerling
    db.cijfer.leerling.writable = False

    form = SQLFORM(db.cijfer).process()

    if form.accepted:
        response.flash = "Cijfer ingevoerd."

    return dict(form=form)


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
