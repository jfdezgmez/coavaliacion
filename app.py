import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Archivo de almacenamiento de datos local
DATA_FILE = "coevaluaciones.csv"

# Inicialización del archivo CSV con sus encabezados si no existe
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Fecha", "UD_Fase", "Grupo", "Evaluador", "Evaluado",
        "Compromiso", "Calidad_Tecnica", "Comunicacion", "Resolucion", "Comentario"
    ])
    df_init.to_csv(DATA_FILE, index=False)

# Configuración de la página
st.set_page_config(page_title="Sistema de Coevaluación", page_icon="📝", layout="centered")
st.title("📝 Formulario de Coevaluación de Proyecto")

# Pestañas para Alumnado y Profesorado
tab_alumno, tab_profesor = st.tabs(["🎓 Formulario Alumnado", "🔒 Panel Docente"])

# ------------------------------------------------------------------------------
# PESTAÑA 1: FORMULARIO DE ALUMNOS
# ------------------------------------------------------------------------------
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
        st.subheader("Criterios de Valoración (Escala 1 a 4)")
        st.caption("1: Insuficiente | 2: Regular / Aceptable | 3: Bueno | 4: Excelente")
        
        c1 = st.slider("1. Compromiso y cumplimiento de plazos:", 1, 4, 3)
        c2 = st.slider("2. Calidad y aportación técnica:", 1, 4, 3)
        c3 = st.slider("3. Comunicación y actitud colaborativa:", 1, 4, 3)
        c4 = st.slider("4. Resolución de problemas e iniciativa:", 1, 4, 3)
        
        comentario = st.text_area("Comentario cualitativo (opcional):")
        
        submitted = st.form_submit_button("Enviar Coevaluación")
        
        if submitted:
            if not evaluador.strip() or not evaluado.strip() or not grupo.strip():
                st.error("Por favor, completa todos los campos de identificación (Grupo, Evaluador y Evaluado).")
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
                    "Comentario": comentario.strip()
                }
                df_actual = pd.read_csv(DATA_FILE)
                df_actual = pd.concat([df_actual, pd.DataFrame([nueva_entrada])], ignore_index=True)
                df_actual.to_csv(DATA_FILE, index=False)
                st.success(f"¡Coevaluación enviada correctamente para {evaluado.strip()}!")

# ------------------------------------------------------------------------------
# PESTAÑA 2: PANEL DOCENTE
# ------------------------------------------------------------------------------
with tab_profesor:
    st.subheader("Acceso Restringido para Docentes")
    
    # Lectura segura de la contraseña desde Streamlit Secrets
    try:
        admin_password = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        admin_password = "profesor2026"  # Clave de respaldo por defecto si no están definidos los Secrets
    
    password = st.text_input("Introduce la contraseña de docente:", type="password")
    
    if password:
        if password == admin_password:
            st.success("Autenticación correcta.")
            
            if os.path.exists(DATA_FILE):
                df = pd.read_csv(DATA_FILE)
                
                if not df.empty:
                    st.subheader("📄 Listado Completo de Respuestas")
                    st.dataframe(df, use_container_width=True)
                    
                    # Asegurar conversión numérica de los criterios
                    cols_num = ["Compromiso", "Calidad_Tecnica", "Comunicacion", "Resolucion"]
                    for col in cols_num:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Calcular nota media individual por respuesta
                    df["Media_Individual"] = df[cols_num].mean(axis=1)
                    
                    # Agrupar por UD, Grupo y Alumno Evaluado
                    resumen = df.groupby(["UD_Fase", "Grupo", "Evaluado"])["Media_Individual"].agg(["mean", "count"]).reset_index()
                    resumen.columns = ["UD/Fase", "Grupo", "Alumno Evaluado", "Nota Media (sobre 4)", "Nº Evaluaciones Recibidas"]
                    
                    # Calcular la conversión a escala sobre 10
                    resumen["Nota Coevaluación (sobre 10)"] = (resumen["Nota Media (sobre 4)"] / 4 * 10).round(2)
                    
                    st.divider()
                    st.subheader("📊 Resumen de Notas Calculadas")
                    st.dataframe(resumen, use_container_width=True)
                    
                    st.divider()
                    # Botón para descargar el archivo CSV de datos
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Informe Completo (CSV)",
                        data=csv_data,
                        file_name=f"coevaluaciones_backup_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Aún no se han registrado respuestas en el sistema.")
            else:
                st.info("No existe archivo de datos registrado.")
        else:
            st.error("Contraseña incorrecta. Acceso denegado.")
