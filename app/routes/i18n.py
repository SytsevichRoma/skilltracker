from flask import Blueprint, request, redirect, session

i18n_bp = Blueprint("i18n", __name__)

@i18n_bp.get("/lang/<code>")
def set_lang(code: str):
    # збережемо в сесію і повернемось назад
    session["lang"] = code
    return redirect(request.referrer or "/")
