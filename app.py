import streamlit as st
import pandas as pd

st.set_page_config(page_title="Change Request Prioritization Engine", layout="wide")

st.title("🔧 Change Request Prioritization Engine")
st.markdown("Use the form below to calculate a priority score (P0–P4).")

# -----------------------------
# LOAD GOOGLE SHEET
# -----------------------------
sheet_csv_url = "https://docs.google.com/spreadsheets/d/1jElAUHxHpOxld2RzMfJEwNQez_33E_LiinWw9eUdJoE/export?format=csv"

df_rpa = pd.read_csv(sheet_csv_url)

# Create RPA label: A + B + C
df_rpa["RPA_Label"] = (
    df_rpa["RPA-number"] + " - " + df_rpa["RPA-name"] + " - " + df_rpa["Team"]
)

# Map RPA → workload
rpa_workload_map = dict(zip(df_rpa["RPA_Label"], df_rpa["3M Workload"]))

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
    "None": 0,
    "Supervisor": 1,
    "Manager": 2,
    "Head": 3,
    "Director/VP": 4
}

# -----------------------------
# SPLIT SCREEN UI
# -----------------------------

left, right = st.columns(2)

with left:
    with st.form("priority_form"):
        st.subheader("Input Fields")

        request_id = st.text_input("Request ID / Title")

        # Mandatory fields with no preselection ("" first)
        impact = st.selectbox(
            "Impact Description (Mandatory)",
            [""] + list(impact_scores.keys()),
            index=0
        )

        urgency = st.selectbox(
            "Urgency Description (Mandatory)",
            [""] + list(urgency_scores.keys()),
            index=0
        )

        escalation = st.selectbox(
            "Escalation Level (Mandatory)",
            list(escalation_scores.keys()),
            index=0  # Defaults to "None"
        )

        # NEW: RPA picklist
        rpa = st.selectbox(
            "RPA (Auto-fills workload if selected)",
            [""] + list(df_rpa["RPA_Label"]),
            index=0
        )

        # Auto-fill based on RPA
        auto_workload = rpa_workload_map.get(rpa, "")

        # Workload field (editable)
        workload_3m = st.number_input(
            "Workload Handled (3M)",
            min_value=0,
            max_value=100000,
            step=1,
            value=auto_workload if auto_workload != "" else 0
        )

        team_workload = st.number_input(
            "Team Workload %",
            min_value=0,
            max_value=100,
            step=1
        )

        submitted = st.form_submit_button("Calculate Priority")

with right:
    st.subheader("Priority Output")

    if submitted:

        # -----------------------------
        # VALIDATION
        # -----------------------------
        if impact == "" or urgency == "":
            st.error("❌ Please select both Impact and Urgency (mandatory fields).")
        else:
            # -----------------------------
            # CORE CALCULATIONS
            # -----------------------------
            S_I = impact_scores[impact]
            S_U = urgency_scores[urgency]
            S_E = escalation_scores[escalation]

            # Workload scoring
            S_WV = min(workload_3m / 25000, 4)  # Normalized 0–4
            S_TW = team_workload / 25          # Normalized 0–4

            # Weighted calculations
            W_I = S_I * 0.55
            W_U = S_U * 0.20
            W_E = S_E * 0.10
            W_WV = S_WV * 0.10
            W_TW = S_TW * 0.05

            total_score = W_I + W_U + W_E + W_WV + W_TW

            # Priority decision tree
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
            # OUTPUT PANEL
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
            st.write(f"- RPA: {rpa}")
            st.write(f"- Workload Handled (3M): {workload_3m}")
            st.write(f"- Team Workload %: {team_workload}")
            st.write(f"- Request ID / Title: {request_id}")
