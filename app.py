import streamlit as st
import google.generativeai as genai
import requests
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="SYNC COACH", page_icon="🦾", layout="centered")

# Design personnalisé (Mode Sombre Sport)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3em;
        background-color: #ff4b4b; color: white; font-weight: bold; border: none;
    }
    .stTextInput>div>div>input { background-color: #1e2130; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DES SECRETS / SIDEBAR ---
with st.sidebar:
    st.title("⚙️ CONFIGURATION")
    # Tu pourras aussi mettre ces clés dans les "Secrets" de Streamlit Cloud pour ne pas les taper à chaque fois
    api_key = st.text_input("Clé API Google AI Studio", type="password")
    ntfy_topic = st.text_input("Canal Notifications (ntfy.sh)", value="sync_coach_perso")
    st.info("Installe l'app 'ntfy' sur ton tel et abonne-toi au canal ci-dessus.")

# --- LOGIQUE GEMINI ---
def generate_coach_response(prompt, system_instruction):
    if not api_key:
        return "⚠️ Erreur : Configure ta clé API dans le menu à gauche."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Erreur technique : {str(e)}"

# --- INTERFACE PRINCIPALE ---
st.title("🦾 SYNC : Coach Privé")

# Prompt Système (L'âme du coach)
COACH_SYSTEM = """Tu es SYNC, un coach sportif d'élite. Ton ton est sec, motivant, et sans excuses. 
Tu es expert en musculation, poids de corps et course à pied. 
Tu dois toujours donner des séances structurées : Échauffement, Corps de séance, Finisher."""

tabs = st.tabs(["📅 AGENDA", "🏋️ SÉANCE RAPIDE", "💬 CHAT"])

# TAB 1 : L'Agenda adaptatif
with tabs[0]:
    st.subheader("Planifier ma semaine")
    jours = st.multiselect("Quels jours es-tu dispo ?", 
                          ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"])
    
    if st.button("Générer mon planning hebdomadaire"):
        prompt = f"Voici mes disponibilités pour cette semaine : {', '.join(jours)}. Crée-moi un programme adapté alternant force et cardio."
        plan = generate_coach_response(prompt, COACH_SYSTEM)
        st.markdown(plan)
        
        # Envoi d'une notification sur le téléphone
        if api_key:
            requests.post(f"https://ntfy.sh/{ntfy_topic}", 
                         data="Ton planning est prêt. Plus d'excuses, on commence demain !".encode('utf-8'))
            st.success("Planning envoyé sur ton téléphone via ntfy !")

# TAB 2 : Générateur instantané
with tabs[1]:
    st.subheader("Séance à la carte")
    col1, col2 = st.columns(2)
    with col1:
        duree = st.selectbox("Durée (min)", [15, 20, 30, 45, 60])
    with col2:
        type_exo = st.selectbox("Type", ["Poids de corps", "Fonte/Muscu", "Running/Cardio"])
    
    materiel = st.text_input("Matériel dispo (ex: haltères, barre de traction, rien)", "Rien")
    
    if st.button("Donne-moi ma séance !"):
        prompt = f"Fais-moi une séance de {duree} min de type {type_exo}. Matériel disponible : {materiel}."
        seance = generate_coach_response(prompt, COACH_SYSTEM)
        st.info(seance)

# TAB 3 : Discussion libre
with tabs[2]:
    st.subheader("Pose une question au Coach")
    user_msg = st.text_input("Message...", placeholder="Coach, j'ai mal aux genoux, on adapte ?")
    if st.button("Envoyer"):
        reponse = generate_coach_response(user_msg, COACH_SYSTEM)
        st.write(reponse)

st.caption("SYNC v1.0 - Le travail bat le talent quand le talent ne travaille pas.")
