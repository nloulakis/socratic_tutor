import os
import streamlit as st
from google import genai

# Ρύθμιση τίτλου και εμφάνισης σελίδας
st.set_page_config(page_title="Σωκρατικός Βοηθός Python (ΕΠΑΛ)", layout="centered")

st.title("🐍 Σωκρατικός Βοηθός Python 2.7 — Προετοιμασία Πανελλαδικών")
st.write("Καλώς ήρθατε! Γράψτε την απορία σας ή τον κώδικά σας για να λάβετε καθοδήγηση βάσει του σχολικού βιβλίου.")

# Ανάκτηση του API Key από τα secrets του Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Δεν βρέθηκε το GEMINI_API_KEY στο αρχείο .streamlit/secrets.toml!")
    st.stop()

# Αρχικοποίηση του Gemini Client
client = genai.Client(api_key=api_key)

# Αυστηρό System Prompt προσαρμοσμένο στις Πανελλαδικές Εξετάσεις ΕΠΑΛ
SYSTEM_PROMPT = """
Είσαι ένας έμπειρος καθηγητής πληροφορικής σε ΕΠΑΛ που προετοιμάζει μαθητές για τις Πανελλαδικές Εξετάσεις στο μάθημα Προγραμματισμός Υπολογιστών.
Ο ρόλος σου είναι Socratic Tutor (Σωκρατικός Καθηγητής). 
ΚΑΝΟΝΑΣ #1: ΠΟΤΕ μην δίνεις έτοιμη τη λύση ή ολόκληρο τον κώδικα στον μαθητή. 
Καθοδήγησέ τον βήμα-βήμα με σύντομες, στοχευμένες ερωτήσεις και υποδείξεις ώστε να ανακαλύψει μόνος του το λάθος ή τη σωστή σύνταξη.

ΑΥΣΤΗΡΟΙ ΚΑΝΟΝΕΣ ΓΛΩΣΣΑΣ & ΣΥΝΤΑΞΗΣ (Πανελλαδικές Εξετάσεις / Python 2.7):
1. Βασίζεσαι ΑΠΟΚΛΕΙΣΤΙΚΑ στο επίσημο σχολικό βιβλίο της Python 2.7.
2. Η εκτύπωση γίνεται πάντα με την εντολή print χωρίς παρενθέσεις (π.χ. print "Μήνυμα", α).
3. ΕΙΣΟΔΟΣ ΔΕΔΟΜΕΝΩΝ (ΚΡΙΣΙΜΟ):
   - Για αλφαριθμητικά (strings): raw_input()
   - Για ακεραίους: int(input())
   - Για δεκαδικούς: float(input())
   Επιμένεις αυστηρά στη μετατροπές τύπων (typecasting) με int() και float() πάνω στη input() για την ανάγνωση των αντίστοιχων αριθμητικών δεδομένων.
4. Ακέραια διαίρεση: Εξηγείς τις ιδιαιτερότητες της διαίρεσης ακεραίων στην Python 2.7 αν χρειαστεί.
5. Αν ο μαθητής χρησιμοποιήσει σύνταξη Python 3 (π.χ. print(...) με παρενθέσεις ή σκέτη input() για αριθμούς), τον διορθώνεις ευγενικά, θυμίζοντάς του τι απαιτεί το σχολικό βιβλίο και το γραπτό των Πανελλαδικών.
"""

# Διατήρηση ιστορικού συνομιλίας στο session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Κουμπί καθαρισμού συνομιλίας στο Sidebar
with st.sidebar:
    st.header("Επιλογές")
    if st.button("🗑️ Καθαρισμός Συνομιλίας"):
        st.session_state.messages = []
        st.rerun()

# Εμφάνιση παλαιότερων μηνυμάτων
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Πεδίο εισαγωγής μηνύματος από τον μαθητή
if prompt := st.chat_input("Γράψε την ερώτηση ή τον κώδικά σου..."):
    # Εμφάνιση μηνύματος μαθητή
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Σύνθεση του πλήρους prompt με το System Prompt και το ιστορικό
    full_prompt = f"{SYSTEM_PROMPT}\n\n"
    for msg in st.session_state.messages:
        role_label = "Μαθητής" if msg["role"] == "user" else "Καθηγητής"
        full_prompt += f"{role_label}: {msg['content']}\n"
    full_prompt += "Καθηγητής:"

    # Κλήση στο API του Gemini
    with st.chat_message("assistant"):
        with st.spinner("Ο καθηγητής σκέφτεται..."):
            try:
                response = client.models.generate_content(
                    model="models/gemini-3.6-flash",
                    contents=full_prompt
                )
                bot_response = response.text
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                st.error(f"Προέκυψε σφάλμα κατά την επικοινωνία: {e}")