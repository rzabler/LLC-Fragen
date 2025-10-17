# app.py — Professionelle, thematisch gegliederte Umfrage (Streamlit)
# --------------------------------------------------------------
# Build: v2025-10-17-03

import os
import csv
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import streamlit as st

# Optional: für Webhook
try:
    import requests  # in requirements.txt enthalten
except Exception:
    requests = None

# ----------------------------
# Basiskonfiguration & Branding
# ----------------------------
st.set_page_config(page_title="Konzept-Umfrage – Superphone LLC", page_icon="📊", layout="centered")

LOGO_URL = os.environ.get("SURVEY_LOGO_URL", "")
SENDER_NAME = os.environ.get("SURVEY_SENDER", "PwC – Konzeptvorstellung / MIS")
FOOTER_IMPRINT = os.environ.get(
    "SURVEY_FOOTER",
    "Diese Demo dient der strukturierten Konzepterhebung (Uni-/Kundenprojekt). Bitte keine unnötigen personenbezogenen Daten angeben.",
)
CSV_PATH = os.environ.get("SURVEY_CSV_PATH", "responses.csv")
BUILD_ID = "v2025-10-17-03"

if LOGO_URL:
    st.image(LOGO_URL, width=160)

st.markdown(f"### {SENDER_NAME}")
st.markdown("#### Kurze, thematisch gegliederte Umfrage – eine Frage pro Schritt")
st.caption(f"Build: {BUILD_ID}")

# ----------------------------
# Teilnehmername (optional)
# ----------------------------
if "participant_name" not in st.session_state:
    st.session_state.participant_name = ""
participant_name = st.text_input(
    "Ihr Name (optional)",
    value=st.session_state.participant_name,
    placeholder="z. B. Vor- und Nachname oder Funktion",
)
st.session_state.participant_name = participant_name
st.divider()

# ----------------------------
# Kontext (ein-/ausblendbar)
# ----------------------------
with st.expander("Kontext: Superphone LLC (Aufgabenstellung)", expanded=False):
    st.markdown(
        """
        Die Superphone LLC ist ein skandinavisches Telko-Unternehmen mit Expansion nach Belgien, Deutschland,
        Italien und Spanien. Uneinigkeit im Vorstand: **Expansion** (z. B. Portugal, Türkei) vs. **Diversifikation**
        in neue Geschäftsfelder. PwC richtet ein MIS ein; erste Rohdaten liegen vor. Ziel: Berichts- & Dashboard-Konzept,
        ggf. inkl. Plan-/Forecast-Daten.
        """
    )

# ---------------------------------
# Fragenkatalog mit Sections
# ---------------------------------
DEFAULT_CHOICES = ["Ja", "Nein", "Keine Angabe"]

