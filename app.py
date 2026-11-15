
import streamlit as st
from google import genai
from google.genai import types

# --------------------------------------------------
# 1. ΡΥΘΜΙΣΕΙΣ ΕΦΑΡΜΟΓΗΣ
# --------------------------------------------------

st.set_page_config(
    page_title="Σωκρατικός Βοηθός Python (ΕΠΑΛ)",
    layout="centered"
)

st.markdown("""
    <style>
    code, pre {
        font-family: 'Courier New', Courier, monospace !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐍 Σωκρατικός Βοηθός Python 2.7 — Προετοιμασία Πανελλαδικών")

st.write(
    "Καλώς ήρθατε! Γράψτε την απορία σας ή τον κώδικά σας "
    "για να λάβετε καθοδήγηση βάσει του σχολικού βιβλίου."
)

# --------------------------------------------------
# 2. ΑΡΧΙΚΟΠΟΙΗΣΗ SESSION STATE
# --------------------------------------------------

if "exercise" not in st.session_state:
    st.session_state.exercise = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pedagogical_memory" not in st.session_state:
    st.session_state.pedagogical_memory = (
        "Δεν έχει αρχίσει ακόμη η επίλυση της άσκησης."
    )

if "usage_totals" not in st.session_state:
    st.session_state.usage_totals = {
        "input": 0,
        "output": 0,
        "thinking": 0,
        "cached": 0,
        "requests": 0
    }

# --------------------------------------------------
# 3. API KEY ΚΑΙ GEMINI CLIENT
# --------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error(
        "Δεν βρέθηκε το GEMINI_API_KEY "
        "στο αρχείο .streamlit/secrets.toml!"
    )
    st.stop()

client = genai.Client(api_key=api_key)

# --------------------------------------------------
# 4. SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
Είσαι ένας έμπειρος καθηγητής πληροφορικής σε ΕΠΑΛ
που προετοιμάζει μαθητές για τις Πανελλαδικές Εξετάσεις
στο μάθημα Προγραμματισμός Υπολογιστών.

Ο ρόλος σου είναι Socratic Tutor (Σωκρατικός Καθηγητής).

ΚΑΝΟΝΑΣ 1:
ΠΟΤΕ μην δίνεις έτοιμη τη λύση ή ολόκληρο τον κώδικα.
Καθοδήγησε τον μαθητή βήμα-βήμα με σύντομες,
στοχευμένες ερωτήσεις και υποδείξεις.

ΚΑΝΟΝΑΣ 2 - ΠΙΣΤΗ ΤΗΡΗΣΗ ΕΚΦΩΝΗΣΗΣ:
Η εκφώνηση που σου παρέχεται αποτελεί την αποκλειστική
πηγή αλήθειας για τα ζητούμενα της άσκησης.

Απαγορεύεται:
- Να επινοείς νέα δεδομένα ή υποερωτήματα.
- Να προσθέτεις απαιτήσεις που δεν αναφέρονται.
- Να παρουσιάζεις υποθέσεις ως στοιχεία της εκφώνησης.
- Να παραθέτεις δήθεν αυτούσια αποσπάσματα που δεν υπάρχουν.

Αν ο μαθητής αναφέρει κάτι που δεν συμφωνεί με την εκφώνηση,
μην το υιοθετείς αυτόματα. Έλεγξε την εκφώνηση και ζήτησε
διευκρίνιση εφόσον χρειάζεται.

Αν δεν γνωρίζεις σε ποιο υποερώτημα αναφέρεται ο μαθητής,
μην μαντεύεις. Ρώτησέ τον.

ΚΑΝΟΝΑΣ 3 - ΠΑΡΑΚΟΛΟΥΘΗΣΗ ΠΡΟΟΔΟΥ:
Χρησιμοποίησε την παιδαγωγική μνήμη για να γνωρίζεις:
- Σε ποιο σημείο βρίσκεται ο μαθητής.
- Τι έχει ήδη καταφέρει.
- Ποια λάθη έχει κάνει.
- Ποιες υποδείξεις έχουν ήδη δοθεί.
- Ποιες δυσκολίες παραμένουν.

Μην επαναλαμβάνεις άσκοπα τις ίδιες υποδείξεις.
Μην αποκαλύπτεις μεταβλητές ή τμήματα λύσης πριν
ο μαθητής προσπαθήσει να τα ανακαλύψει.

ΚΑΝΟΝΑΣ 4 - ΓΛΩΣΣΑ ΚΑΙ ΣΥΝΤΑΞΗ PYTHON 2.7:

1. Βασίζεσαι αποκλειστικά στο επίσημο σχολικό βιβλίο
   και στις συμβάσεις Python 2.7 που ορίζονται εδώ.

2. Η εκτύπωση γίνεται με print χωρίς παρενθέσεις.
   Παράδειγμα: print "Μήνυμα", α

3. ΕΙΣΟΔΟΣ ΔΕΔΟΜΕΝΩΝ:
   - Για αλφαριθμητικά: raw_input()
   - Για ακεραίους: int(input())
   - Για δεκαδικούς: float(input())

4. Εξηγείς την ακέραια διαίρεση στην Python 2.7
   αν χρειαστεί.

5. Αν ο μαθητής χρησιμοποιήσει σύνταξη Python 3,
   τον διορθώνεις ευγενικά.

6. Απαγορεύεται αυστηρά η χρήση της εντολής break.

ΚΑΝΟΝΑΣ 5 - ΠΑΙΔΑΓΩΓΙΚΗ ΣΥΜΠΕΡΙΦΟΡΑ:
Να αναφέρεσαι συγκεκριμένα στο υποερώτημα που εξετάζετε.
Να μην αναγκάζεις τον μαθητή να ανατρέχει συνεχώς στην εκφώνηση.

Να αναγνωρίζεις την πρόοδο, αλλά να μην χαρακτηρίζεις
έναν κώδικα απολύτως σωστό αν δεν έχει ελεγχθεί συνολικά.

ΚΑΝΟΝΑΣ 6 - ΕΣΩΤΕΡΙΚΗ ΕΝΗΜΕΡΩΣΗ ΜΝΗΜΗΣ:
Στο τέλος κάθε απάντησης θα δημιουργείς μια σύντομη
ενημέρωση της παιδαγωγικής μνήμης.

Η ενημέρωση αυτή θα βρίσκεται ανάμεσα στους ειδικούς
δείκτες <STATE_UPDATE> και </STATE_UPDATE>.

Θα περιλαμβάνει μόνο:
- Την πρόοδο του μαθητή.
- Τα λάθη και τις διορθώσεις του.
- Τις υποδείξεις που έχουν ήδη δοθεί.
- Το επόμενο εκκρεμές βήμα.

Η ενημέρωση πρέπει να είναι σύντομη και να μην υπερβαίνει
τις 100 λέξεις.

Δεν θα εμφανίζεις στον μαθητή τους ειδικούς δείκτες
ούτε το περιεχόμενο της εσωτερικής ενημέρωσης.
"""

# --------------------------------------------------
# 5. SIDEBAR - ΔΙΑΧΕΙΡΙΣΗ ΑΣΚΗΣΗΣ
# --------------------------------------------------

with st.sidebar:

    st.header("📚 Διαχείριση άσκησης")

    with st.form("new_exercise_form"):

        exercise_input = st.text_area(
            "Εισαγωγή εκφώνησης νέας άσκησης:",
            height=200,
            placeholder="Επικολλήστε εδώ ολόκληρη την εκφώνηση..."
        )

        start_exercise = st.form_submit_button(
            "Έναρξη / Νέα άσκηση"
        )

    if start_exercise:

        if exercise_input.strip():

            st.session_state.exercise = exercise_input.strip()

            st.session_state.messages = []

            st.session_state.pedagogical_memory = (
                "Η άσκηση μόλις ξεκίνησε. "
                "Δεν υπάρχουν ακόμη προσπάθειες του μαθητή."
            )

            st.session_state.usage_totals = {
                "input": 0,
                "output": 0,
                "thinking": 0,
                "cached": 0,
                "requests": 0
            }

            st.rerun()

        else:
            st.warning("Πρέπει να εισαγάγετε την εκφώνηση.")

    st.divider()

    if st.session_state.exercise:

        if st.button("🗑️ Καθαρισμός συνομιλίας"):

            st.session_state.messages = []

            st.session_state.pedagogical_memory = (
                "Η συνομιλία καθαρίστηκε. "
                "Η ίδια άσκηση παραμένει ενεργή."
            )

            st.rerun()

        st.subheader("📊 Στατιστικά συνεδρίας")

        totals = st.session_state.usage_totals

        st.metric("Αιτήματα", totals["requests"])
        st.metric("Input tokens", totals["input"])
        st.metric("Output tokens", totals["output"])
        st.metric("Thinking tokens", totals["thinking"])
        st.metric("Cached tokens", totals["cached"])

# --------------------------------------------------
# 6. ΕΛΕΓΧΟΣ ΕΝΕΡΓΗΣ ΑΣΚΗΣΗΣ
# --------------------------------------------------

if not st.session_state.exercise:

    st.info(
        "Για να ξεκινήσετε, εισαγάγετε πρώτα "
        "την εκφώνηση της άσκησης από το αριστερό μενού."
    )

    st.stop()

with st.expander("📖 Εκφώνηση ενεργής άσκησης", expanded=True):

    st.markdown(st.session_state.exercise)

# --------------------------------------------------
# 7. ΕΜΦΑΝΙΣΗ ΙΣΤΟΡΙΚΟΥ ΣΥΝΟΜΙΛΙΑΣ
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------
# 8. ΔΙΑΧΕΙΡΙΣΗ ΑΠΑΝΤΗΣΗΣ GEMINI
# --------------------------------------------------

def separate_memory(response_text):

    start_marker = "<STATE_UPDATE>"
    end_marker = "</STATE_UPDATE>"

    start = response_text.find(start_marker)
    end = response_text.find(end_marker)

    if start != -1 and end != -1 and end > start:

        visible_answer = response_text[:start].strip()

        new_memory = response_text[
            start + len(start_marker):end
        ].strip()

        return visible_answer, new_memory

    # Αν δεν δημιουργήθηκε σωστά η ενημέρωση,
    # διατηρούμε την προηγούμενη παιδαγωγική μνήμη.

    return response_text.strip(), None

# --------------------------------------------------
# 9. ΕΙΣΟΔΟΣ ΜΗΝΥΜΑΤΟΣ ΜΑΘΗΤΗ
# --------------------------------------------------

if prompt := st.chat_input("Γράψε την ερώτηση ή τον κώδικά σου..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Κρατάμε τα τελευταία 6 μηνύματα.
    # Η παλαιότερη πρόοδος διατηρείται στη μνήμη.

    recent_messages = st.session_state.messages[-6:]

    conversation = ""

    for msg in recent_messages:

        role_label = (
            "Μαθητής"
            if msg["role"] == "user"
            else "Καθηγητής"
        )

        conversation += (
            role_label + ": " + msg["content"] + "\n"
        )

    # Η εκφώνηση και η παιδαγωγική μνήμη
    # αποστέλλονται σε κάθε αίτημα.

    full_prompt = f"""
ΑΥΘΕΝΤΙΚΗ ΕΚΦΩΝΗΣΗ ΑΣΚΗΣΗΣ:
{st.session_state.exercise}

ΠΑΙΔΑΓΩΓΙΚΗ ΜΝΗΜΗ:
{st.session_state.pedagogical_memory}

ΠΡΟΣΦΑΤΗ ΣΥΝΟΜΙΛΙΑ:
{conversation}

Απάντησε στο τελευταίο μήνυμα του μαθητή.
Τήρησε όλους τους κανόνες του System Prompt.
Στο τέλος πρόσθεσε την εσωτερική ενημέρωση
ανάμεσα στους δείκτες <STATE_UPDATE> και </STATE_UPDATE>.
"""

    # --------------------------------------------------
    # 10. ΚΛΗΣΗ GEMINI API
    # --------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Ο καθηγητής σκέφτεται..."):

            try:

                response = client.models.generate_content(

                    model="models/gemini-3.6-flash",

                    contents=full_prompt,

                    config=types.GenerateContentConfig(

                        system_instruction=SYSTEM_PROMPT,

                        thinking_config=types.ThinkingConfig(
                            thinking_level="low"
                        )
                    )
                )

                raw_response = response.text or ""

                bot_response, new_memory = separate_memory(
                    raw_response
                )

                # Ενημέρωση παιδαγωγικής μνήμης

                if new_memory:
                    st.session_state.pedagogical_memory = new_memory

                # Εμφάνιση απάντησης μαθητή

                st.markdown(bot_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_response
                })

                # --------------------------------------------------
                # 11. ΚΑΤΑΓΡΑΦΗ TOKENS
                # --------------------------------------------------

                usage = response.usage_metadata

                if usage:

                    input_tokens = usage.prompt_token_count or 0
                    output_tokens = usage.candidates_token_count or 0
                    thinking_tokens = usage.thoughts_token_count or 0
                    cached_tokens = usage.cached_content_token_count or 0

                    totals = st.session_state.usage_totals

                    totals["input"] += input_tokens
                    totals["output"] += output_tokens
                    totals["thinking"] += thinking_tokens
                    totals["cached"] += cached_tokens
                    totals["requests"] += 1

                    st.caption(
                        f"Input: {input_tokens} | "
                        f"Output: {output_tokens} | "
                        f"Thinking: {thinking_tokens} | "
                        f"Cached: {cached_tokens}"
                    )

                else:

                    st.session_state.usage_totals["requests"] += 1

            except Exception as e:

                st.error(
                    f"Προέκυψε σφάλμα κατά την επικοινωνία: {e}"
                )
