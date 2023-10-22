import cv2
from cv2 import dnn
from cv2.typing import MatLike

from matplotlib import pyplot as plt
import pytesseract
import numpy as np
from werkzeug.datastructures import FileStorage

from . import finemapping as fm
from . import finemapping_vertical as fv

LARGURA_ENTRADA = 480
ALTURA_ENTRADA = 640

FATOR_DE_ESCALA_ENTRADA = 0.007843
VALOR_MEDIO = 127.5

# Lê o arquivo de modelo
REDE = dnn.readNetFromCaffe(
    "./model/MobileNetSSD_test.prototxt", "./model/lpr.caffemodel"
)
REDE.setPreferableBackend(dnn.DNN_BACKEND_OPENCV)

# Ativar aceleracao GPU OPENCL, padrao FP32
REDE.setPreferableTarget(dnn.DNN_TARGET_OPENCL)


class LRP:
    __verbose = False

    def __init__(self, verbose=False):
        self.__verbose = verbose

    def detect(self, frame: MatLike):
        """
        Localiza placas e reconhece os caracteres da placa a partir da imagem de entrada\n
        Retornando a imagem marcada e os resultados de reconhecimento da placa
        """

        # Redimensiona a imagem original para a largura e altura especificadas
        frame_redimensionado = cv2.resize(frame, (LARGURA_ENTRADA, ALTURA_ENTRADA))

        # Calcula a proporcao de redimensionamento da altura
        fatorAltura = frame.shape[0] / ALTURA_ENTRADA
        fatorLargura = frame.shape[1] / LARGURA_ENTRADA

        # Lê a imagem
        blob = dnn.blobFromImage(
            frame_redimensionado,
            FATOR_DE_ESCALA_ENTRADA,
            (LARGURA_ENTRADA, ALTURA_ENTRADA),
            VALOR_MEDIO,
        )
        REDE.setInput(blob)

        # Localiza a placa
        deteccoes = REDE.forward()

        # Largura da imagem redimensionada
        colunas = frame_redimensionado.shape[1]
        linhas = frame_redimensionado.shape[0]

        resultados = []

        # Percorre as placas localizadas
        for i in range(deteccoes.shape[2]):
            confianca = deteccoes[0, 0, i, 2]

            # Confianca na localizacao da placa é maior que o valor especificado
            if confianca > 0.2:
                # Coordenada x do ponto inferior esquerdo da caixa da placa na imagem detectada
                xEsquerdaInferior = int(deteccoes[0, 0, i, 3] * colunas)
                yEsquerdaInferior = int(deteccoes[0, 0, i, 4] * linhas)

                # Coordenada x do ponto inferior direito da caixa da placa na imagem detectada
                xDireitaSuperior = int(deteccoes[0, 0, i, 5] * colunas)
                yDireitaSuperior = int(deteccoes[0, 0, i, 6] * linhas)

                # Coordenada x do ponto superior esquerdo da caixa da placa na imagem original
                xEsquerdaInferior_ = int(fatorLargura * xEsquerdaInferior)
                yEsquerdaInferior_ = int(fatorAltura * yEsquerdaInferior)

                # Coordenada x do ponto superior direito da caixa da placa na imagem original
                xDireitaSuperior_ = int(fatorLargura * xDireitaSuperior)
                yDireitaSuperior_ = int(fatorAltura * yDireitaSuperior)

                # Aumenta a caixa delimitadora da placa
                h = yDireitaSuperior_ - yEsquerdaInferior_
                w = xDireitaSuperior_ - xEsquerdaInferior_

                yEsquerdaInferior_ -= int(h * 0.5)
                yDireitaSuperior_ += int(h * 0.5)

                xEsquerdaInferior_ -= int(w * 0.14)
                xDireitaSuperior_ += int(w * 0.14)

                # Recorta a área de localizacao da placa na imagem original
                imagem_recorte = frame[
                    yEsquerdaInferior_:yDireitaSuperior_,
                    xEsquerdaInferior_:xDireitaSuperior_,
                ]
                if self.__verbose:
                    plt.imshow(imagem_recorte, cmap="gray")
                    plt.show()

                # Deve ajustar todas as placas para o mesmo tamanho
                placa = imagem_recorte

                if placa.shape[0] > 36:
                    placa = cv2.resize(imagem_recorte, (136, 36 * 2))
                else:
                    placa = cv2.resize(imagem_recorte, (136, 36))

                if self.__verbose:
                    plt.imshow(placa, cmap="gray")
                    plt.show()

                # Precisao de localizacao, correcao de inclinacao
                imagem_rgb = fm.findContoursAndDrawBoundingBox(placa, self.__verbose)

                if self.__verbose:
                    plt.imshow(imagem_rgb, cmap="gray")
                    plt.show()

                imagem_rgb = fv.finemappingVertical(imagem_rgb)

                if self.__verbose:
                    plt.imshow(imagem_rgb, cmap="gray")
                    plt.show()

                resultado = cv2.cvtColor(imagem_rgb, cv2.COLOR_BGR2GRAY)
                resultado = cv2.GaussianBlur(resultado, (3, 3), 0)

                if self.__verbose:
                    plt.imshow(resultado, cmap="gray")
                    plt.show()

                # Reconhecimento dos caracteres da placa
                pytesseract.pytesseract.tesseract_cmd = (
                    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                )
                caracs = pytesseract.image_to_string(
                    resultado,
                    lang="eng",
                    config="--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                )
                if self.__verbose:
                    print(caracs)

                resultados.append(caracs)
        return frame, resultados

    def detectFromFileStorage(self, file: FileStorage):
        """
        Localiza placas e reconhece os caracteres da placa a partir de um FileStorage de entrada\n
        Retornando a imagem marcada e os resultados de reconhecimento da placa
        """
        bites = file.stream.read()

        nparr = np.fromstring(bites, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame, charset = self.detect(img)
        return bites, frame, charset
