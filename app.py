import streamlit as st
import numpy as np
import pandas as pd
from fractions import Fraction

st.title("Aplicación AHP (Proceso Analítico Jerárquico)")

# --- Paso 1: Ingreso de criterios y alternativas ---
criterios = st.text_area("Criterios (uno por línea)", "Precio\nEstética\nSeguridad\nConsumo").splitlines()
alternativas = st.text_area("Alternativas (uno por línea)", "Coche A\nCoche B\nCoche C").splitlines()

n_criterios = len(criterios)
n_alternativas = len(alternativas)

# --- Paso 2: Matriz de comparación por pares para criterios ---
st.subheader("Matriz Comparación de Criterios")
criterios_matrix = np.ones((n_criterios, n_criterios))

for i in range(n_criterios):
    for j in range(i+1, n_criterios):
        entrada = st.text_input(f"{criterios[i]} vs {criterios[j]}", value="1", key=f"criterio_{i}_{j}")
        try:
            valor = float(Fraction(entrada))
            if valor <= 0:
                st.warning("El valor debe ser positivo. Se usará 1 como valor por defecto.")
                valor = 1.0
        except Exception:
            st.warning("Entrada inválida. Se usará 1 como valor por defecto.")
            valor = 1.0
        criterios_matrix[i][j] = valor
        criterios_matrix[j][i] = 1 / valor

# Normalización y cálculo de pesos
col_sum = criterios_matrix.sum(axis=0)
normalized = criterios_matrix / col_sum
pesos_criterios = normalized.mean(axis=1)

st.markdown("### Pesos de los criterios")
pesos_df = pd.DataFrame({
    'Criterio': criterios,
    'Peso': pesos_criterios
})
st.dataframe(pesos_df)

# --- Paso 3: Comparación de alternativas por cada criterio ---
st.subheader("Comparación de alternativas por criterio")

pesos_alternativas = {}

for idx, criterio in enumerate(criterios):
    st.markdown(f"#### Criterio: {criterio}")
    matrix = np.ones((n_alternativas, n_alternativas))
    for i in range(n_alternativas):
        for j in range(i+1, n_alternativas):
            entrada_alt = st.text_input(f"{alternativas[i]} vs {alternativas[j]} ({criterio})", value="1", key=f"{criterio}_{i}_{j}")
            try:
                val = float(Fraction(entrada_alt))
                if val <= 0:
                    st.warning("El valor debe ser positivo. Se usará 1 como valor por defecto.")
                    val = 1.0
            except Exception:
                st.warning("Entrada inválida. Se usará 1 como valor por defecto.")
                val = 1.0
            matrix[i][j] = val
            matrix[j][i] = 1 / val
    norm = matrix / matrix.sum(axis=0)
    pesos = norm.mean(axis=1)
    pesos_alternativas[criterio] = pesos

# --- Paso 4: Cálculo del ranking global ---
st.subheader("Ranking final de alternativas")

ranking = np.zeros(n_alternativas)

for i, criterio in enumerate(criterios):
    ranking += pesos_criterios[i] * pesos_alternativas[criterio]

ranking_df = pd.DataFrame({
    'Alternativa': alternativas,
    'Puntaje Global': ranking
}).sort_values(by='Puntaje Global', ascending=False)

st.dataframe(ranking_df)

# --- Paso 5: Análisis de sensibilidad ---
st.subheader("Análisis de Sensibilidad")
pesos_editables = []

for i, crit in enumerate(criterios):
    val = st.slider(f"Nuevo peso para {crit}", min_value=0.0, max_value=1.0, value=float(pesos_criterios[i]), step=0.01)
    pesos_editables.append(val)

# Normalizamos para que sumen 1
pesos_editables = np.array(pesos_editables)
pesos_editables /= pesos_editables.sum()

ranking_sensibilidad = np.zeros(n_alternativas)

for i, criterio in enumerate(criterios):
    ranking_sensibilidad += pesos_editables[i] * pesos_alternativas[criterio]

ranking_df2 = pd.DataFrame({
    'Alternativa': alternativas,
    'Puntaje (Sensibilidad)': ranking_sensibilidad
}).sort_values(by='Puntaje (Sensibilidad)', ascending=False)

st.dataframe(ranking_df2)
