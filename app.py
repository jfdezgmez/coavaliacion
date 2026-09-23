import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
DATA_FILE = "coevaluaciones.csv"

UDS = [f"UD{i} — Fase {i}" for i in range(1, 8)]
UD_LABELS = {
    "UD1 — Fase 1": "UD1 · Plan Director, Análise de Riscos, Políticas e Xestión de Incidentes",
    "UD2 — Fase 2": "UD2 · Redes Seguras: VLANs, Subnetting, VPN",
    "UD3 — Fase 3": "UD3 · Xestión de Credenciais: PKI, Certificados, MFA",
    "UD4 — Fase 4": "UD4 · Control de Acceso e Autenticación: RADIUS, 802.1X",
    "UD5 — Fase 5": "UD5 · Dispositivos e Arranque Seguro: BIOS/UEFI, Secure Boot, Cifrado",
    "UD6 — Fase 6": "UD6 · Hardening de Sistemas Operativos",
    "UD7 — Fase 7": "UD7 · Configuración Perimetral: Firewall, IDS/IPS, SIEM",
}

CRITERIOS = [
    ("prazos",        "1. Cumprimento de prazos internos",
     "¿Entregou as súas partes nos tempos acordados polo grupo?"),
    ("calidade",      "2. Calidade da contribución técnica",
     "¿As partes que fixo son correctas e están ben documentadas?"),
    ("colaboracion",  "3. Colaboración e comunicación",
     "¿Participou nas decisións do grupo e comunicou os problemas a tempo?"),
    ("responsabilidade", "4. Asunción de responsabilidade",
     "¿Cumpriu cos roles asignados ao longo das fases?"),
]

ESCALA = "1 = Insuficiente · 2 = Aceptable · 3 = Bo · 4 = Notable · 5 = Excelente"

COLS_CSV = [
    "Fecha", "UD_Fase", "Grupo", "Evaluador", "Evaluado",
    "Prazos", "Calidade_Tecnica", "Colaboracion", "Responsabilidade", "Comentario"
]
COLS_NUM = ["Prazos", "Calidade_Tecnica", "Colaboracion", "Responsabilidade"]

# Inicializar CSV si no existe
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLS_CSV).to_csv(DATA_FILE, index=False)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Coevaluación · Bastionado de Redes e Sistemas",
    page_icon="📝",
    layout="centered",
)
st.title("📝 Coevaluación entre Pares")
st.caption("Módulo *Bastionado de Redes e Sistemas* (5022) · IES San Clemente")

tab_alumno, tab_profesor = st.tabs(["🎓 Formulario Alumnado", "🔒 Panel Docente"])