QUESTIONS: List[Dict[str, Any]] = [
    {"type": "section", "title": "1) Strategische Ausrichtung"},
    {
        "id": "tg_zielgruppen",
        "text": "Primäre Zielgruppe ist der Vorstand. Sollen 1–2 Ebenen darunter (z. B. Bereichs-/Fachbereichsleitung) ebenfalls adressiert werden – und falls ja: mit welcher **Detailtiefe**?",
        "comment_ph": "Bitte Zielgruppen & gewünschte Tiefe kurz skizzieren",
    },
    {
        "id": "freq_reporting",
        "text": "Gibt es **Teile des Reports**, die **live/nahezu in Echtzeit** vorliegen sollen (z. B. Soll–Ist)? Wie ist die gewünschte **Aktualisierungsfrequenz** insgesamt?",
        "options": ["Live (Teilbereiche)", "Täglich", "Wöchentlich", "Monatlich", "Quartalsweise", "Ad-hoc", "Keine Angabe"],
    },
    {
        "id": "strategie_status",
        "text": "Wie ist der **aktuelle Stand** der Diskussion *Expansion* vs. *Diversifikation*?",
        "options": ["Klar pro Expansion", "Klar pro Diversifikation", "Ausgewogen/offen", "Unterschiedlich je Bereich", "Keine Angabe"],
        "comment_ph": "Kurze Einordnung / Präferenz",
    },
    {
        "id": "szenario_abdeckung",
        "text": "Sollen **beide Strategien** (Expansion & Diversifikation) vergleichbar im Bericht dargestellt werden?",
        "options": ["Ja", "Nein", "Keine Angabe"],
    },

    {"type": "section", "title": "2) Dashboard-Design & Nutzung"},
    {
        "id": "layout_praferenz",
        "text": "Bevorzugen Sie **responsives Design** (mehrere Geräte) oder **Canvas** (feste Darstellung für große Screens)?",
        "options": ["Responsive", "Canvas", "Hybrid", "Keine Angabe"],
    },
    {
        "id": "drill_reihenfolge",
        "text": "Welche **Drill-Reihenfolge** bevorzugen Sie?",
        "options": ["Land → Produkt", "Produkt → Land", "Produktgruppe → Produkt → Region", "Noch unklar", "Keine Angabe"],
        "comment_ph": "Alternative Drill-Logiken oder Besonderheiten",
    },
    {
        "id": "anzahl_ansichten",
        "text": "Wie viele **Ansichten** sind sinnvoll, um den Informationsbedarf abzudecken?",
        "options": ["3–4 Kernseiten", "Detaillierte Struktur (Regionen/Produkte/Forecast)", "Noch unklar", "Keine Angabe"],
    },

    {"type": "section", "title": "3) Reporting-Typ & Dokumente"},
    {
        "id": "bericht_typ",
        "text": "Bevorzugen Sie **Vorstandsbericht (Management Report)** oder **Benutzerhandbuch (MIS-Guide)**?",
        "options": ["Vorstandsbericht", "Benutzerhandbuch", "Beides (kompakt)", "Keine Angabe"],
    },
    {
        "id": "bericht_details",
        "text": "Was verstehen Sie **konkret** unter einem Vorstandsbericht (Management Report)? Und welche **Details** erwarten Sie in einem Benutzerhandbuch (MIS-Guide)?",
        "comment_ph": "Bitte Erwartungen an Inhalt/Tiefe skizzieren",
    },
    {
        "id": "guide_inhalt",
        "text": "Falls ein **Benutzerhandbuch** vorgesehen ist: Soll es **Interpretationen der Kennzahlen** enthalten?",
        "options": ["Ja", "Nein", "Keine Angabe"],
    },
    {
        "id": "best_practices",
        "text": "Gibt es **interne Orientierungen/Vorgaben** für die Gestaltung – oder haben wir **freie Hand**?",
        "comment_ph": "Beispiele, Styleguides, Unternehmens-Referenzen",
    },

    {"type": "section", "title": "4) Analysen, KPIs & Datenlogik"},
    {
        "id": "vdt_mehrwert",
        "text": "Wo sehen Sie den größten **Mehrwert** eines **Value Driver Trees**?",
        "options": ["Management Overview", "Produktanalyse", "Plan/Forecast (Simulation)", "Übergreifend", "Keine Angabe"],
    },
    {
        "id": "ist_daten",
        "text": "**Ist-Daten**: Vorliegen aktuell für 2020–2024. Welche Ist-Daten sollen **wie** verwendet werden? Sollen fehlende Ist-Daten für aktuelle Perioden zunächst **simuliert/hochgerechnet** werden?",
        "comment_ph": "Bitte gewünschtes Vorgehen zu Ist-Daten & ggf. Simulation beschreiben",
    },
    {
        "id": "forecast_presets",
        "text": "**Forecast**: Sollen wir **Voreinstellungen** anbieten?",
        "options": ["Optimistisch", "Realistisch", "Pessimistisch", "Keine Angabe"],
        "comment_ph": "Optionale Hinweise zur Parametrisierung (z. B. Wachstum, Marketing, Kosten)",
    },
    {
        "id": "db1_annahmen",
        "text": "**DB1-Annahmen**: Können wir bei den **operativen Kosten** einen **variablen Anteil** ansetzen (z. B. Prozentsatz) – oder sind diese **voll fix**? (Hinweis: DB1 = Umsatz – variable Kosten)",
        "comment_ph": "Vorschlag für %-Satz bzw. Definition variabler Kosten",
    },
    {
        "id": "daten_scope",
        "text": "**Datenscope:** In der Aufgabenstellung wird beschrieben, dass Superphone vor einigen Jahren u. a. nach **Belgien** expandierte. In der bereitgestellten **Excel-Datei** taucht jedoch **Russland** statt Belgien auf. Welches Land sollen wir für das Reporting als Referenz verwenden?",
        "options": ["Belgien", "Russland", "Noch unklar", "Keine Angabe"],
    },

    {"type": "section", "title": "5) Regressionsmodell & Marketing-Lag"},
    {
        "id": "regression_info",
        "text": "Sollen wir ein **Regressionsmodell** im Reporting berücksichtigen? Hintergrund: Die **einzige beeinflussbare Variable** ist aktuell das **Marketing**; es zeigt einen **1-Jahres-Lag** (~+1,4 pro Marketing-Einheit auf den Umsatz im Folgejahr).",
        "options": ["Ja", "Nein", "Keine Angabe"],
    },
    {
        "id": "regression_integration",
        "text": "Wie möchten Sie die **Integration** der Marketing-Lag-Logik sehen?",
        "options": ["Schieberegler (Marketing-Budget)", "Szenario-Buttons (Low/Med/High)", "Parameter-Eingabe (Expertenmodus)", "Noch unklar", "Keine Angabe"],
    },

    {"type": "section", "title": "6) Sonstiges"},
    {"id": "hinweise", "text": "Gibt es **weitere Hinweise oder Wünsche**?", "comment_ph": "Offene Punkte, Risiken, Wünsche"},
]

