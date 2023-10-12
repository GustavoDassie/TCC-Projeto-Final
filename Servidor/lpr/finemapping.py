import cv2
import numpy as np
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt
from . import deskew


def fitLine_ransac(pts, zero_add=0):
    """
    Função para ajustar uma linha usando o método RANSAC
    """
    if len(pts) >= 2:
        # Ajuste uma linha usando o método RANSAC
        [vx, vy, x, y] = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01)
        lefty = int((-x * vy / vx) + y)
        righty = int(((136 - x) * vy / vx) + y)
        # Adicione um deslocamento (zero_add) e retorne os pontos extremos da linha
        return lefty + 30 + zero_add, righty + 30 + zero_add
    return 0, 0


def findContoursAndDrawBoundingBox(image_rgb, verbose=False):
    """
    Função para encontrar contornos e desenhar caixas delimitadoras
    """

    line_upper = []
    line_lower = []
    line_experiment = []

    # Converta a imagem de cores para escala de cinza
    gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

    # Itere sobre diferentes valores de 'k' para aplicar limiarização adaptativa
    for k in np.linspace(-50, 0, 10):
        
        # Aplique a limiarização adaptativa para binarizar a imagem
        binary_niblack = cv2.adaptiveThreshold(
            gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 17, k
        )

        # Encontre os contornos na imagem binarizada
        contours, hierarchy = cv2.findContours(
            binary_niblack.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )

        image_rgb2 = image_rgb.copy()
        cv2.drawContours(image_rgb2, contours, -1, (0, 0, 255), 2)
        if verbose:
            imshow(image_rgb2, cmap="gray")
            plt.show()

        # Itere sobre os contornos encontrados
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 30 and area < 300:
                bdbox = cv2.boundingRect(contour)
                # Verifique critérios para considerar a caixa delimitadora
                if (
                    bdbox[3] / float(bdbox[2]) > 0.7
                    and bdbox[3] * bdbox[2] > 100
                    and bdbox[3] * bdbox[2] < 1200
                ) or (bdbox[3] / float(bdbox[2]) > 3 and bdbox[3] * bdbox[2] < 100):
                    if verbose:
                        print(area)
                    # Adicione as coordenadas das caixas delimitadoras às listas
                    line_upper.append([bdbox[0], bdbox[1]])
                    line_lower.append([bdbox[0] + bdbox[2], bdbox[1] + bdbox[3]])

                    line_experiment.append([bdbox[0], bdbox[1]])
                    line_experiment.append([bdbox[0] + bdbox[2], bdbox[1] + bdbox[3]])

    # Adicione uma borda à imagem
    rgb = cv2.copyMakeBorder(image_rgb, 30, 30, 0, 0, cv2.BORDER_REPLICATE)

    # Encontre as linhas superiores e inferiores usando RANSAC
    leftyA, rightyA = fitLine_ransac(np.array(line_lower), 3)
    leftyB, rightyB = fitLine_ransac(np.array(line_upper), -3)

    _, cols = rgb.shape[:2]

    if verbose:
        rgb2 = cv2.copyMakeBorder(image_rgb, 30, 30, 0, 0, cv2.BORDER_REPLICATE)
        rgb2 = cv2.line(
            rgb2, (cols - 1, rightyA), (0, leftyA), (0, 0, 255), 1, cv2.LINE_AA
        )
        rgb2 = cv2.line(
            rgb2, (cols - 1, rightyB), (0, leftyB), (0, 255, 0), 1, cv2.LINE_AA
        )
        imshow(rgb2, cmap="gray")
        plt.show()

    # Crie uma matriz de projeção para corrigir a perspectiva
    pts_map1 = np.float32(
        [[cols - 1, rightyA], [0, leftyA], [cols - 1, rightyB], [0, leftyB]]
    )
    pts_map2 = np.float32([[136, 36], [0, 36], [136, 0], [0, 0]])
    mat = cv2.getPerspectiveTransform(pts_map1, pts_map2)

    # Aplique a correção de perspectiva na imagem
    image = cv2.warpPerspective(rgb, mat, (136, 36), flags=cv2.INTER_CUBIC)

    image, M = deskew.fastDeskew(image)

    return image
