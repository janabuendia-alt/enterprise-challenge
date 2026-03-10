import streamlit as st
import os
# IMPORTEM ELS TEUS FITXERS (Vigila que els noms coincideixin!)
from fmea_engine import generate_fmea
from excel_formatter import create_fmea_excel

st.set_page_config(page_title="FMEA Generator", layout="centered")

st.title("🛠️ FMEA Analysis Tool")
st.write("Eina professional per a la generació de FMEA amb IA.")

# FORMULARI DISSENYAT PER A STREAMLIT
with st.form("meu_formulari"):
    project = st.text_input("Nom del Projecte", "Projecte Alpha")
    user = st.text_input("Enginyer/a", "JJana")
    version = st.text_input("Versió", "1.0")
    object_name = st.text_input("Objecte a analitzar", "Motor")
    peces = st.text_area("Peces (separades per comes)", "Rotor, Estator, Rodaments")
    
    submit = st.form_submit_button("Generar FMEA i Excel")

if submit:
    # Preparem les dades com les espera el teu fmea_engine
    form_data = {
        "project": project,
        "user": user,
        "version": version,
        "object": object_name,
        "peces": peces
    }
    
    with st.spinner("La IA està treballant... espera uns segons."):
        try:
            # 1. CRIDEM EL TEU MOTOR DE IA
            fmea_data = generate_fmea(form_data)
            
            # 2. CRIDEM EL TEU FORMATADOR D'EXCEL
            # Nota: El teu codi guarda el fitxer i retorna la ruta (path)
            file_path = create_fmea_excel(fmea_data, form_data)
            
            # 3. BOTÓ DE DESCÀRREGA
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Descarregar l'Excel FMEA",
                    data=f,
                    file_name=f"FMEA_{project}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.success("Fet! Ja pots descarregar el fitxer.")
            
        except Exception as e:
            st.error(f"S'ha produït un error: {e}")