# ----------------------------
# Query-Parameter (z. B. Token)
# ----------------------------
try:
    qp = st.query_params  # Streamlit >=1.30
except Exception:
    qp = st.experimental_get_query_params()

TOKEN: Optional[str] = None
if isinstance(qp, dict):
    TOKEN = (qp.get("t") if isinstance(qp.get("t"), str) else (qp.get("t", [None])[0]))

# ----------------------------
# Session State
# ----------------------------
if "idx" not in st.session_state:
    st.session_state.idx = 0  # Index über Fragen (Sections werden übersprungen)
if "answers" not in st.session_state:
    st.session_state.answers = {}  # {question_id: {"choice": str, "comment": str}}
if "started_at" not in st.session_state:
    st.session_state.started_at = time.time()

# ----------------------------
# Hilfsfunktionen
# ----------------------------
def is_section(item: Dict[str, Any]) -> bool:
    return item.get("type") == "section"

def get_question_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [it for it in items if not is_section(it)]

def save_to_csv(row: Dict[str, Any], path: str = CSV_PATH) -> None:
    file_exists = os.path.exists(path)
    write_header = not file_exists or os.path.getsize(path) == 0
    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def post_to_make(payload: Dict[str, Any]) -> tuple[bool, str]:
    """Sendet das Payload an den (optional) konfigurierten Make-Webhook."""
    # 1) secrets.toml: make_webhook = "https://hook...."
    webhook = None
    try:
        webhook = st.secrets.get("make_webhook")  # type: ignore[attr-defined]
    except Exception:
        webhook = None
    # 2) oder Env-Variable
    if not webhook:
        webhook = os.environ.get("MAKE_WEBHOOK_URL", "")

    if not webhook:
        return (False, "Kein Webhook konfiguriert (st.secrets['make_webhook'] oder env MAKE_WEBHOOK_URL).")

    if requests is None:
        return (False, "requests nicht verfügbar (prüfe requirements).")

    try:
        r = requests.post(webhook, json=payload, timeout=6)
        if 200 <= r.status_code < 300:
            return (True, "An Make übermittelt.")
        return (False, f"Make-Status {r.status_code}: {r.text[:200]}")
    except Exception as e:
        return (False, f"Fehler beim Webhook: {e}")

def compile_payload() -> Dict[str, Any]:
    ended_at = time.time()
    duration_sec = int(ended_at - st.session_state.started_at)
    ts_iso = datetime.now(timezone.utc).isoformat()

    payload: Dict[str, Any] = {
        "timestamp_utc": ts_iso,
        "token": TOKEN or "",
        "duration_sec": duration_sec,
        "participant_name": st.session_state.get("participant_name", ""),
    }

    for it in get_question_items(QUESTIONS):
        qid = it["id"]
        ans = st.session_state.answers.get(qid, {})
        payload[f"{qid}_choice"] = ans.get("choice", "")
        payload[f"{qid}_comment"] = ans.get("comment", "")

    return payload

