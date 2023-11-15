from flask import Blueprint, request, Response, render_template
from lpr import LPR as Lpr
from services import acessoService as AcessoService
from services import veiculoService as VeiculoService
import jsonpickle

controller_bp = Blueprint("acesso", __name__)

LPR_MODEL = Lpr(verbose=False)

ALLOWED_EXTENSIONS = {"jpg", "jpeg"}


def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def JsonResponse(object, status: int):
    response_json = jsonpickle.encode(object)
    return Response(response=response_json, status=status, mimetype="application/json")


@controller_bp.route("/", methods=["POST"])
def new_access():
    response = {"placa": "", "message": "Formato incorreto"}
    status = 401
    if "imageFile" not in request.files:
        response["message"] = "Nenhuma imagem enviada"
        status = 415
    else:
        file = request.files["imageFile"]

        if file and allowed_file(file.filename):
            try:
                _, _, detects = LPR_MODEL.detectFromFileStorage(file)

                hasAccess, charset, veiculo_id = VeiculoService.verify_access(
                    detects, LPR_MODEL
                )

                response["placa"] = "{}".format(charset)
                if hasAccess:
                    response["message"] = "Acesso autorizado!"
                    status = 200
                    AcessoService.Save(
                        ehEntrada=1,
                        caracteres_detectados=charset,
                        veiculo_id=veiculo_id,
                    )
                else:
                    response["message"] = "Acesso negado!"
                    status = 401

            except Exception as error:
                response = {
                    "message": "Não foi possível processar a imagem",
                    "erro": error,
                }
                status = 500

    return JsonResponse(response, status)


@controller_bp.route("/", methods=["GET"])
def home():
    acessos = AcessoService.GetAll()
    return render_template("home.jinja", acessos=acessos)


@controller_bp.route("/api/acessos", methods=["GET"])
def getAcessos():
    acessos = AcessoService.GetAllAsJson()
    return JsonResponse(acessos, 200)
