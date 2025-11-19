import streamlit as st

st.set_page_config(layout="wide")

# ---------------------------
# Priority Calculation Logic
# ---------------------------
def calculate_priority(impact_desc, urgency_desc, escalation_level, workload_3m, workload_pct):
    # Convert descriptions into numeric weights
    impact_weights = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4,
    }
    urgency_weights = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4,
    }
    escalation_weights = {
        "None": 0,
        "L1": 1,
        "L2": 2,
        "L3": 3,
    }

    impact_value = impact_weights.get(impact_desc, 0)
    urgency_value = urgency_weights.get(urgency_desc, 0)
    escalation_value = escalation_weights.get(escalation_level, 0)

    # Normalize 3m workload → 0 to 4 scale
    workload_3m_norm = min(max(workload_3m / 25000, 0), 4)

    # Normalize workload percentage → 0 to 4 scale
    workload_pct_norm = min(max(workload_pct / 25, 0), 4)

    # Final score formula
    score = (
        (impact_value * 0.35) +
        (urgency_value * 0.35) +
        (escalation_value * 0.10) +
        (workload_3m_norm * 0.10) +
        (workload_pct_norm * 0.10)
    )

    # Priority classification
    if score >= 3.2:
        return "🔥 P1 - Critical"
    elif score >= 2.4:
        return "⚠️ P2 - High"
    elif score >= 1.6:
        return "📌 P3 - Medium"
    else:
        return "🟢 P4 - Low"


# ---------------------------
# Streamlit Layout
# ---------------------------

st.title("Request Priority Calculator")

left, right = st.columns(2)


# ---------------------------
# LEFT SIDE → Inputs
# ---------------------------
with left:
    st.header("Input Fields")

    impact_desc = st.selectbox(
        "Impact Description (mandatory)",
        ["", "Low", "Medium", "High", "Critical"],
        index=0,
        help="Select how impactful the issue is"
    )

    urgency_desc = st.selectbox(
        "Urgency Description (mandatory)",
        ["", "Low", "Medium", "High", "Critical"],
        index=0,
        help="Select how urgent the issue is"
    )

    escalation_level = st.selectbox(
        "Escalation Level (mandatory)",
        ["None", "L1", "L2", "L3"],
        index=0,
        help="Select escalation level"
    )

    workload_3m = st.number_input(
        "3-Month Workload (0 to 100,000)",
        min_value=0,
        max_value=100000,
        value=0
    )

    workload_pct = st.slider(
        "Current Workload (%)",
        0, 100, 0
    )

    # Validation
    if impact_desc == "" or urgency_desc == "":
        st.warning("Please select both Impact Description and Urgency Description to continue.")


# ---------------------------
# RIGHT SIDE → Output
# ---------------------------
with right:
    st.header("Priority Output")

    if impact_desc != "" and urgency_desc != "":
        priority = calculate_priority(
            impact_desc,
            urgency_desc,
            escalation_level,
            workload_3m,
            workload_pct
        )

        st.subheader("Priority Result")
        st.success(priority)

    else:
        st.info("Priority will appear here once all mandatory fields are populated.")
