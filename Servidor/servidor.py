from flask import Flask, request, Response, render_template
import jsonpickle
import numpy as np
import cv2
import time
from LerPlaca import LerPlaca
from SimpleLPR import LerPlaca as SimpleLPRRead
import os
from imutils import paths
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

UPLOAD_FOLDER = (
    r"C:\Users\gusta\Documentos\IFSP\TCC\TCC-Projeto-Final\Servidor\static\uploads"
)
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# route http posts to this method
@app.route("/", methods=["POST"])
def test():
    print("chegou!")
    ler = LerPlaca()
    r = request
    if "imageFile" not in request.files:
        response = {
            "message": "Nenhuma imagem enviada"
        }
        # encode response using jsonpickle
        response_pickled = jsonpickle.encode(response)

        return Response(
            response=response_pickled, status=400, mimetype="application/json"
        )

    file = request.files["imageFile"]
    print(file)
    print(r.files)
   
    response = {
        "message": "Não foi possível processar a imagem"
    }
    if file and allowed_file(file.filename):
        time_stamp = time.time()

        filename = (
            str(time_stamp).replace(".", "_")
            + "."
            + file.filename.split(".")[1].lower()
        )
        print("{}".format(filename))
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        img = cv2.imread(os.path.join(UPLOAD_FOLDER, filename))
        results = SimpleLPRRead(img)
        print(results)
        response = {
            "message": "results: {}".format(results)
        }

    # build a response dict to send back to client
   
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route("/Home", methods=["GET"])
def home():
    imagePaths = []
    for (rootDir, dirNames, filenames) in os.walk(UPLOAD_FOLDER):
        # loop over the filenames in the current directory
        for filename in filenames:
            # if the contains string is not none and the filename does not contain
            # the supplied string, then ignore the file
            # determine the file extension of the current file
            ext = filename[filename.rfind("."):].lower()

            # check to see if the file is an image and should be processed
            if ext.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")):
                # construct the path to the image and yield it
                imagePaths.append('/uploads/'+filename)
    imagePaths = sorted(imagePaths,reverse=True)
    return render_template('home.html',imagens = imagePaths )


if __name__ == "__main__":
    app.debug = True
    app.run()
