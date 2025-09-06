# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 16:09:21 2025

@author: zzzz
"""
import numpy as np #importa NumPy (vectores, funciones trigonométricas, etc.)
import pandas as pd #importa pandas (manejo de tablas/CSV) como pd.
import matplotlib.pyplot as plt #importa la parte de trazado de Matplotlib como plt.
import matplotlib.dates as mdates #importa utilidades para fechas en gráficos (no se usa luego en el código).
from datetime import datetime, timedelta
from numpy import sin, cos, radians, degrees, arctan2 #importa funciones de NumPy para usarlas sin el prefijo np..
import pytz #biblioteca de zonas horarias (no se usa después).
# Conversión robusta de fechas
def parse_date(x): #intenta convertir la cadena x a fecha con dos formatos posibles
    for fmt in ("%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"):
        try:
            return pd.to_datetime(x, format=fmt)
        except:
            continue
    return pd.NaT #Si ninguno funciona devuelve

lat = float(input("Ingrese la latitud (ej. 42.28): "))
lon = float(input("Ingrese la longitud (ej. -3.68): "))
fecha_str = input("Ingrese la fecha (YYYY-MM-DD): ")
inclinacion = float(input("Ingrese la inclinación del panel (ej. 30): "))
acimut_panel = float(input("Ingrese el acimut del panel (0=Norte, 180=Sur): "))
area = 270 
fecha = pd.to_datetime(fecha_str)

#Se abre el archivo csv 
df = pd.read_csv("Copia de SolarArrayProduction.csv", sep=";", header=None, skiprows=1, #indican que el archivo tiene una fila inicial que se ignora; se definen manualmente los nombres de columnas.
                 names=["fechaHora", "elect p1", "elect p2"])
df["fechaHora"] = df["fechaHora"].astype(str).str.strip()


#Se convierten fechas a date time 
df["fechaHora"] = df["fechaHora"].apply(parse_date)
df["elect p1"] = df["elect p1"].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)#Limpia los espacios, y se convierten en número 
df["elect p2"] = df["elect p2"].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)


#Filtras los datos del día que pidió el usuario.
filtro = df[df["fechaHora"].dt.date == fecha.date()].copy()
filtro["hora_decimal"] = filtro["fechaHora"].dt.hour + filtro["fechaHora"].dt.minute / 60 #Para crear gráficos o cálculos 



 # 2. Generación de horas del día (cada 15 min)

horas = filtro["fechaHora"].dt.hour + filtro["fechaHora"].dt.minute / 60 #hora de cada fila en decimales 
n = fecha.dayofyear # El número de días en la fecha ingresada 


# 3. Cálculo de posición solar

declinacion = 23.45 * np.cos(np.radians(360/365 * (n - 172))) #inclinación del Sol ese día respecto al ecuador (en radianes).
declinacion = np.radians(declinacion)
lat_rad = np.radians(lat) #latitud convertida a radianes.

new_f=fecha.date() # verifica que solo tome una fecha 
t=pd.date_range(f"{new_f} 00:00",f"{new_f} 23:59",freq="15min") # genera marcas de t cada 15min 
hora_s=t.hour+t.minute/60+t.second/3600 #versión numérica/decimal de esas horas, lista para cálculos y gráficos.

lts=hora_s-1+(lon/60) # hora solar local (corrige hora decimal con longitud y desfase).
H = radians(15 * (lts - 12)) # ángulo horario solar (cuánto ha girado la Tierra respecto al mediodía solar).

angulo_sol= (sin(declinacion)*sin(lat_rad)) + (cos(declinacion)*cos(lat_rad))*cos(H) # angulo solar seno de la altura solar.


s_in=1.4883*0.7**((angulo_sol)**-0.678) #irradiancia  irradiancia aproximada que llega al suelo.

altura = np.arcsin(angulo_sol)         # altura solar en radianes
altura_grados = np.degrees(altura) #altura solar en grados (más intuitiva para interpretar).


# Simulación de potencia y energía

eficiencia = 0.18

produccion=area*angulo_sol*s_in #produccion simulada 
# produccion_dia = round(produccion.sum(),2) #kWh


# 7. Visualización de comparación


if not filtro.empty:
    
    plt.figure(figsize=(10, 5))
    
    # Simulada
    plt.plot(horas, produccion, label="Potencia Simulada (W)", color='orange')
    
    # Real
    plt.plot(horas,filtro["elect p1"] , label="Potencia Real (W)", color='green')
    plt.plot(horas, filtro["elect p2"], label="Potencia Real (W)", color='red')
    plt.title(f"Comparación de Potencia FV - {fecha.date()}")
    plt.xlabel("Hora")
    plt.ylabel("Potencia (W)")
    plt.grid(True)
    plt.legend()
    plt.xticks(np.arange(0, 25, 1))
    plt.tight_layout()
    # plt.suptitle(f"Energía diaria: Simulada = {energia_simulada_kwh:.2f} kWh | Real = {energia_1_kwh:.2f} kWh {energia_2_kwh:.2f}kwh", y=1.02)
    plt.show()

#angulo de altitud solar 
plt.figure(figsize=(10,5))
plt.plot(hora_s,altura, color= "purple")
plt.title("Angulo de altitud solar vs Hora del dia")
plt.xlabel("Hora")
plt.ylabel("Angulo solar")
plt.grid(True)
plt.xticks(np.arange(0, 25, 1))
plt.show

#producciin simulada 
plt.figure(figsize=(10,5))
plt.plot(hora_s,produccion)
plt.title("produccion similada vs Hora del dia")
plt.grid(True)
plt.xticks(np.arange(0, 25, 1))
plt.show

H=15 * (lts - 12)
#angulo horario
plt.figure(figsize=(10,5))
plt.plot(hora_s,H,color= "orange")
plt.title("Angulo horario vs Hora del dia")
plt.xlabel("Hora")
plt.ylabel("Angulo")
plt.grid(True)
plt.xticks(np.arange(0, 25, 1))
plt.show
