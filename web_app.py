import streamlit as st
import unicodedata
import re

# Configuration de la page
st.set_page_config(page_title="Assistant Paiement Mobile", page_icon="💳")

st.title("💳 Assistant de Paiement Mobile")
st.write("Posez vos questions librement, l'assistant est là pour vous guider.")

# Base de connaissances enrichie avec de multiples expressions
BASE = {
    'salutation': {
        'mots': ['bonjour', 'salut', 'bonsoir', 'coucou', 'hey', 'alo', 'allo'],
        'reponse': "Bonjour ! Je suis l'assistant de votre service de paiement mobile. Comment puis-je vous aider aujourd'hui ?"
    },
    'envoi': {
        'mots': ['envoyer', 'transferer', 'transfert', 'envoye', 'donner', 'expedier', 'transmettre', 'verser'],
        'reponse': "Pour envoyer de l'argent, composez le *123#, choisissez l'option 1 'Transfert', entrez le numéro du destinataire et le montant."
    },
    'retrait': {
        'mots': ['retirer', 'retrait', 'cash', 'recuperer', 'distributeur', 'argent liquide', 'sortir'],
        'reponse': "Pour effectuer un retrait, rendez-vous chez un agent agréé ou composez le *123# option 2 'Retrait' avec votre code secret."
    },
    'solde': {
        'mots': ['solde', 'compte', 'verifier', 'credit', 'argent', 'combien', 'restant', 'avoir'],
        'reponse': "Pour consulter votre solde à tout moment, composez le *123*4# (service gratuit)."
    },
    'changer_code': {
        'mots': ['code', 'pin', 'modifier', 'changer', 'secret', 'oublier', 'reinitialiser'],
        'reponse': "Pour modifier votre code secret ou le réinitialiser, allez dans les paramètres de votre compte ou composez le *123*9#."
    },
    'facture': {
        'mots': ['facture', 'electricite', 'eau', 'loyer', 'abonnement', 'payer', 'regler', 'cie', 'sodecoes'],
        'reponse': "Pour payer vos factures, accédez à l'option 'Paiement de factures' dans le menu *123# et suivez les instructions."
    },
    'frais': {
        'mots': ['frais', 'cout', 'taxe', 'prix'],
        'reponse': "Les frais s'élèvent à 1% du montant pour les transferts et sont gratuits pour les retraits supérieurs à 10 000 FCFA."
    },
    'perte_telephone': {
        'mots': ['perte', 'vole', 'vol', 'bloquer', 'fraude', 'perdu'],
        'reponse': "En cas de perte ou de vol, contactez immédiatement le service client au 111 pour bloquer votre compte temporairement."
    },
    'aide': {
        'mots': ['aide', 'probleme', 'contact', 'client', 'assistance', 'souci'],
        'reponse': "En cas de problème urgent (perte de téléphone ou blocage), contactez le service client au 123 ou rendez-vous en agence."
    }
}

def normaliser(texte):
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    texte = re.sub(r'[^a-z0-9 ]', ' ', texte)
    return re.sub(r'\s+', ' ', texte)

def trouver_reponse(message):
    message_norm = normaliser(message)

    # Gestion du prénom
    if "je m appelle" in message_norm:
        mots_msg = message_norm.split()
        if "appelle" in mots_msg:
            idx = mots_msg.index("appelle")
            if idx + 1 < len(mots_msg):
                prenom = mots_msg[idx + 1].strip('.,?!').capitalize()
                st.session_state.prenom = prenom
                return f"Enchanté {prenom} ! Comment puis-je vous aider avec votre compte ?"

    # 1. Recherche par mot-clé entier pour éviter les confusions
    for cle, donnees in BASE.items():
        for mot in donnees['mots']:
            if re.search(r'\b' + re.escape(mot) + r'\b', message_norm):
                reponse = donnees['reponse']
                if 'prenom' in st.session_state and st.session_state.prenom:
                    return f"{st.session_state.prenom}, {reponse}"
                return reponse
                
    # 2. Si aucun mot-clé direct n'est trouvé
    return "Je ne saisis pas bien votre préoccupation. Vous pouvez me poser des questions sur l'**envoi d'argent**, le **retrait**, la consultation du **solde**, le changement de **code PIN** ou le paiement de **factures**."

# Initialisation de l'historique de discussion
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prenom" not in st.session_state:
    st.session_state.prenom = None

# Affichage des messages de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone de saisie du chat
if prompt := st.chat_input("Écrivez votre question ici..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_bot = trouver_reponse(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": reponse_bot})
    with st.chat_message("assistant"):
        st.markdown(reponse_bot)