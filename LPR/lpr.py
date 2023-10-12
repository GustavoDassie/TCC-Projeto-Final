# Exemplo de uso: python3 lpr.py --video=executar.mp4
#                 python3 lpr.py --image=passaro.jpg
# coding=utf-8

from cv2 import dnn
import cv2
import argparse
import sys
import numpy as np
import os.path
from hyperlpr_py3 import pipline as pp
import time
from PIL import Image, ImageDraw, ImageFont
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt
import pytesseract
from PIL import Image

# Inicialize os parâmetros
tiposDePlacas = ["蓝", "黄", "绿", "白", "黑 "]

fonteC = ImageFont.truetype("Font/platech.ttf", 38, 0)  # Carregue a fonte chinesa, 38 é o tamanho da fonte, 0 é o código Unicode

larguraEntrada = 480  # 480  # de ssd.prototxt, 540, 960, 720, 640, 768
alturaEntrada = 640  # 640, 720, 1280, 960, 480, 1024
taxaDeAspecto = larguraEntrada / float(alturaEntrada)
fatorDeEscalaEntrada = 0.007843  # 1/127.5
valorMédio = 127.5

classNames = ('background',
              'plate')

rede = dnn.readNetFromCaffe("./model/MobileNetSSD_test.prototxt", "./model/lpr.caffemodel")  # Lê o arquivo de modelo
rede.setPreferableBackend(dnn.DNN_BACKEND_OPENCV)
rede.setPreferableTarget(dnn.DNN_TARGET_OPENCL)  # Ativar aceleração GPU OPENCL, padrão FP32
# rede.setPreferableTarget(dnn.DNN_TARGET_OPENCL_FP16)   # apenas para teste de xianka da Intel para velocidade mais rápida

analizadorDeArgumentos = argparse.ArgumentParser(description='Detecção de objetos usando SSD no OPENCV')
analizadorDeArgumentos.add_argument('--image', help='Caminho para o arquivo de imagem.')
analizadorDeArgumentos.add_argument('--video', help='Caminho para o arquivo de vídeo.')
argumentos = analizadorDeArgumentos.parse_args()

# Função para desenhar a caixa delimitadora da placa e os caracteres da placa reconhecidos e retornar a imagem marcada
def desenharPrevisão(frame, label, esquerda, topo, direita, fundo):
    # Desenhe a borda da placa.
    cv2.rectangle(frame, (esquerda, topo), (direita, fundo), (255, 178, 50), 2)

    img = Image.fromarray(frame)
    desenho = ImageDraw.Draw(img)
    desenho.text((esquerda + 1, topo - 28), label, (0, 0, 255), font=fonteC)  # Caracteres chineses vermelhos acima da caixa da placa
    imagem_x = np.array(img)
    return imagem_x

# Pós-processamento dos resultados da detecção para determinar a melhor placa reconhecida com base na confiança, etc.
def pósProcessar(resultados):
    i = 0
    for placa, corDaPlaca, confiança in resultados[:]:  # Percorra a lista de placas copiada
        if confiança < 0.8:
            resultados.remove([placa, corDaPlaca, confiança])
            continue
        if len(placa) != 7:
            resultados.remove([placa, corDaPlaca, confiança])
            continue

    return resultados

