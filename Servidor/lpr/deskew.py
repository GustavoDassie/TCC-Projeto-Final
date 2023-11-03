import numpy as np
from numpy._typing import _Shape
import cv2
from cv2.typing import MatLike
import math
from scipy.ndimage import _filters as filters


def angle(x: int, y: int):
    """
    Função para calcular o ângulo entre dois vetores
    """
    return int(math.atan2(float(y), float(x)) * 180.0 / 3.1415)


def v_rot(
    img: MatLike, angel: int, shape: _Shape, max_angel: int
) -> tuple[MatLike, MatLike]:
    """
    Função para realizar a rotação vertical
    """
    size_o = [shape[1], shape[0]]
    size = (
        shape[1] + int(shape[0] * np.cos((float(max_angel) / 180) * 3.14)),
        shape[0],
    )
    interval = abs(int(np.sin((float(angel) / 180) * 3.14) * shape[0]))
    pts1 = np.float32([[0, 0], [0, size_o[1]], [size_o[0], 0], [size_o[0], size_o[1]]])
    if angel > 0:
        pts2 = np.float32(
            [[interval, 0], [0, size[1]], [size[0], 0], [size[0] - interval, size_o[1]]]
        )
    else:
        pts2 = np.float32(
            [[0, 0], [interval, size[1]], [size[0] - interval, 0], [size[0], size_o[1]]]
        )

    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(img, M, size)
    return dst, M


def skew_detection(image_gray: MatLike):
    """
    Função para detecção de inclinação (skew)
    """
    h, w = image_gray.shape[:2]
    eigen = cv2.cornerEigenValsAndVecs(image_gray, 12, 5)
    angle_sur = np.zeros(180, np.uint)
    eigen = eigen.reshape(h, w, 3, 2)
    flow = eigen[:, :, 2]
    vis = image_gray.copy()
    vis[:] = (192 + np.uint32(vis)) / 2
    d = 12

    # Gere pontos de interesse em uma grade
    points = np.dstack(np.mgrid[d / 2 : w : d, d / 2 : h : d]).reshape(-1, 2)
    for x, y in points:
        vx, vy = np.int32(flow[int(y), int(x)] * d)
        ang = angle(vx, vy)

        # Aumente o contador de ângulo correspondente
        angle_sur[(ang + 180) % 180] += 1

    angle_sur = angle_sur.astype(np.float)

    # Normalize o histograma de ângulos
    angle_sur = (angle_sur - angle_sur.min()) / (angle_sur.max() - angle_sur.min())

    # Aplique um filtro gaussiano para suavização
    angle_sur = filters.gaussian_filter1d(angle_sur, 5)

    # Determine a inclinação vertical e horizontal
    skew_v_val = angle_sur[20 : 180 - 20].max()
    skew_v = angle_sur[30 : 180 - 30].argmax() + 30
    skew_h_A = angle_sur[0:30].max()
    skew_h_B = angle_sur[150:180].max()
    skew_h = 0

    # Verifique se há inclinação horizontal significativa
    if skew_h_A > skew_v_val * 0.3 or skew_h_B > skew_v_val * 0.3:
        if skew_h_A >= skew_h_B:
            skew_h = angle_sur[0:20].argmax()
        else:
            skew_h = -angle_sur[160:180].argmax()
    return skew_h, skew_v


def fastDeskew(image: MatLike):
    """
    Função para realizar o deskew rápido na imagem
    """
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, skew_v = skew_detection(image_gray)
    deskew, M = v_rot(image, int((90 - skew_v) * 1.5), image.shape, 60)
    return deskew, M
