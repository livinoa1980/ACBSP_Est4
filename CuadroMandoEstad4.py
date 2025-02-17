# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 11:54:41 2025

@author: Livino M. Armijos Toro

Cuadro de mando integral - Estándar4 de ACBSP
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Obtener credenciales desde `secrets.toml`
USUARIOS = st.secrets["credentials"]

st.title("Inicio de Sesión")

usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    if usuario in USUARIOS and USUARIOS[usuario] == clave:
        st.session_state["autenticado"] = True
        st.success(f"Bienvenido, {usuario} 🎉")
    else:
        st.error("Usuario o contraseña incorrectos.")

if "autenticado" in st.session_state and st.session_state["autenticado"]:
    st.write("¡Aquí va tu aplicación después de la autenticación!")

    
# Cargar datos actualizados
file_path = "Base medición - Estándar 4.xlsx"
df = pd.read_excel(file_path, sheet_name='base')

# Renombrar columnas correctamente
df.columns = [
    "Número", "Semestre", "Año", "Medición", "Componente", "Aula_Canvas",
    "Carrera", "Tipo_evaluado", "Participantes", "Criterio1", "Criterio2",
    "Criterio3", "Criterio4", "Resultados"
]

# Eliminar primera fila con nombres originales
df = df.iloc[1:].reset_index(drop=True)

# Convertir columnas a tipo numérico donde aplique
cols_numericas = ["Año", "Medición", "Semestre", "Participantes", "Criterio1", "Criterio2", "Criterio3", "Criterio4", "Resultados"]
df[cols_numericas] = df[cols_numericas].apply(pd.to_numeric, errors='coerce')

# Filtrar registros donde la columna "Resultados" no sea "NA"
df = df.dropna(subset=["Resultados"])

# Expandir registros por el número de participantes
df_expanded = df.loc[df.index.repeat(df["Participantes"].astype(int))].reset_index(drop=True)

# Categorizar resultados en Deficiente, Aceptable y Excelente
df_expanded["Categoría Resultados"] = pd.cut(
    df_expanded["Resultados"],
    bins=[-float("inf"), 0.33, 0.66, float("inf")],
    labels=["Deficiente", "Aceptable", "Excelente"]
)

# Configurar la página de Streamlit
st.set_page_config(page_title="Cuadro de Mando", layout="wide")

# Mostrar los logos en la parte superior
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.image("image1.jpg", width=100)
with col3:
    st.image("image2.png", width=100)

st.title("📊 Cuadro de Mando - Evaluación")

# Filtro de Carrera
carrera_seleccionada = st.selectbox("Selecciona una Carrera", ["Todos"] + list(df_expanded["Carrera"].unique()))

# Filtrar componentes según la carrera seleccionada
if carrera_seleccionada != "Todos":
    componentes_disponibles = df_expanded[df_expanded["Carrera"] == carrera_seleccionada]["Componente"].unique()
else:
    componentes_disponibles = df_expanded["Componente"].unique()
componente_seleccionado = st.selectbox("Selecciona un Componente", ["Todos"] + list(componentes_disponibles))

# Aplicar filtros
df_filtrado = df_expanded.copy()
if carrera_seleccionada != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Carrera"] == carrera_seleccionada]
if componente_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Componente"] == componente_seleccionado]

# Contar el número de casos por categoría de resultados y medición
df_grouped = df_filtrado.groupby(["Medición", "Categoría Resultados"]).size().reset_index(name="Cuenta de Resultados")

# Colores basados en la presentación
colores = {"Deficiente": "#FF5733", "Aceptable": "#FFC300", "Excelente": "#2ECC71"}

# Crear gráfico de barras con etiquetas mostrando evolución histórica
fig = px.bar(df_grouped, x="Medición", y="Cuenta de Resultados", color="Categoría Resultados",
             color_discrete_map=colores, labels={"Cuenta de Resultados": "Número de Casos"}, 
             title="Evolución de Resultados por Medición", text="Cuenta de Resultados", barmode="group")
fig.update_traces(textposition='outside')

st.plotly_chart(fig)
