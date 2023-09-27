# Exemplo de uso: python3 lpr.py --video=run.mp4
#                 python3 lpr.py --image=bird.jpg
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

# Inicializa os parâmetros
tiposPlaca = ["Azul", "Amarela", "Verde", "Branca", "Preta"]

fonteC = ImageFont.truetype("Font/platech.ttf", 38, 0)  # Carrega a fonte chinesa, 38 é o tamanho da fonte, 0 é a codificação unicode

larguraEntrada = 480  # 480  # de ssd.prototxt, 540, 960, 720, 640, 768
alturaEntrada = 640  # 640, 720, 1280, 960, 480, 1024
WHRatio = larguraEntrada / float(alturaEntrada)
fatorEscalaEntrada = 0.007843  # 1/127.5
valorMedio = 127.5

nomesClasses = ('fundo',
              'placa')

net = dnn.readNetFromCaffe("./model/MobileNetSSD_test.prototxt","./model/lpr.caffemodel")  # Lê os arquivos do modelo
net.setPreferableBackend(dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(dnn.DNN_TARGET_OPENCL)   # Ativa aceleração GPU OPENCL, padrão FP32
# net.setPreferableTarget(dnn.DNN_TARGET_OPENCL_FP16)   # somente para teste de placa de identificação de Xianka Intel com velocidade mais rápida

parser = argparse.ArgumentParser(description='Detecção de objetos usando SSD no OPENCV')
parser.add_argument('--image', help='Caminho para o arquivo de imagem.')
parser.add_argument('--video', help='Caminho para o arquivo de vídeo.')
args = parser.parse_args()

# Função para desenhar a caixa delimitadora da placa e os caracteres da placa e retornar a imagem marcada
def desenharPredicao(frame, label, esquerda, topo, direita, inferior):
    # Desenha a caixa delimitadora da placa.
    cv2.rectangle(frame, (esquerda, topo), (direita, inferior), (255, 178, 50), 2)

    img = Image.fromarray(frame)
    desenho = ImageDraw.Draw(img)
    desenho.text((esquerda + 1, topo - 28), label, (0, 0, 255), font=fonteC)  # Caracteres vermelhos acima da caixa da placa
    imagemX = np.array(img)
    return imagemX

# Pós-processamento dos resultados de detecção para determinar a placa de identificação mais adequada com base na confiança, etc.
def posProcessar(res_set):
    i = 0
    for placa, corPlaca, confianca in res_set[:]:  # Itera sobre a lista de placas copiadas
        if confianca < 0.8:
            res_set.remove([placa, corPlaca, confianca])
            continue
        if len(placa) != 7:
            res_set.remove([placa, corPlaca, confianca])
            continue
    return res_set

# Localiza a placa e reconhece os caracteres da placa na imagem de entrada, retorna a imagem com a placa marcada e os resultados de reconhecimento
def detectar(frame):

    frameRedimensionado = cv2.resize(frame, (larguraEntrada, alturaEntrada)); # Redimensiona a imagem original para as dimensões especificadas

    alturaFator = frame.shape[0] / alturaEntrada;  # Calcula o fator de escala da altura
    larguraFator = frame.shape[1] / larguraEntrada;

    t0 = time.time()
    blob = dnn.blobFromImage(frameRedimensionado, fatorEscalaEntrada, (larguraEntrada, alturaEntrada), valorMedio) # Lê a imagem
    net.setInput(blob)
    detecoes = net.forward()   # Localiza a placa
    # print("Tempo de localização da placa:", time.time() - t0)

    colunas = frameRedimensionado.shape[1]  # Largura da imagem redimensionada
    linhas = frameRedimensionado.shape[0]

    res_set = []
    # Itera sobre as placas localizadas
    for i in range(detecoes.shape[2]):
        confianca = detecoes[0, 0, i, 2]
        if confianca > 0.2:   # Confiança na localização da placa maior que um valor especificado
            id_classe = int(detecoes[0, 0, i, 1])

            xEsquerdaInferior = int(detecoes[0, 0, i, 3] * colunas) # Coordenada x do canto superior esquerdo da caixa de detecção da placa na imagem real
            yEsquerdaInferior = int(detecoes[0, 0, i, 4] * linhas)
            xDireitaSuperior = int(detecoes[0, 0, i, 5] * colunas)  # Coordenada x do canto inferior direito da caixa de detecção da placa na imagem real
            yDireitaSuperior = int(detecoes[0, 0, i, 6] * linhas)

            xEsquerdaInferior_ = int(larguraFator * xEsquerdaInferior); # Coordenada x do canto superior esquerdo da caixa de detecção da placa na imagem original
            yEsquerdaInferior_ = int(alturaFator * yEsquerdaInferior);
            xDireitaSuperior_ = int(larguraFator * xDireitaSuperior);
            yDireitaSuperior_ = int(alturaFator * yDireitaSuperior);
            # print("y1:", yEsquerdaInferior_, "y2:", yDireitaSuperior_, "x1:", xEsquerdaInferior_, "x2:", xDireitaSuperior_)  # Saída das informações de localização da placa na imagem original
            # Amplia a caixa de localização da placa
            h = yDireitaSuperior_ - yEsquerdaInferior_
            w = xDireitaSuperior_ - xEsquerdaInferior_
            yEsquerdaInferior_ -= int(h * 0.5)
            yDireitaSuperior_ += int(h * 0.5)
            xEsquerdaInferior_ -= int(w * 0.14)
            xDireitaSuperior_ += int(w * 0.14)

           # cv2.rectangle(frame, (xEsquerdaInferior_-2, yEsquerdaInferior_-2), (xDireitaSuperior_+2, yDireitaSuperior_+2),(0, 0,255))    # Desenha uma borda vermelha na posição da placa

            imagem_sub = frame[yEsquerdaInferior_:yDireitaSuperior_, xEsquerdaInferior_:xDireitaSuperior_] # Recorta a região de localização da placa na imagem original

            # A placa deve ser ajustada para o mesmo tamanho
            placa = imagem_sub
            # print(placa.shape[0],placa.shape[1])
            if placa.shape[0] > 36:
                placa = cv2.resize(imagem_sub, (136, 36 * 2))
            else:
                placa = cv2.resize(imagem_sub, (136, 36 ))
          #  cv2.imshow("test", plate)
          #  cv2.waitKey(0)
            # Determina a cor da placa
            tipoPlaca = pp.td.SimplePredict(placa)
            corPlaca = tiposPlaca[tipoPlaca]

            if (tipoPlaca > 0) and (tipoPlaca < 5):
                placa = cv2.bitwise_not(placa)


            # Refinamento preciso, correção de inclinação
            imagem_rgb = pp.fm.findContoursAndDrawBoundingBox(placa)
           # cv2.imshow("test", image_rgb);
           # cv2.waitKey(0)
            # Correção das bordas esquerda e direita da placa
            imagem_rgb = pp.fv.finemappingVertical(imagem_rgb)
           # cv2.imshow("test", image_rgb);
           # cv2.waitKey(0)
            # Reconhecimento de caracteres da placa
            t0 = time.time()
            placaE2E, confiancaE2E = pp.e2e.recognizeOne(imagem_rgb)
          #  print("e2e:", placaE2E, confiancaE2E, corPlaca)   # Julgamento dos caracteres da placa
          #  print("Tempo de reconhecimento dos caracteres da placa:", time.time()-t0)

            frame  = desenharPredicao(frame, placaE2E, xEsquerdaInferior_, yEsquerdaInferior_, xDireitaSuperior_, yDireitaSuperior_)

            res_set.append([placaE2E,
                            corPlaca,
                            confiancaE2E])
    return frame , res_set

# Gira a imagem em torno do centro da imagem para um ângulo especificado
def girar(imagem, grau):
    (h, w) = imagem.shape[:2]
    centro = (w / 2, h / 2)
    # Gira a imagem em 180 graus
    M = cv2.getRotationMatrix2D(centro, grau, 1.0)
    girada = cv2.warpAffine(imagem, M, (w, h))
    return girada

# Processa as entradas
nomeJanela = 'Detecção de objetos de aprendizado profundo no OpenCV'
cv2.namedWindow(nomeJanela, cv2.WINDOW_NORMAL)

arquivoSaida = "ssd_out_py.avi" # Define o nome do arquivo de saída
if (args.image):
    # Abre o arquivo de imagem
    if not os.path.isfile(args.image):
        print("O arquivo de imagem de entrada ", args.image, " não existe")
        sys.exit(1)
    cap = cv2.VideoCapture(args.image)
    arquivoSaida = args.image[:-4] + '_ssd_out_py.jpg'
elif (args.video):
    # Abre o arquivo de vídeo
    if not os.path.isfile(args.video):
        print("O arquivo de vídeo de entrada ", args.video, " não existe")
        sys.exit(1)
    cap = cv2.VideoCapture(args.video)
    arquivoSaida = args.video[:-4] + '_ssd_out_py.avi'
else:
    # Entrada da câmera
    cap = cv2.VideoCapture(0)

# print("w:",cap.get(cv2.CAP_PROP_FRAME_WIDTH),"h:",cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Inicializa o escritor de vídeo para salvar o vídeo de saída
if (not args.image):
    vid_writer = cv2.VideoWriter(arquivoSaida, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30,
                                (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while cv2.waitKey(1) < 0:

    # Obtém o quadro do vídeo
    temFrame, frame = cap.read()

    # Para o programa se o final do vídeo for alcançado
    if not temFrame:
        print("Processamento concluído!")
        print("O arquivo de saída foi armazenado em: ", arquivoSaida)
        cv2.waitKey(3000)
        break

    # Rotação da imagem em 90 graus, apenas para arquivos de vídeo de teste
    if  args.video.find("test")!=-1:
        frame = girar(frame, -90)

    t0 = time.time();
    frame, res = detectar(frame)

    # Saída do tempo de detecção da placa no canto superior esquerdo da imagem
    label = ' %.0f ms' % ((time.time()-t0)*1000)
    cv2.putText(frame, label, (int(frame.shape[1]/4), 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255))
    # Pós-processamento da placa, filtragem de placas não qualificadas
    res = posProcessar(res)
    # Saída de informações de detecção da placa
    info = ""
    for placa, corPlaca, confianca in res:
        info = placa + corPlaca+" "
    if len(info) > 1:
        print(info, label)

    # Escreve o quadro com as caixas de detecção
    if (args.image):
        cv2.imwrite(arquivoSaida, frame.astype(np.uint8))
    else:
        vid_writer.write(frame.astype(np.uint8))

    cv2.imshow(nomeJanela, frame)

cap.release()
vid_writer.release()
cv2.destroyAllWindows()
