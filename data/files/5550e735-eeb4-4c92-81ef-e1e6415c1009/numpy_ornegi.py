# NumPy ile Bilimsel Hesaplama
import numpy as np

print("NumPy versiyonu:", np.__version__)

# Dizi oluşturma
arr = np.array([1, 2, 3, 4, 5])
print("Dizi:", arr)
print("Dizinin karesi:", arr ** 2)

# Rastgele sayılar
random_arr = np.random.random(10)
print("Rastgele sayılar:", random_arr)

# İstatistiksel işlemler
print("Ortalama:", np.mean(random_arr))
print("Standart sapma:", np.std(random_arr))

# Matris işlemleri
matrix = np.array([[1, 2], [3, 4]])
print("Matris:\n", matrix)
print("Matris determinantı:", np.linalg.det(matrix))