# ----------------------------
# Navigation: eine Frage pro Schritt
# ----------------------------
question_items = get_question_items(QUESTIONS)
num_q = len(question_items)
idx = max(0, min(st.session_state.idx, num_q - 1))
st.session_state.idx = idx

progress = idx / num_q if num_q else 1.0
st.progress(progress, text=f"Frage {idx+1} von {num_q}")

current_q = question_items[idx]

# Letzte Section-Überschrift vor current_q finden
section_title = None
for it in QUESTIONS:
    if is_section(it):
        section_title = it["title"]
    else:
        if it is current_q:
            break

if section_title:
    st.markdown(f"##### {section_title}")

st.markdown(f"### {current_q['text']}")

# Vorbelegte Werte
prev = st.session_state.answers.get(current_q["id"], {})
options = current_q.get("options", DEFAULT_CHOICES)
comment_ph = current_q.get("comment_ph", "(optional)")

# Auswahl (Radio) & Kommentar
default_index = options.index(prev.get("choice")) if prev.get("choice") in options else None
choice = st.radio("Ihre Antwort:", options, index=default_index)
comment = st.text_area("Optionaler Kommentar", value=prev.get("comment", ""), height=120, placeholder=comment_ph)

# Zwischenspeichern
st.session_state.answers[current_q["id"]] = {"choice": choice, "comment": comment}

# Buttons
cols = st.columns(3)
with cols[0]:
    if st.button("⬅️ Zurück", disabled=(idx == 0)):
        st.session_state.idx = max(0, idx - 1)
        st.rerun()
with cols[1]:
    if st.button("Weiter ➡️", disabled=(idx >= num_q - 1)):
        st.session_state.idx = min(num_q - 1, idx + 1)
        st.rerun()
with cols[2]:
    pass

st.divider()

# ----------------------------
# Zusammenfassung & Absenden
# ----------------------------
if idx == num_q - 1:
    st.markdown("#### Zusammenfassung")
    if st.session_state.get("participant_name"):
        st.write(f"**Teilnehmer:** {st.session_state['participant_name']}")
    for it in QUESTIONS:
        if is_section(it):
            st.write(f"**{it['title']}**")
        else:
            a = st.session_state.answers.get(it["id"], {})
            st.write(f"- {it['text']} — **{a.get('choice', '')}**")
            if a.get("comment"):
                st.caption(f"Kommentar: {a['comment']}")

    with st.expander("Datenschutz & Einwilligung", expanded=True):
        st.markdown(
            """
            Wir speichern ausschließlich Ihre Antworten, einen Zeitstempel, optional den Einladungs-Token (falls im Link
            enthalten), die Bearbeitungsdauer **und** – falls angegeben – Ihren Namen. Es werden keine IP-Adressen oder
            Gerätekennungen gespeichert.
            Mit dem Absenden willigen Sie in die Verarbeitung zu Evaluationszwecken dieses Projekts ein.
            """
        )
        consent = st.checkbox("Ich willige in die Verarbeitung meiner Antworten ein.")

    if st.button("Antworten absenden", type="primary", disabled=not consent):
        row = compile_payload()

        # 1) lokal sichern
        save_to_csv(row)
        csv_ok = True

        # 2) optional an Make senden
        make_ok, make_msg = post_to_make(row)

        if csv_ok and make_ok:
            st.success("Vielen Dank! Ihre Antworten wurden gespeichert **und** übermittelt.")
        elif csv_ok and not make_ok:
            st.warning(f"Ihre Antworten wurden lokal gespeichert. Hinweis zur Übermittlung: {make_msg}")
        elif not csv_ok and make_ok:
            st.warning("Übermittlung ok, aber lokale Speicherung ist fehlgeschlagen.")
        else:
            st.error("Weder Speicherung noch Übermittlung war erfolgreich. Bitte später erneut versuchen.")

        st.balloons()
        st.session_state.idx = 0
        st.session_state.answers = {}
        st.session_state.started_at = time.time()

# ----------------------------
# Footer
# ----------------------------
st.divider()
st.caption(FOOTER_IMPRINT)
if TOKEN:
    st.caption(f"Token: {TOKEN}")