# Localiza placas e reconhece os caracteres da placa a partir da imagem de entrada, retornando a imagem marcada e os resultados de reconhecimento da placa
def detectar(frame):

    frame_redimensionado = cv2.resize(frame, (larguraEntrada, alturaEntrada)); # Redimensiona a imagem original para a largura e altura especificadas
    # cv2.imshow("test", frame_redimensionado);
    # cv2.waitKey(0);

    fatorAltura = frame.shape[0] / alturaEntrada;  # Calcula a proporção de redimensionamento da altura
    fatorLargura = frame.shape[1] / larguraEntrada;

    t0 = time.time()
    blob = dnn.blobFromImage(frame_redimensionado, fatorDeEscalaEntrada, (larguraEntrada, alturaEntrada), valorMédio) # Lê a imagem
    rede.setInput(blob)
    detecções = rede.forward()   # Localiza a placa
    # print("Tempo de localização da placa:", time.time() - t0)

    colunas = frame_redimensionado.shape[1]  # Largura da imagem redimensionada
    linhas = frame_redimensionado.shape[0]

    resultados = []
    # Percorre as placas localizadas
    for i in range(detecções.shape[2]):
        confiança = detecções[0, 0, i, 2]
        if confiança > 0.2:   # Confiança na localização da placa é maior que o valor especificado
            classe_id = int(detecções[0, 0, i, 1])

            xEsquerdaInferior = int(detecções[0, 0, i, 3] * colunas) # Coordenada x do ponto superior esquerdo da caixa da placa na imagem detectada
            yEsquerdaInferior = int(detecções[0, 0, i, 4] * linhas)
            xDireitaSuperior = int(detecções[0, 0, i, 5] * colunas)  # Coordenada x do ponto inferior direito da caixa da placa na imagem detectada
            yDireitaSuperior = int(detecções[0, 0, i, 6] * linhas)

            xEsquerdaInferior_ = int(fatorLargura * xEsquerdaInferior); # Coordenada x do ponto superior esquerdo da caixa da placa na imagem original
            yEsquerdaInferior_ = int(fatorAltura * yEsquerdaInferior);
            xDireitaSuperior_ = int(fatorLargura * xDireitaSuperior);
            yDireitaSuperior_ = int(fatorAltura * yDireitaSuperior);
            # print("y1:", yEsquerdaInferior_, "y2:", yDireitaSuperior_, "x1:", xEsquerdaInferior_, "x2:", xDireitaSuperior_)  # Saída das informações de posição da placa na imagem original
            # Aumenta a caixa delimitadora da placa
            h = yDireitaSuperior_ - yEsquerdaInferior_
            w = xDireitaSuperior_ - xEsquerdaInferior_
            yEsquerdaInferior_ -= int(h * 0.5)
            yDireitaSuperior_ += int(h * 0.5)
            xEsquerdaInferior_ -= int(w * 0.14)
            xDireitaSuperior_ += int(w * 0.14)

            # cv2.rectangle(frame, (xEsquerdaInferior_-2, yEsquerdaInferior_-2), (xDireitaSuperior_+2, yDireitaSuperior_+2),(0, 0,255))    # Desenha uma borda vermelha em torno da posição da placa

            imagem_recorte = frame[yEsquerdaInferior_:yDireitaSuperior_, xEsquerdaInferior_:xDireitaSuperior_] # Recorta a área de localização da placa na imagem original
            imshow(imagem_recorte,cmap="gray")
            plt.show()
            # Deve ajustar todas as placas para o mesmo tamanho
            placa = imagem_recorte
            
            # rotated_image1 = placa.rotate(-18)
            # imshow(rotated_image1,cmap="gray")
            # plt.show()
            # print(placa.shape[0],placa.shape[1])
            if placa.shape[0] > 36:
                placa = cv2.resize(imagem_recorte, (136, 36 * 2))
            else:
                placa = cv2.resize(imagem_recorte, (136, 36 ))
            imshow(placa,cmap="gray")
            plt.show()
            # cv2.imshow("test", placa)
            # cv2.waitKey(0)
            # Determina a cor da placa
            tipoDaPlaca = pp.td.SimplePredict(placa)
            corDaPlaca = tiposDePlacas[tipoDaPlaca]

            # if (tipoDaPlaca > 0) and (tipoDaPlaca < 5):
            #     placa = cv2.bitwise_not(placa)

            # Precisão de localização, correção de inclinação
            imagem_rgb = pp.fm.findContoursAndDrawBoundingBox(placa)
            imshow(imagem_rgb,cmap="gray")
            plt.show()
            # cv2.imshow("test", imagem_rgb);
            # cv2.waitKey(0)
            # Correção das bordas esquerda e direita da placa
            imagem_rgb = pp.fv.finemappingVertical(imagem_rgb)
            imshow(imagem_rgb,cmap="gray")
            plt.show()
            resultado = cv2.cvtColor(imagem_rgb, cv2.COLOR_BGR2GRAY)
            resultado = cv2.GaussianBlur(resultado,(3,3),0)
            imshow(resultado,cmap="gray")
            plt.show()
            # hsv = cv2.cvtColor(resultado, cv2.COLOR_BGR2HSV)

            # # Defina os limites inferior e superior para a cor preta em HSV
            # limite_inferior_preto = np.array([0, 0, 0])
            # limite_superior_preto = np.array(
            #     [190, 100, 100]
            # )  # Aumente o valor de V para tornar a correspondência mais tolerante

            # # Crie uma máscara para identificar a cor preta na imagem
            # mascara_preto = cv2.inRange(hsv, limite_inferior_preto, limite_superior_preto)

            # # Substitua todos os pixels não pretos por branco usando bitwise_not
            # resultado = cv2.bitwise_not(mascara_preto)
            # imshow(resultado,cmap="gray")
            # plt.show()
            
            pytesseract.pytesseract.tesseract_cmd = ("C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
            caracs = pytesseract.image_to_string(resultado,
                lang="eng",config ='--oem 3 -l eng --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )
            print(caracs)
            # cv2.imshow("test", imagem_rgb);
            # cv2.waitKey(0)
            # Reconhecimento dos caracteres da placa
            t0 = time.time()
            placaCompleta, confiançaPlaca = pp.e2e.recognizeOne(imagem_rgb)
            # print("e2e:", placaCompleta, confiançaPlaca, corDaPlaca)   # Determina os caracteres da placa
            # print("Tempo de reconhecimento dos caracteres da placa:", time.time()-t0)

            frame  = desenharPrevisão(frame, placaCompleta, xEsquerdaInferior_, yEsquerdaInferior_, xDireitaSuperior_, yDireitaSuperior_)

            resultados.append([placaCompleta,
                            corDaPlaca,
                            confiançaPlaca])
    return frame , resultados

# Gire a imagem em torno do centro da imagem para o ângulo especificado
def girar(imagem, grau):
    (h, w) = imagem.shape[:2]
    centro = (w / 2, h / 2)
    # Gire a imagem em 180 graus
    M = cv2.getRotationMatrix2D(centro, grau, 1.0)
    girada = cv2.warpAffine(imagem, M, (w, h))
    return girada

# Processa as entradas
# nomeJanela = 'Detecção de objetos com aprendizado profundo no OpenCV'
# cv2.namedWindow(nomeJanela, cv2.WINDOW_NORMAL)

arquivoDeSaida = "ssd_out_py.avi" # Define o nome do arquivo de saída
if (argumentos.image):
    # Abra o arquivo de imagem
    if not os.path.isfile(argumentos.image):
        print("O arquivo de imagem de entrada ", argumentos.image, " não existe")
        sys.exit(1)
    captura = cv2.VideoCapture(argumentos.image)
    arquivoDeSaida = argumentos.image[:-4] + '_ssd_out_py.jpg'
elif (argumentos.video):
    # Abra o arquivo de vídeo
    if not os.path.isfile(argumentos.video):
        print("O arquivo de vídeo de entrada ", argumentos.video, " não existe")
        sys.exit(1)
    captura = cv2.VideoCapture(argumentos.video)
    arquivoDeSaida = argumentos.video[:-4] + '_ssd_out_py.avi'
else:
    # Entrada da câmera
    captura = cv2.VideoCapture(0)

# print("largura:", captura.get(cv2.CAP_PROP_FRAME_WIDTH), "altura:", captura.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Inicializa o gravador de vídeo para salvar o vídeo de saída
if (not argumentos.image):
    escritorDeVídeo = cv2.VideoWriter(arquivoDeSaida, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                                (round(captura.get(cv2.CAP_PROP_FRAME_WIDTH)), round(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while cv2.waitKey(1) < 0:

    # Obtenha um quadro do vídeo
    temQuadro, quadro = captura.read()

    # Pare o programa se chegou ao final do vídeo
    if not temQuadro:
        print("Processamento concluído!")
        print("O arquivo de saída está armazenado em: ", arquivoDeSaida)
        cv2.waitKey(3000)
        break

    # Gire a imagem em 90 graus, apenas para arquivos de vídeo de teste
    if  (argumentos.video and argumentos.video.find("test")!=-1):
        quadro = girar(quadro, -90)

    t0 = time.time();
    quadro, resultados = detectar(quadro)

    # Imprima o tempo de detecção da placa no canto superior esquerdo da imagem
    etiqueta = ' %.0f ms' % ((time.time()-t0)*1000)
    cv2.putText(quadro, etiqueta, (int(quadro.shape[1]/4), 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255))
    # Pós-processamento das placas, filtrando placas não válidas
    resultados = pósProcessar(resultados)
    # Imprima informações de detecção de placa
    informações = ""
    for placa, corDaPlaca, confiança in resultados:
        informações = placa + corDaPlaca+" "
    if len(informações) > 1:
        print(informações, etiqueta)

    # Escreva o quadro com as caixas de detecção
    if (argumentos.image):
        cv2.imwrite(arquivoDeSaida, quadro.astype(np.uint8))
    else:
        escritorDeVídeo.write(quadro.astype(np.uint8))

    # cv2.imshow(nomeJanela, quadro)

if (argumentos.image):
    captura.release()
if (not argumentos.image):
    escritorDeVídeo.release()
cv2.destroyAllWindows()
