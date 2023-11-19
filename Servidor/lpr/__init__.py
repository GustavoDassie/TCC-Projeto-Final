import cv2
from cv2 import dnn
from cv2.typing import MatLike

from matplotlib import pyplot as plt
import pytesseract
import numpy as np
from werkzeug.datastructures import FileStorage
import json
import re

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


def load_json(file_name: str) -> dict[str, dict[str, int]]:
    with open(file_name, "r") as arquivo_json:
        return json.load(arquivo_json)


DICT_ALL_FIX = load_json("./model/map_errors_plates.json")


class LPR:
    __verbose = False

    def __init__(self, verbose=False):
        self.__verbose = verbose

    def detect(self, frame: MatLike) -> tuple[MatLike, list[str]]:
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

    def __all_str_to_number(
        self,
        char: str,
        dicionario_erros: dict[str, dict[str, int]],
        variacoes: list[list[str]],
        index: int,
    ):
        new_variacoes = []
        for c in dicionario_erros:
            if c.isnumeric():
                if char in dicionario_erros[c]:
                    for var in variacoes:
                        new_variacoes.append(
                            [v if index != i else c for i, v in enumerate(var)]
                        )
        return new_variacoes

    def __all_number_to_str(
        self,
        char: str,
        dicionario_erros: dict[str, dict[str, int]],
        variacoes: list[list[str]],
        index: int,
    ) -> list[list[str]]:
        new_variacoes = []
        for c in dicionario_erros:
            if c.isupper():
                if char in dicionario_erros[c]:
                    for var in variacoes:
                        new_variacoes.append(
                            [v if index != i else c for i, v in enumerate(var)]
                        )
        return new_variacoes

    def __valida_padrao_placa(self, placa_list: list[str]) -> bool:
        # Use expressões regulares para validar o padrão da placa
        padrao_merc = r"^[A-Z]{3}\d[A-Z]\d{2}$"
        padrao_old = r"^[A-Z]{3}\d{4}$"
        placa = "".join(placa_list)
        if re.match(padrao_merc, placa) or re.match(padrao_old, placa):
            return True
        else:
            return False

    def all_correcoes_placa(self, placa: str):
        variacoes = [list(placa)]
        for i, char in enumerate(placa):
            if i <= 2 and not char.isupper():
                variacoes.extend(
                    self.__all_number_to_str(char, DICT_ALL_FIX, variacoes, i)
                )
            elif i != 4 and not char.isnumeric():
                variacoes.extend(
                    self.__all_str_to_number(char, DICT_ALL_FIX, variacoes, i)
                )

        variacoes = list(filter(self.__valida_padrao_placa, variacoes))
        # Calcular a confiança para cada variação
        confiancas = self.__calcular_confiancas(variacoes, placa, DICT_ALL_FIX)

        # Ordenar as variações com base na confiança
        variacoes_ordenadas = sorted(
            zip(variacoes, confiancas), key=lambda x: x[1], reverse=True
        )
        # Retornar as 5 variações mais prováveis
        return ["".join(newPlaca) for newPlaca, _ in variacoes_ordenadas[:5]]

    def __calcular_confiancas(
        self,
        variacoes: list[str],
        placa_original: str,
        dicionario_erros: dict[str, dict[str, int]],
    ) -> list[int]:
        confiancas = []
        for var in variacoes:
            confianca = 0
            for char_original, char_variacao in zip(placa_original, var):
                if char_original != char_variacao and char_variacao in dicionario_erros:
                    confianca += dicionario_erros[char_variacao].get(char_original, 0)
            confiancas.append(confianca)
        return confiancas
