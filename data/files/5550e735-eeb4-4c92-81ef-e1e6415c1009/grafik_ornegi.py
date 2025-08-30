# Matplotlib ile Grafik Çizimi
import matplotlib.pyplot as plt
import numpy as np

# Sinüs ve kosinüs grafiği
x = np.linspace(0, 2 * np.pi, 100)
y1 = np.sin(x)
y2 = np.cos(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, label='sin(x)', color='blue')
plt.plot(x, y2, label='cos(x)', color='red')
plt.title('Sinüs ve Kosinüs Fonksiyonları')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()

# Bar grafiği
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]

plt.figure(figsize=(8, 6))
plt.bar(categories, values, color=['red', 'green', 'blue', 'orange'])
plt.title('Örnek Bar Grafiği')
plt.ylabel('Değerler')
plt.show()

print("Grafikler oluşturuldu!")
