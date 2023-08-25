import cv2
import pytesseract
from PIL import Image
import string
import re
import numpy as np


class LerPlaca:
    def __init__(self):
        image = ""

    # get grayscale image
    def get_grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(self, image):
        return cv2.medianBlur(image, 5)

    # thresholding
    def thresholding(self, image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation
    def dilate(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

    # erosion
    def erode(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    # opening - erosion followed by dilation
    def opening(self, image):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    def canny(self, image):
        return cv2.Canny(image, 100, 200)

    # skew correction
    def deskew(self, image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    # template matching
    def match_template(self, image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

    def isolar_cor(self, imagem):
        # Converta a imagem para o espaço de cores HSV
        hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

        # Defina os limites inferior e superior para a cor preta em HSV
        limite_inferior_preto = np.array([0, 0, 0])
        limite_superior_preto = np.array(
            [190, 100, 100]
        )  # Aumente o valor de V para tornar a correspondência mais tolerante

        # Crie uma máscara para identificar a cor preta na imagem
        mascara_preto = cv2.inRange(hsv, limite_inferior_preto, limite_superior_preto)

        # Substitua todos os pixels não pretos por branco usando bitwise_not
        resultado = cv2.bitwise_not(mascara_preto)

        return resultado
    
    def detect_license_plate(self,image_path):
        try:
            # Carrega a imagem usando o OpenCV
            image = cv2.imread(image_path)

            # Converte a imagem para tons de cinza
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Realiza a binarização da imagem para destacar os contornos
            _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

            # Encontra os contornos na imagem binarizada
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Filtra os contornos para encontrar a região da placa
            max_area = 0
            license_plate_contour = None
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    max_area = area
                    license_plate_contour = contour

            # Desenha o contorno da placa na imagem original (apenas para visualização)
            if license_plate_contour is not None:
                cv2.drawContours(image, [license_plate_contour], -1, (0, 255, 0), 2)

            # Opcional: Salva a imagem com o contorno desenhado (apenas para visualização)
            cv2.imwrite("result.jpg", image)

            # Retorna o contorno da placa (ou None se não foi encontrada)
            return license_plate_contour
        except Exception as e:
            return None

    def ler(self, image):
        img = cv2.imread(
            r"C:\Users\gusta\Documentos\IFSP\TCC\TCC-novo\jupiter\Placa.png"
        )
        #teste 2
        imagem_isolada = self.isolar_cor(img)
        #(T, bin) = cv2.threshold(imagem_isolada,  0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((5,5),np.uint8)
        open = cv2.morphologyEx(imagem_isolada, cv2.MORPH_OPEN, kernel)
        resize = cv2.resize(open, (300, 80))
        # teste
        # gray = self.get_grayscale(img)
        # gray = self.thresholding(gray)
        # gray = cv2.resize(gray, (300, 200))
        # gray = self.opening(gray)
        # gray = cv2.GaussianBlur(gray, (3, 3), 1000)
        # gray = self.erode(gray)
        # normal
        # gray = self.get_grayscale(img)
        # gray = cv2.GaussianBlur(gray, (9, 9), 1000)

        # gray = self.thresholding(gray)
        # gray = self.opening(gray)
        # # gray = canny(gray)
        # gray = cv2.resize(gray, (300, 200))
        # gray = cv2.GaussianBlur(gray, (9, 9), 1000)
        cv2.imwrite("test.jpg", resize)
        # normal
        # img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        # (T, Thresh1) = cv2.threshold(img, 40, 50, cv2.THRESH_TRUNC)
        # (T, Thresh3) = cv2.threshold(Thresh1, 26, 44, cv2.THRESH_BINARY)
        # (T, Thresh2) = cv2.threshold(Thresh3, 0, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        # (T, Thresh4) = cv2.threshold(Thresh2, 30, 255, cv2.CALIB_CB_ADAPTIVE_THRESH)
        # pronta = cv2.resize(Thresh4, (300, 200))
        # pronta1 = cv2.GaussianBlur(pronta, (9, 9), 1000)
        # cv2.imwrite("merc.jpg", pronta1)
        pytesseract.pytesseract.tesseract_cmd = (
            "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        )
        caracs = pytesseract.image_to_string(
            Image.open("test.jpg"),
            lang="eng",
        )
        letras = caracs[:3]
        num = caracs[4:8]
        num = num.replace("O", "0")
        num = num.replace("I", "1")
        letras = letras.replace("0", "O")
        letras = letras.replace("1", "I")
        num = num.replace("G", "6")
        letras = letras.replace("6", "G")
        num = num.replace("B", "3")
        letras = letras.replace("3", "B")
        num = num.replace("T", "1")
        letras = letras.replace("1", "T")
        print("Os caracteres presente na placa são: " + caracs)
        print("A placa é (com modificações): " + letras + "-" + num)


t = LerPlaca()
plate_contour = t.detect_license_plate(r"C:\Users\gusta\Documentos\IFSP\TCC\TCC-novo\jupiter\testeLegitimo.jpg")
if plate_contour is not None:
    print("Placa encontrada!",plate_contour)
else:
    print("Placa não encontrada ou não detectada corretamente.")
t.ler("")
