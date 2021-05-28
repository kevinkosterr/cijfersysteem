# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
@auth.requires_login()
def index():
    links = [
        dict(
            header="Bekijken",
            body=lambda row: A("Bekijken", _href=URL("leerling", args=[row.id])),
        )
    ]

    leerlingen = SQLFORM.grid(db.leerling, editable=False, details=False, links=links)
    return dict(grid=leerlingen)


@auth.requires_login()
def leerling():
    if not request.args:
        redirect(URL("index"))
    leerling_id = request.args[0]
    cur_leerling = db.leerling[leerling_id]
    recente_cijfers = db(db.cijfer.leerling == leerling_id).select(
        limitby=(0, 5), orderby=~db.cijfer.ingevoerd_op
    )
    klasgenoten = db(db.leerling.klas == cur_leerling.klas).select(
        limitby=(0, 5), orderby=db.leerling.achternaam
    )
    return dict(
        leerling=cur_leerling, recente_cijfers=recente_cijfers, klasgenoten=klasgenoten
    )


# ---- API (example) -----
@auth.requires_login()
def vakken():
    vakken = SQLFORM.smartgrid(db.vak, csv=False, advanced_search=False)
    return dict(grid=vakken)



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
