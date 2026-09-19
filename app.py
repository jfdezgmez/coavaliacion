import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de archivo de base de datos
DATA_FILE = "coevaluaciones.csv"

# Crear el archivo si no existe
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Fecha", "UD_Fase", "Grupo", "Evaluador", "Evaluado",
        "Compromiso", "Calidad_Tecnica", "Comunicacion", "Resolucion", "Comentario"
    ])
    df_init.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Sistema de Coevaluación", page_icon="📝")
st.title("📝 Formulario de Coevaluación de Proyecto")

# Pestañas: Alumnos / Profesor
tab_alumno, tab_profesor = st.tabs(["🎓 Formulario Alumnado", "🔒 Panel Docente"])

with tab_alumno:
    st.markdown("Cubre este formulario para **cada uno de los compañeros** de tu grupo al finalizar la fase o UD.")
    
    with st.form("form_coevaluacion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ud_fase = st.selectbox("Unidad Didáctica / Fase:", [f"UD {i}" for i in range(1, 8)])
            grupo = st.text_input("Nombre o Número de Grupo/Equipo:")
        with col2:
            evaluador = st.text_input("Tu Nombre Completo (Evaluador):")
            evaluado = st.text_input("Nombre del Compañero a Evaluar:")
            
        st.divider()
        st.subheader("Criterios de Valoración (1 a 4)")
        
        c1 = st.slider("1. Compromiso y cumplimiento de plazos:", 1, 4, 3)
        c2 = st.slider("2. Calidad y aportación técnica:", 1, 4, 3)
        c3 = st.slider("3. Comunicación y actitud colaborativa:", 1, 4, 3)
        c4 = st.slider("4. Resolución de problemas e iniciativa:", 1, 4, 3)
        
        comentario = st.text_area("Comentario cualitativo (opcional):")
        
        submitted = st.form_submit_button("Enviar Coevaluación")
        
        if submitted:
            if not evaluador or not evaluado or not grupo:
                st.error("Por favor, cubre todos los campos de identificación.")
            else:
                nueva_entrada = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "UD_Fase": ud_fase,
                    "Grupo": grupo.strip().upper(),
                    "Evaluador": evaluador.strip(),
                    "Evaluado": evaluado.strip(),
                    "Compromiso": c1,
                    "Calidad_Tecnica": c2,
                    "Comunicacion": c3,
                    "Resolucion": c4,
                    "Comentario": comentario
                }
                df_actual = pd.read_csv(DATA_FILE)
                df_actual = pd.concat([df_actual, pd.DataFrame([nueva_entrada])], ignore_index=True)
                df_actual.to_csv(DATA_FILE, index=False)
                st.success(f"¡Coevaluación enviada correctamente para {evaluado}!")

with tab_profesor:
    st.subheader("Acceso Restringido")
    password = st.text_input("Contraseña de docente:", type="password")
    
    if password == "profesor2026":  # Cambia esta contraseña
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                st.subheader("Resumen de Respuestas")
                st.dataframe(df)
                
                # Cálculo de nota media por evaluado y UD
                df["Media_Individual"] = df[["Compromiso", "Calidad_Tecnica", "Comunicacion", "Resolucion"]].mean(axis=1)
                
                resumen = df.groupby(["UD_Fase", "Grupo", "Evaluado"])["Media_Individual"].agg(["mean", "count"]).reset_index()
                resumen.columns = ["UD/Fase", "Grupo", "Alumno Evaluado", "Nota Media (sobre 4)", "Nº Evaluaciones Recibidas"]
                
                # Convertir a escala sobre 10
                resumen["Nota Coevaluación (sobre 10)"] = (resumen["Nota Media (sobre 4)"] / 4 * 10).round(2)
                
                st.subheader("📊 Notas Calculadas de Coevaluación")
                st.table(resumen)
                
                # Descargar datos en CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Descargar Informe Completo (CSV)", csv, "coevaluaciones_export.csv", "text/csv")
            else:
                st.info("Aún no se han registrado respuestas.")
