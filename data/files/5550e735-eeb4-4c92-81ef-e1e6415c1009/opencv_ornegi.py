# OpenCV ile Görüntü İşleme
import cv2
import numpy as np
import matplotlib.pyplot as plt

print("OpenCV versiyonu:", cv2.__version__)

# Görüntü oluşturma
# Boş bir görüntü oluştur (siyah)
img = np.zeros((300, 400, 3), dtype=np.uint8)

# Renkli şekiller çiz
cv2.rectangle(img, (50, 50), (150, 150), (0, 255, 0), -1)  # Yeşil kare
cv2.circle(img, (300, 100), 50, (255, 0, 0), -1)  # Mavi daire
cv2.line(img, (0, 200), (400, 200), (0, 0, 255), 3)  # Kırmızı çizgi

# Metin ekle
cv2.putText(img, 'OpenCV Test', (50, 250), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Matplotlib ile görüntüyü göster
plt.figure(figsize=(10, 6))
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('OpenCV ile Oluşturulan Görüntü')
plt.axis('off')
plt.show()

# Histogram oluşturma
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

plt.figure(figsize=(8, 5))
plt.plot(hist)
plt.title('Görüntü Histogramı')
plt.xlabel('Piksel Değeri')
plt.ylabel('Piksel Sayısı')
plt.show()

# Blur efekti
blurred = cv2.GaussianBlur(img, (15, 15), 0)

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title('Orijinal')
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
plt.title('Bulanık')
plt.axis('off')
plt.show()

print("OpenCV görüntü işleme örnekleri tamamlandı!")
