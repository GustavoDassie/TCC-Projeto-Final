from flask import (
    Blueprint,
    Flask,
    request,
    Response,
    render_template,
    redirect,
    url_for,
)
from services import funcionarioService as Service

controller_bp = Blueprint("funcionario", __name__)


@controller_bp.route("/", methods=["GET"])
def home():
    entities = Service.GetAll()
    return render_template("funcionario/index.jinja", entities=entities)


@controller_bp.route("/create", methods=["GET"])
def create():
    return render_template("funcionario/create.jinja")


@controller_bp.route("/create", methods=["POST"])
def create_post():
    data = request.form

    Service.Save(
        data["nome"], data["email"], data["cpf"], data["prontuario"], 1
    )
    return redirect(url_for("funcionario.home"))


@controller_bp.route("/toggle/<int:id>", methods=["GET"])
def toggle(id: int):
    Service.ToggleAtivo(id)
    return redirect(url_for("funcionario.home"))


@controller_bp.route("/edit/<int:id>", methods=["GET"])
def edit(id: int):
    entity = Service.GetById(id)
    return render_template("funcionario/edit.jinja", entity=entity)


@controller_bp.route("/edit/<int:id>", methods=["POST"])
def edit_post(id: int):
    data = request.form

    Service.Update(id, data["nome"], data["email"])
    return redirect(url_for("funcionario.home"))


@controller_bp.route("/delete/<int:id>", methods=["GET"])
def delete(id: int):
    Service.Delete(id)
    return redirect(url_for("funcionario.home"))
