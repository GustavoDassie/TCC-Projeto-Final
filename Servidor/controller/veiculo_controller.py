from flask import (
    Blueprint,
    Flask,
    request,
    Response,
    render_template,
    redirect,
    url_for,
)
from services import veiculoService as Service
from services import funcionarioService as FuncionarioService


controller_bp = Blueprint("veiculo", __name__)


@controller_bp.route("/", methods=["GET"])
def home():
    entities = Service.GetAll()
    return render_template("veiculo/index.jinja", entities=entities)


@controller_bp.route("/create", methods=["GET"])
def create():
    all_funcionarios = FuncionarioService.GetAll()
    return render_template("veiculo/create.jinja", all_funcionarios=all_funcionarios)


@controller_bp.route("/create", methods=["POST"])
def create_post():
    data = request.form

    Service.Save(data["placa"], data["funcionario_id"], data["modelo"], data["ano"], 1)
    return redirect(url_for("veiculo.home"))


@controller_bp.route("/toggle/<int:id>", methods=["GET"])
def toggle(id: int):
    Service.ToggleAtivo(id)
    return redirect(url_for("veiculo.home"))


@controller_bp.route("/edit/<int:id>", methods=["GET"])
def edit(id: int):
    entity = Service.GetById(id)
    all_funcionarios = FuncionarioService.GetAll()
    return render_template(
        "veiculo/edit.jinja", entity=entity, all_funcionarios=all_funcionarios
    )


@controller_bp.route("/edit/<int:id>", methods=["POST"])
def edit_post(id: int):
    data = request.form
    Service.Update(
        id,
        data["placa"],
        data["funcionario_id"],
        data["modelo"],
        data["ano"],
    )
    return redirect(url_for("veiculo.home"))


@controller_bp.route("/delete/<int:id>", methods=["GET"])
def delete(id: int):
    Service.Delete(id)
    return redirect(url_for("veiculo.home"))
