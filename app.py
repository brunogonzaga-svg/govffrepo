import streamlit as st
import pandas as pd

st.set_page_config(page_title="Change Request Prioritization Engine", layout="centered")

st.title("🔧 Change Request Prioritization Engine")
st.markdown("Use the form below to calculate a priority score (P0–P4).")

# -----------------------------
# LOAD GOOGLE SHEET
# -----------------------------

SHEET_URL = "https://docs.google.com/spreadsheets/d/1jElAUHxHpOxld2RzMfJEwNQez_33E_LiinWw9eUdJoE/export?format=csv&id=1jElAUHxHpOxld2RzMfJEwNQez_33E_LiinWw9eUdJoE&gid=0"

@st.cache_data
def load_rpa_data():
    df = pd.read_csv(SHEET_URL)
    # Create RPA concatenated string
    df["RPA"] = df["RPA-number"] + " - " + df["RPA-name"] + " - " + df["Team"]
    return df

rpa_df = load_rpa_data()

# Build RPA → Workload lookup
rpa_workload_lookup = dict(zip(rpa_df["RPA"], rpa_df["3M Workload"]))

# -----------------------------
# LOOKUP TABLES
# -----------------------------

impact_scores = {
    "Directly blocks revenue / Severe compliance risk": 4,
    "Significant process improvement / High volume manual work": 3,
    "Minor bug / Technical debt / Efficiency for small group": 2,
    "Minor UI/UX change / Nice-to-have": 1
}

urgency_scores = {
    "Imminent fixed deadline / Production blocker (1-2 weeks)": 4,
    "Time-sensitive process / High workload workaround (3-4 weeks)": 3,
    "Standard turnaround time / Manageable workaround (1-2 months)": 2,
    "Future planning / No specific deadline": 1
}

escalation_scores = {
    "Director/VP": 4,
    "Head": 3,
    "Manager": 2,
    "Supervisor": 1,
    "None": 0
}

# -----------------------------
# FORM UI
# -----------------------------

with st.form("priority_form"):
    st.subheader("Input Fields")

    request_id = st.text_input("Request ID / Title")

    impact = st.selectbox("Impact Description (Mandatory)", list(impact_scores.keys()))
    urgency = st.selectbox("Urgency Description (Mandatory)", list(urgency_scores.keys()))
    escalation = st.selectbox("Escalation Level (Mandatory)", list(escalation_scores.keys()))

    # -----------------------------
    # RPA PICKLIST + AUTO-FILL WORKLOAD
    # -----------------------------

    rpa_selected = st.selectbox(
        "RPA (Auto-fills workload if selected)",
        ["None"] + list(rpa_workload_lookup.keys())
    )

    # Auto-fill workload if RPA selected
    if rpa_selected != "None":
        default_workload = int(rpa_workload_lookup[rpa_selected])
    else:
        default_workload = 0

    workload_3m = st.number_input("Workload Handled (3M)", min_value=0, max_value=100000,
                                  value=default_workload, step=1)

    team_workload = st.number_input("Team Workload %", min_value=0, max_value=100, step=1)

    submitted = st.form_submit_button("Calculate Priority")

# -----------------------------
# CALCULATION LOGIC
# -----------------------------

if submitted:
    S_I = impact_scores[impact]
    S_U = urgency_scores[urgency]
    S_E = escalation_scores[escalation]

    # New workload-based scores
    S_WV = min(workload_3m / 25000, 4)  # Normalized to 0–4
    S_TW = team_workload / 25           # Normalized to 0–4

    # Weighted components
    W_I = S_I * 0.55
    W_U = S_U * 0.20
    W_E = S_E * 0.10
    W_WV = S_WV * 0.10
    W_TW = S_TW * 0.05

    total_score = W_I + W_U + W_E + W_WV + W_TW

    # Priority assignment
    if total_score >= 3.5:
        priority = "P0: IMMEDIATE"
    elif total_score >= 2.8:
        priority = "P1: HIGH"
    elif total_score >= 2.0:
        priority = "P2: MEDIUM"
    elif total_score >= 1.4:
        priority = "P3: LOW"
    else:
        priority = "P4: BACKLOG"

    # -----------------------------
    # OUTPUT
    # -----------------------------

    st.success(f"### Final Priority: **{priority}**")

    st.write("### Calculation Breakdown")
    st.write(f"- Impact Score: {S_I} → Weighted: {W_I:.2f}")
    st.write(f"- Urgency Score: {S_U} → Weighted: {W_U:.2f}")
    st.write(f"- Escalation Score: {S_E} → Weighted: {W_E:.2f}")
    st.write(f"- Workload Volume Score: {S_WV:.2f} → Weighted: {W_WV:.2f}")
    st.write(f"- Team Workload Score: {S_TW:.2f} → Weighted: {W_TW:.2f}")

    st.write(f"---\n### **Total Score: {total_score:.2f}**")

    st.write("### Contextual Data")
    st.write(f"- Workload Handled (3M): {workload_3m}")
    st.write(f"- Team Workload %: {team_workload}")
    st.write(f"- Request ID / Title: {request_id}")
    st.write(f"- RPA: {rpa_selected}")