# ===========================================================================
# PESTAÑA 1 · FORMULARIO ALUMNADO
# ===========================================================================
with tab_alumno:
    st.markdown(
        "Cubre este formulario **por cada compañeiro/a do teu grupo** ao peche de cada trimestre. "
        "As túas respostas son anónimas para os teus compañeiros; o docente pode velas de forma individual."
    )

    with st.form("form_coevaluacion", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ud_fase = st.selectbox("Unidade Didáctica / Fase:", UDS)
            grupo   = st.text_input("Nome ou número do grupo:")
        with col2:
            evaluador = st.text_input("O teu nome completo (quen avalia):")
            evaluado  = st.text_input("Nome do/a compañeiro/a avaliado/a:")

        st.divider()
        st.subheader("Criterios de valoración")
        st.caption(ESCALA)

        puntuacions = {}
        for key, label, axuda in CRITERIOS:
            puntuacions[key] = st.slider(label, 1, 5, 3, help=axuda)

        comentario = st.text_area(
            "Comentario cualitativo (opcional):",
            placeholder="Podes engadir aquí calquera observación que consideres relevante.",
            max_chars=500,
        )

        enviado = st.form_submit_button("Enviar coevaluación ✉️")

        if enviado:
            if not evaluador.strip() or not evaluado.strip() or not grupo.strip():
                st.error("Por favor, completa todos os campos de identificación (Grupo, Avaliador e Avaliado).")
            elif evaluador.strip().lower() == evaluado.strip().lower():
                st.warning("Non podes avaliarte a ti mesmo/a neste formulario.")
            else:
                nova = {
                    "Fecha":            datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "UD_Fase":          ud_fase,
                    "Grupo":            grupo.strip().upper(),
                    "Evaluador":        evaluador.strip().title(),
                    "Evaluado":         evaluado.strip().title(),
                    "Prazos":           puntuacions["prazos"],
                    "Calidade_Tecnica": puntuacions["calidade"],
                    "Colaboracion":     puntuacions["colaboracion"],
                    "Responsabilidade": puntuacions["responsabilidade"],
                    "Comentario":       comentario.strip(),
                }
                df_actual = pd.read_csv(DATA_FILE)
                df_actual = pd.concat(
                    [df_actual, pd.DataFrame([nova])], ignore_index=True
                )
                df_actual.to_csv(DATA_FILE, index=False)
                media = sum(puntuacions.values()) / len(puntuacions)
                st.success(
                    f"Coevaluación enviada para **{nova['Evaluado']}**. "
                    f"Puntuación media desta avaliación: **{media:.2f} / 5**."
                )

# ===========================================================================
# PESTAÑA 2 · PANEL DOCENTE
# ===========================================================================
with tab_profesor:
    st.subheader("Acceso restrinxido — Docente")

    try:
        admin_password = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        admin_password = "profesor2026"

    contrasinal = st.text_input("Contrasinal:", type="password")

    if contrasinal:
        if contrasinal != admin_password:
            st.error("Contrasinal incorrecto. Acceso denegado.")
            st.stop()

        st.success("Autenticación correcta.")

        if not os.path.exists(DATA_FILE):
            st.info("Aínda non hai datos rexistrados.")
            st.stop()

        df = pd.read_csv(DATA_FILE)
        if df.empty:
            st.info("Aínda non se rexistrou ningunha resposta.")
            st.stop()

        for col in COLS_NUM:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # ── Filtros ────────────────────────────────────────────────────────
        st.subheader("Filtros")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            uds_dispon = ["Todas"] + sorted(df["UD_Fase"].dropna().unique().tolist())
            filtro_ud  = st.selectbox("Unidade Didáctica:", uds_dispon)
        with col_f2:
            grupos_dispon = ["Todos"] + sorted(df["Grupo"].dropna().unique().tolist())
            filtro_grupo  = st.selectbox("Grupo:", grupos_dispon)

        df_f = df.copy()
        if filtro_ud    != "Todas": df_f = df_f[df_f["UD_Fase"] == filtro_ud]
        if filtro_grupo != "Todos": df_f = df_f[df_f["Grupo"]   == filtro_grupo]

        # ── Listado completo ────────────────────────────────────────────────
        st.divider()
        st.subheader("📄 Respostas individuais")
        st.dataframe(df_f, use_container_width=True)

        # ── Resumo por alumno ───────────────────────────────────────────────
        df_f["Media_Coevaluacion"] = df_f[COLS_NUM].mean(axis=1)

        resumen = (
            df_f.groupby(["UD_Fase", "Grupo", "Evaluado"])["Media_Coevaluacion"]
            .agg(media="mean", n="count")
            .reset_index()
        )
        resumen.columns = ["UD/Fase", "Grupo", "Alumno/a avaliado/a", "Media (sobre 5)", "Nº avaliacións recibidas"]

        # Conversión a nota sobre 10 (escala 1–5 → 0–10)
        # Fórmula: (media - 1) / 4 * 10  →  1=0, 3=5, 5=10
        resumen["Nota coevaluación (sobre 10)"] = ((resumen["Media (sobre 5)"] - 1) / 4 * 10).round(2)
        resumen["Media (sobre 5)"] = resumen["Media (sobre 5)"].round(2)

        st.divider()
        st.subheader("📊 Nota de coevaluación por alumno/a")
        st.caption(
            "A nota calcúlase como a media das avaliacións recibidas (excluída a autoevaluación). "
            "Escala: 1 → 0,00 pts · 3 → 5,00 pts · 5 → 10,00 pts."
        )

        def cor_nota(val):
            """Coloración CSS sen necesidade de matplotlib."""
            try:
                v = float(val)
            except (TypeError, ValueError):
                return ""
            if v >= 8:
                return "background-color: #c6efce; color: #276221"
            elif v >= 6:
                return "background-color: #ffeb9c; color: #7d6608"
            elif v >= 4:
                return "background-color: #ffc7ce; color: #9c1d25"
            else:
                return "background-color: #f4cccc; color: #6b0000"

        st.dataframe(
            resumen.style.applymap(cor_nota, subset=["Nota coevaluación (sobre 10)"]),
            use_container_width=True,
        )

        # ── Alerta discrepancias ────────────────────────────────────────────
        st.divider()
        st.subheader("⚠️ Discrepancias destacables (>2 puntos entre avaliacións)")
        discrepancias = (
            df_f.groupby(["UD_Fase", "Grupo", "Evaluado"])["Media_Coevaluacion"]
            .agg(desv="std", n="count")
            .reset_index()
            .query("n >= 2 and desv > 0.5")   # std alto ≈ criterios moi diferentes
        )
        if discrepancias.empty:
            st.success("Non se detectaron discrepancias significativas nos filtros actuais.")
        else:
            st.warning(
                "Os seguintes alumnos/as recibiron avaliacións moi dispares entre compañeiros. "
                "Recoméndase revisión antes de aplicar a nota."
            )
            st.dataframe(discrepancias.rename(columns={
                "UD_Fase": "UD/Fase", "Evaluado": "Alumno/a",
                "desv": "Desv. típica (criterios)", "n": "Nº avaliacións"
            }), use_container_width=True)

        # ── Descarga ────────────────────────────────────────────────────────
        st.divider()
        csv_raw    = df_f.to_csv(index=False).encode("utf-8")
        csv_resumen = resumen.to_csv(index=False).encode("utf-8")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "📥 Descargar respostas completas (CSV)",
                data=csv_raw,
                file_name=f"coevaluacion_respostas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        with col_d2:
            st.download_button(
                "📥 Descargar notas calculadas (CSV)",
                data=csv_resumen,
                file_name=f"coevaluacion_notas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
