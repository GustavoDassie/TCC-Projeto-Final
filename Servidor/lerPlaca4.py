# 导入opencv库
import cv2
# 导入依赖包
import hyperlpr3 as lpr3

# 实例化识别对象
catcher = lpr3.LicensePlateCatcher()

# 读取图片
image = cv2.imread(r'C:\Users\gusta\Documentos\IFSP\TCC\TCC-novo\jupiter\testeLegitimo.jpg')
# 识别结果
result = catcher.pipeline.detector(image)
out = result[0]
rect = result[0][:4].astype(int)
land_marks = out[5:13].reshape(4, 2).astype(int)
print(land_marks)

result = catcher(image)
print(result)