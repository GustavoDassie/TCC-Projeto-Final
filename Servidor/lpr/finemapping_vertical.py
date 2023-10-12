from keras.layers import Conv2D, Input, MaxPool2D, Activation, Flatten, Dense
from keras.models import Model
import numpy as np
import cv2


def getModel():
    """
    Função para criar o modelo da rede neural
    """
    # Defina a entrada da rede com dimensões 16x66x3 (16 de altura, 66 de largura e 3 canais de cor)
    input = Input(shape=[16, 66, 3])
    # Camada de convolução com 10 filtros de 3x3, passo de 1, preenchimento 'valid' e nome 'conv1'
    x = Conv2D(10, (3, 3), strides=1, padding="valid", name="conv1")(input)
    x = Activation("relu", name="relu1")(x)  # Ativação ReLU
    x = MaxPool2D(pool_size=2)(x)  # Camada de pooling (max pooling)

    # Outra camada de convolução com 16 filtros de 3x3, nome 'conv2'
    x = Conv2D(16, (3, 3), strides=1, padding="valid", name="conv2")(x)
    x = Activation("relu", name="relu2")(x)  # Ativação ReLU

    # Camada de convolução com 32 filtros de 3x3, nome 'conv3'
    x = Conv2D(32, (3, 3), strides=1, padding="valid", name="conv3")(x)
    x = Activation("relu", name="relu3")(x)  # Ativação ReLU
    x = Flatten()(x)  # Aplanamento dos dados

    output = Dense(2, name="dense")(x)  # Camada densa com 2 unidades
    output = Activation("relu", name="relu4")(output)  # Ativação ReLU
    model = Model([input], [output])  # Criação do modelo
    return model


# Criação do modelo da rede neural
model = getModel()
model.load_weights("./model/model12.h5")  # Carregamento dos pesos pré-treinados


def finemappingVertical(image):
    """
    Função para realizar o mapeamento  na direção vertical
    """
    # Redimensiona a imagem para 66x16 e normaliza
    resized = cv2.resize(image, (66, 16))
    resized = resized.astype(np.float) / 255

    # Realiza a previsão do modelo para mapeamento na direção vertical
    res = model.predict(np.array([resized]))[0]

    # Escala os valores de saída para as dimensões originais da imagem
    res = res * image.shape[1]
    res = res.astype(np.int)
    H, T = res
    H -= 3
    T += 2

    if H < 0:
        H = 0

    if T >= image.shape[1] - 1:
        T = image.shape[1] - 1

    # Recorta a região mapeada
    image = image[0:35, H : T + 2]

    # Redimensiona a imagem para 136x36
    image = cv2.resize(image, (int(136), int(36)))

    return image
