from flask import Flask, request, Response, render_template
import jsonpickle
from lpr import LRP as Lpr
from sqlalchemy import *
import mimetypes
from services import imageService as ImgService

# Initialize the Flask application
app = Flask(__name__)

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
            bites, _, caracters = LPR_MODEL.detectFromFileStorage(file)
            charset = "".join(caracters)
            ImgService.Save(bites, charset, file.filename)
            response = {"message": "results: {}".format(charset)}

            response_pickled = jsonpickle.encode(response)

            return Response(response=response_pickled, status=200, mimetype="application/json")
        
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
    images = ImgService.GetAll()
    return render_template("home.html", imagens=images)


@app.route("/image-raw/<int:id>")
def raw_image(id: int):
    image = ImgService.GetById(id)
    content_type = get_content_type(image.file_ext)
    return Response(image.raw_data, mimetype=content_type)


@app.route("/image-treated/<int:id>")
def treated_image(id: int):
    image = ImgService.GetById(id)
    content_type = get_content_type(image.file_ext)
    return Response(image.treated_data, mimetype=content_type)


if __name__ == "__main__":
    app.debug = True
    app.run()
