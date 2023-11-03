from flask import Flask, request, Response, render_template, jsonify
from flask_assets import Environment, Bundle
import jsonpickle
from lpr import LRP as Lpr
from sqlalchemy import *
import mimetypes
from services import acessoService as AcessoService
from services import veiculoService as VeiculoService
from services import funcionarioService as FuncionarioService

# Initialize the Flask application
app = Flask(__name__)
assets = Environment(app)

css_bundle = Bundle("scss/estilo.scss", filters="libsass", output="css/site.css")
assets.register("css_bundle", css_bundle)


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

LPR_MODEL = Lpr(verbose=False)


def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_content_type(extensao: str):
    content_type, _ = mimetypes.guess_type(f"arquivo.{extensao}")

    if content_type is None:
        return "application/octet-stream"

    return content_type


@app.route("/", methods=["POST"])
def test():
    if "imageFile" not in request.files:
        response = {"message": "Nenhuma imagem enviada"}
        response_pickled = jsonpickle.encode(response)

        return Response(
            response=response_pickled, status=400, mimetype="application/json"
        )

    file = request.files["imageFile"]

    response = {"message": "Formato incorreto"}

    if file and allowed_file(file.filename):
        try:
            _, _, caracters = LPR_MODEL.detectFromFileStorage(file)
            charset = ("".join(caracters)).replace(" ", "").replace("\n", "")
            print(f'*{charset}*')
            veiculo_id = None
            veiculo = VeiculoService.GetByPlaca(charset)
            response = {"message": "results: {}".format(charset)}

            if veiculo is not None:
                veiculo_id = veiculo.id
            else:
                response["message"] = "Acesso Negado! \n Placa:{}não encontrada".format(
                    charset
                )

            AcessoService.Save(
                ehEntrada=1, caracteres_detectados=charset, veiculo_id=veiculo_id
            )

            response_pickled = jsonpickle.encode(response)

            return Response(
                response=response_pickled, status=200, mimetype="application/json"
            )

        except Exception as error:
            response = {"message": "Não foi possível processar a imagem", "erro": error}
            response_pickled = jsonpickle.encode(response)
            return Response(
                response=response_pickled, status=500, mimetype="application/json"
            )

    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=400, mimetype="application/json")


@app.route("/", methods=["GET"])
def home():
    acessos = AcessoService.GetAll()
    return render_template("home.jinja", acessos=acessos)


@app.route("/api/acessos", methods=["GET"])
def getAcessos():
    acessos = AcessoService.GetAllAsJson()
    return Response(response=acessos, status=200, mimetype="application/json")


@app.route("/funcionario", methods=["GET"])
def funcionario():
    funcionarios = FuncionarioService.GetAll()
    return render_template("funcionario/index.jinja", funcionarios=funcionarios)

@app.route("/funcionario/create", methods=["GET"])
def add_funcionario():
    return render_template("funcionario/create.jinja")


@app.route("/veiculo", methods=["GET"])
def veiculo():
    veiculos = VeiculoService.GetAll()
    return render_template("veiculo/index.jinja", veiculos=veiculos)


@app.route("/image-raw/<int:id>")
def raw_image(id: int):
    image = AcessoService.GetById(id)
    content_type = get_content_type(image.file_ext)
    return Response(image.raw_data, mimetype=content_type)


@app.route("/image-treated/<int:id>")
def treated_image(id: int):
    image = AcessoService.GetById(id)
    content_type = get_content_type(image.file_ext)
    return Response(image.treated_data, mimetype=content_type)


if __name__ == "__main__":
    app.debug = True
    app.run()
