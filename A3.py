## 0. Librerías 
import numpy as np
from scipy.stats import kurtosis, pearsonr
import matplotlib.pyplot as plt
from datetime import datetime
import requests
## 1. Obtención de la información 
# URL de la información a descargar
url = "https://hesperia.gsfc.nasa.gov/fermi/lat/qlook/lat_events.txt"
# Validación del URL y guardar el contenido en un archivo local
response = requests.get(url)
if response.status_code == 200:
    with open("lat_events_local.txt", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("Archivo descargado y guardado como lat_events_local.txt")
else:
    print(f"Error al descargar el archivo. Código de estado: {response.status_code}")
## 2. Código para lectura
# Leer el archivo local
try:
    with open("lat_events_local.txt", "r", encoding="utf-8") as file:
        data_lines = file.readlines()
        print("Archivo leído correctamente. Número de líneas:", len(data_lines))
except FileNotFoundError:
    print("El archivo no existe.")
    data_lines = []
except UnicodeDecodeError:
    print("Error al decodificar el archivo.")
    data_lines = []
## Transformación de datos y manejo de errores (detección de anomalías)
# Como la fuente original tiene los datos organizados en 2 formas, por lo que se 
# eliminan los duplicados
lista = []
duplicados = set()  # Para evitar duplicados
for line in data_lines:
    partes = line.split()
    # Validar que tenga al menos 8 columnas (incluyendo el "to")
    if len(partes) >= 7 and partes[2].lower() == "to":
        try:
            flux = float(partes[5])
            sigma = float(partes[6])
            # Crear clave única con fechas y horas
            key = (partes[0], partes[1], partes[3], partes[4])
            if key not in duplicados:
                entry = {
                    "StartDate": partes[0],
                    "StartTime": partes[1],
                    "EndDate": partes[3],
                    "EndTime": partes[4],
                    "Flux": flux,
                    "Sigma": sigma
                }
                lista.append(entry)
                duplicados.add(key)
        except ValueError:
            continue
print("Número de filas válidas:", len(lista))
## Para confirmar que la limpieza fue correcta
# Imprimir todo el archivo línea por línea
print("=== Contenido completo del archivo ===")
for i, line in enumerate(data_lines, start=1):
    print(f"{i:03d}: {line}")
# Imprimir solo las filas válidas en formato limpio
print("=== Archivo limpio (solo datos) ===")
for i, entry in enumerate(lista, start=1):
    print(f"{i:03d}: {entry['StartDate']} {entry['StartTime']} "
          f"to {entry['EndDate']} {entry['EndTime']} "
          f"Flux={entry['Flux']} Sigma={entry['Sigma']}")
# Guardar dataset limpio en un archivo TXT
with open("lat_events_clean.txt", "w", encoding="utf-8") as txtfile:
    for entry in lista:
        line = (f"{entry['StartDate']} {entry['StartTime']} "
                f"to {entry['EndDate']} {entry['EndTime']} "
                f"Flux={entry['Flux']} Sigma={entry['Sigma']}\n")
        txtfile.write(line)
print("Archivo limpio guardado como lat_events_clean.txt")
# 3. Cálculo de estadísticos
# Extraer columnas numéricas
flux = [d["Flux"] for d in lista]
sigma = [d["Sigma"] for d in lista]
flux_v = np.array(flux)
sigma_v = np.array(sigma)
# Calcular estadísticas
mean_flux = np.mean(flux_v)
var_flux = np.var(flux_v)
kurt_flux = kurtosis(flux_v)
mean_sigma = np.mean(sigma_v)
var_sigma = np.var(sigma_v)
kurt_sigma = kurtosis(sigma_v)
# Correlación entre Flux y Sigma
corr, p_value = pearsonr(flux_v, sigma_v)
# Mostrar resultados
print("=== Estadísticas de Flux ===")
print("Media:", mean_flux)
print("Varianza:", var_flux)
print("Curtosis:", kurt_flux)
print("\n=== Estadísticas de Sigma ===")
print("Media:", mean_sigma)
print("Varianza:", var_sigma)
print("Curtosis:", kurt_sigma)
print("\n=== Correlación Flux vs Sigma ===")
print("Coeficiente de correlación:", corr)
print("Valor p:", p_value)
## Para la viscualización de los datos
# Convertir StartDate + StartTime en un objeto datetime
times = []
flux = []
sigma = []
for entry in lista:
    try:
        dt = datetime.strptime(entry["StartDate"] + " " + entry["StartTime"], "%d-%b-%Y %H:%M:%S.%f")
        times.append(dt)
        flux.append(entry["Flux"])
        sigma.append(entry["Sigma"])
    except Exception as e:
        print("Error al convertir fecha/hora:", e)
# Crear gráficos
plt.figure(figsize=(12, 6))
# Gráfico de Flux
plt.subplot(2, 1, 1)
plt.plot(times, flux, marker="o", linestyle="-", color="blue")
plt.title("Comportamiento de Flux a lo largo del tiempo")
plt.xlabel("Tiempo")
plt.ylabel("Flux (gamma cm^-2 s^-1)")
plt.grid(True)
# Gráfico de Sigma
plt.subplot(2, 1, 2)
plt.plot(times, sigma, marker="o", linestyle="-", color="red")
plt.title("Comportamiento de Sigma a lo largo del tiempo")
plt.xlabel("Tiempo")
plt.ylabel("Sigma (desviaciones)")
plt.grid(True)
plt.tight_layout()
plt.show()
