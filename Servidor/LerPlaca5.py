import cv2
import pytesseract
from PIL import Image
import imutils
import string
import re
import numpy as np
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt

class LerPlaca:
    def __init__(self):
        image = ""
    # get grayscale image
    def get_grayscale(self,image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # noise removal
    def remove_noise(self,image):
        return cv2.medianBlur(image,5)
    
    #thresholding
    def thresholding(self,image):
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    #dilation
    def dilate(self,image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.dilate(image, kernel, iterations = 1)
        
    #erosion
    def erode(self,image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.erode(image, kernel, iterations = 1)

    #opening - erosion followed by dilation
    def opening(self,image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    #canny edge detection
    def canny(self,image):
        return cv2.Canny(image, 100, 200)

    #skew correction
    def deskew(self,image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    #template matching
    def match_template(self,image, template):
        return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    
    def find_plate(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        gray = cv2.bilateralFilter(gray, 13, 15, 15) 
        
        edged = cv2.Canny(gray, 30, 200) 
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
        screenCnt = None

        for c in contours:
            
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        
            if len(approx) == 4:
                screenCnt = approx
                break

        if screenCnt is None:
            detected = 0
            print ("No contour detected")
        else:
            detected = 1

        if detected == 1:
            cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)
        imshow(img,cmap="gray")
        plt.show()
        
    def ler(self,image):
        img = cv2.imread(r'C:\Users\gusta\Documentos\IFSP\TCC\TCC-novo\Imagens\Carro1.jpg')
        self.find_plate(img)
        #teste
        # gray = self.get_grayscale(img)
        # gray = self.thresholding(gray)
        # gray = cv2.resize(gray, (300, 200))
        # gray = self.opening(gray)
        # gray = cv2.GaussianBlur(gray, (3, 3), 1000)
        # gray = self.erode(gray)
        #normal
        gray = self.get_grayscale(img)
        gray = cv2.GaussianBlur(gray, (9, 9), 1000)

        gray = self.thresholding(gray)
        gray = self.opening(gray)
        #gray = canny(gray)
        gray = cv2.resize(gray, (300, 200))
        gray = cv2.GaussianBlur(gray, (9, 9), 1000)
        cv2.imwrite("test.jpg", gray)
        #normal
        # img = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        # (T, Thresh1) = cv2.threshold(img, 40, 50, cv2.THRESH_TRUNC)
        # (T, Thresh3) = cv2.threshold(Thresh1, 26, 44, cv2.THRESH_BINARY)
        # (T, Thresh2) = cv2.threshold(Thresh3, 0, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        # (T, Thresh4) = cv2.threshold(Thresh2, 30, 255, cv2.CALIB_CB_ADAPTIVE_THRESH)
        # pronta = cv2.resize(Thresh4, (300, 200))
        # pronta1 = cv2.GaussianBlur(pronta, (9, 9), 1000)
        # cv2.imwrite("merc.jpg", pronta1)
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        caracs = pytesseract.image_to_string(Image.open("test.jpg"), lang="eng",)
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

t =  LerPlaca()
t.ler('')