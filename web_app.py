import streamlit as st
import unicodedata
import re
import time
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Kely - Ton IA de Paiement Mobile", page_icon="💳", layout="centered")

# ===== STYLE INSTAGRAM - TEXTE NOIR OBLIGATOIRE =====
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, div { color: black !important; }
    h1 { text-align: center; color: black !important; }

    /* Conteneur d'une bulle */
    .bubble-row-user {
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
        margin: 6px 0 !important;
    }
    .bubble-row-kely {
        display: flex !important;
        justify-content: flex-start !important;
        width: 100% !important;
        margin: 6px 0 !important;
    }
    /* Ta bulle : A DROITE EN BLEU CLAIR + TEXTE NOIR */
    .bubble-user {
        background-color: #3797F0 !important;
        color: black !important;
        padding: 10px 14px !important;
        border-radius: 20px 20px 5px 20px !important;
        max-width: 80% !important;
        font-size: 16px !important;
        line-height: 1.4 !important;
    }
    .bubble-user p, .bubble-user strong, .bubble-user b {
        color: black !important;
        margin: 0 !important;
    }
    /* Bulle de Kely : A GAUCHE EN ROUGE CLAIR + TEXTE NOIR */
    .bubble-kely {
        background-color: #FFD6D1 !important;
        color: black !important;
        padding: 10px 14px !important;
        border-radius: 20px 20px 20px 5px !important;
        max-width: 80% !important;
        font-size: 16px !important;
        line-height: 1.4 !important;
    }
    .bubble-kely p, .bubble-kely strong, .bubble-kely b {
        color: black !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💳 Kely - Ton IA de Paiement Mobile")
st.write("Discute avec Kely comme sur Instagram : toi à droite, Kely à gauche !")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "prenom" not in st.session_state:
    st.session_state.prenom = None

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Salut ! 👋 Moi c'est Kely, ton IA de paiement mobile. Je peux t'aider pour tes dépôts, retraits, transferts, solde, factures... Tu veux commencer par quoi ?"})

# ===== AFFICHAGE STYLE INSTAGRAM =====
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="bubble-row-user"><div class="bubble-user">{message["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-row-kely"><div class="bubble-kely">🤖 {message["content"]}</div></div>', unsafe_allow_html=True)

# Boutons suggestions
st.markdown("**💡 Essaie :**")
col1, col2, col3, col4 = st.columns(4)
suggestion = None
with col1:
    if st.button("💰 Faire un dépôt"):
        suggestion = "Comment faire un dépôt ?"
with col2:
    if st.button("📤 Faire un transfert"):
        suggestion = "Comment faire un transfert ?"
with col3:
    if st.button("👀 Voir mon solde"):
        suggestion = "C'est quoi mon solde ?"
with col4:
    if st.button("🧾 Payer facture"):
        suggestion = "Comment payer ma facture ?"

# Vocal
st.markdown("### 🎙️ Enregistrement Vocal")
audio_data = mic_recorder(start_prompt="Parler à Kely", stop_prompt="Arrêter l'enregistrement", key='mic_payment_kely')
if audio_data:
    st.audio(audio_data['bytes'])
    st.success("Message vocal bien reçu par Kely !")
st.markdown("---")

def normaliser(texte):
    texte = texte.lower().strip()
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    texte = re.sub(r'[^a-z0-9 ]', ' ', texte)
    return re.sub(r'\s+', ' ', texte)

def get_bot_response(text):
    message_norm = normaliser(text)

    if "je m appelle" in message_norm:
        mots = message_norm.split()
        if "appelle" in mots:
            idx = mots.index("appelle")
            if idx + 1 < len(mots):
                prenom = mots[idx+1].capitalize()
                st.session_state.prenom = prenom
                return f"Enchanté {prenom} ! Moi c'est Kely. Comment puis-je t'aider aujourd'hui ?"
    
    def perso(rep):
        return f"{st.session_state.prenom}, {rep}" if st.session_state.prenom else rep

    # ===== CORRIGÉ : "COMMENT TU VAS" MAINTENANT FONCTIONNE =====
    if re.search(r'\b(bonjour|salut|coucou|bonsoir|hey|alo|allo|hello|bjr|slt)\b', message_norm):
        return "Bonjour ! C'est Kely 😊 Comment ça va ? Je peux t'aider pour : dépôt, retrait, transfert, solde, factures, forfaits, code PIN, sécurité... Dis-moi tout !"
    elif re.search(r'(comment tu vas|comment vas tu|tu vas bien|ca va|comment ca va|la forme|quoi de neuf|tu fais quoi)', message_norm):
        return "Je vais super bien, merci ! 😊 Et toi, comment se passe ta journée ? Tu veux faire un paiement ou on discute un peu ?"
    elif re.search(r'\b(creer un compte|ouvrir un compte|inscription|s inscrire|nouveau compte|avoir un compte)\b', message_norm):
        return perso("Pour créer ton compte mobile money, va chez un agent agréé avec ta pièce d'identité (CNI ou passeport). L'agent va enregistrer ton numéro, prendre ta photo et tu vas choisir ton code secret à 4 chiffres. C'est gratuit et ça prend 5 minutes !")
    elif re.search(r'\b(piece|identite|cni|passeport|kyc|carte d identite|document)\b', message_norm):
        return perso("Pour ton compte, il te faut une pièce d'identité valide : CNI, passeport ou carte de séjour. Sans ça, ton compte sera limité.")
    elif re.search(r'\b(depos|depot|mettre de l argent|charger mon compte|alimenter|recharger mon compte)\b', message_norm):
        return perso("Pour faire un dépôt, va chez un agent agréé (MTN, Moov, Orange, Wave) avec ton argent en espèces + ton numéro. Donne l'argent à l'agent, il charge ton compte. Valide avec ton code, et garde bien ton reçu. Le dépôt est toujours gratuit.")
    elif re.search(r'\b(retrait|retirer|enlever|sortir de l argent|prendre de l argent|recuperer mon argent)\b', message_norm):
        return perso("Pour faire un retrait : compose *123# > 'Retrait' > entre le montant > entre ton code secret. Tu vas recevoir un code de retrait. Va chez un agent avec ce code + ta pièce d'identité.")
    elif re.search(r'\b(transfer|envo|envoyer|donner de l argent|payer quelqu un)\b', message_norm):
        return perso("Pour faire un transfert : Menu > 'Transfert' > saisis le numéro > vérifie bien son nom > entre le montant > valide avec ton code secret. Vérifie 2 fois le numéro !")
    elif re.search(r'\b(mauvais numero|erreur|trompe|remboursement|annuler|double debit|argent parti)\b', message_norm):
        return perso("Si tu as envoyé à un mauvais numéro ou débité 2 fois : Appelle vite le 123 ou 111, donne la date, le montant et le numéro, va en agence avec ta CNI.")
    elif re.search(r'\b(solde|combien j ai|combien il me reste|mon compte|verifier mon argent)\b', message_norm):
        return perso("Pour voir ton solde, compose *123*4# (gratuit) ou ouvre ton appli mobile money, ton solde est affiché en haut.")
    elif re.search(r'\b(historique|releve|transaction|recu|preuve|mes depenses)\b', message_norm):
        return perso("Pour voir ton historique, va dans ton appli > 'Historique' ou compose *123# > 'Mes transactions'.")
    elif re.search(r'\b(frais|cout|taxe|prix|combien ca coute|commission)\b', message_norm):
        return perso("Les frais : Dépôt = gratuit. Transfert = 1% du montant. Retrait de plus de 10 000 FCFA = gratuit, en dessous = 100 FCFA.")
    elif re.search(r'\b(plafond|limite|maximum|montant max|combien je peux envoyer)\b', message_norm):
        return perso("Ton plafond : Compte simple = max 200 000 FCFA par jour, Compte vérifié avec CNI = jusqu'à 2 000 000 FCFA par jour.")
    elif re.search(r'\b(code|pin|secret|oublier|reinitialiser|changer mon code|mot de passe|bloque|debloquer)\b', message_norm):
        return perso("Si tu as oublié ton code PIN ou compte bloqué : compose *123*9# ou appelle le 123 avec ta CNI. Ne donne JAMAIS ton code à quelqu'un !")
    elif re.search(r'\b(facture|electricite|cie|sbee|eau|sodeco|loyer|abonnement|payer ma facture|canal|dstv|ecole)\b', message_norm):
        return perso("Pour payer une facture : *123# > 'Paiement de factures' > choisis CIE / SBEE, SODECO, Canal+ / DSTV, ou ton école. Entre ton numéro de facture + montant, puis valide avec ton code.")
    elif re.search(r'\b(recharge|credit|forfait|internet|data|mega|appel|unite|acheter du credit)\b', message_norm):
        return perso("Pour acheter du crédit ou un forfait internet : *123# > 'Recharge' ou 'Forfait' > choisis Montant ou Forfait Internet > valide avec ton code.")
    elif re.search(r'\b(commercant|marche|boutique|magasin|qr|code qr|payer un vendeur)\b', message_norm):
        return perso("Pour payer un commerçant, demande son numéro marchand ou son QR Code. Dans ton appli, choisis 'Payer un marchand', scanne le QR ou entre son numéro, mets le montant et valide.")
    elif re.search(r'\b(perte|perdu|vole|vol|fraude|arnaque|faux sms|pirate|securite)\b', message_norm):
        return perso("⚠️ URGENT : Si tu as perdu ton téléphone ou reçu un faux SMS : Appelle tout de suite le 111 pour bloquer ton compte, ne clique JAMAIS sur un lien SMS, ne donne JAMAIS ton code PIN.")
    elif re.search(r'\b(echec|echoue|pas recu|pas arrive|en attente|probleme|souci|ca marche pas|bug)\b', message_norm):
        return perso("Si ton transfert a échoué : attends 5 minutes, vérifie ton solde et ton historique. Si c'est toujours pareil, appelle le 123 avec le numéro de la transaction.")
    elif re.search(r'\b(agence|agent|ou aller|proche|horaire|ouvert|ferme|ou trouver)\b', message_norm):
        return perso("Les agences sont ouvertes du Lundi au Samedi de 8h à 18h, et certains agents de quartier jusqu'à 20h et le Dimanche.")
    elif re.search(r'\b(mtn|moov|orange|wave|mobile money|paiement|momo)\b', message_norm):
        return perso("Je connais tous les opérateurs : MTN MoMo, Moov Money, Orange Money, Wave. Dis-moi lequel tu utilises et ce que tu veux faire.")
    elif re.search(r'\b(qui es tu|tu t appelles|ton nom|c est quoi ton nom|tu es qui)\b', message_norm):
        return "Je m'appelle **Kely**, ton IA de paiement mobile. Je connais tout : dépôt, retrait, transfert, solde, factures, forfaits, sécurité... Comment puis-je t'aider ?"
    elif re.search(r'\b(raconte|blague|histoire|drole|tu aimes quoi|ton plat prefere|foot|musique|film|ecole|etude|amour|ami)\b', message_norm):
        return "Ahh, on passe en mode discussion ! 😄 J'adore ça. Raconte-moi, je t'écoute comme un vrai ami. Mais si tu as besoin d'un paiement entre deux, je suis là aussi !"
    elif re.search(r'\b(merci|top|genial|super|cool|ok|d accord|au revoir|bye|a plus)\b', message_norm):
        return "Avec grand plaisir ! 😊 N'hésite pas si tu as une autre question. Et n'oublie pas : ne partage JAMAIS ton code secret !"
    elif re.search(r'\b(comment ca marche|aide|comment faire|je comprends pas|explique|comment utiliser)\b', message_norm):
        return perso("Le paiement mobile, c'est comme un porte-monnaie dans ton téléphone. Tu mets de l'argent dedans (dépôt), tu peux l'envoyer (transfert), le retirer (retrait), payer tes factures... Tout avec ton code secret.")
    else:
        return "C'est très intéressant ! Dis-m'en un peu plus. Tu veux de l'aide pour un dépôt, un retrait, un transfert, ton solde, une facture, un forfait, ou on discute juste ?"

def afficher_reponse(prompt_text):
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    st.markdown(f'<div class="bubble-row-user"><div class="bubble-user">{prompt_text}</div></div>', unsafe_allow_html=True)
    with st.spinner("Kely est en train d'écrire..."):
        time.sleep(0.6)
        response = get_bot_response(prompt_text)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.markdown(f'<div class="bubble-row-kely"><div class="bubble-kely">🤖 {response}</div></div>', unsafe_allow_html=True)

if suggestion:
    afficher_reponse(suggestion)

if prompt := st.chat_input("Écris ton message à Kely ici..."):
    afficher_reponse(prompt)
