import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="AquaMed360 Climate-Health Prototype",
    page_icon="🌍",
    layout="wide"
)

st.title("AquaMed360 Climate-Health Early Warning Prototype")
st.caption("Open-source climate-health risk intelligence for vulnerable children in coastal communities.")

data = [
    {
        "community": "Ayetoro",
        "latitude": 6.1000,
        "longitude": 4.8000,
        "children_under_5": 850,
        "school_children": 1400,
        "flood_frequency_score": 88,
        "water_contamination_score": 82,
        "malaria_risk_score": 74,
        "heat_exposure_score": 68,
        "health_facility_access_score": 45,
        "safe_water_access_score": 32,
        "sanitation_access_score": 38,
        "field_report": "Recurring flooding around homes, school routes and water points.",
        "recommended_action": "Activate WASH alert, child health outreach and safe water messaging."
    },
    {
        "community": "Abereke",
        "latitude": 6.1800,
        "longitude": 4.7600,
        "children_under_5": 520,
        "school_children": 970,
        "flood_frequency_score": 76,
        "water_contamination_score": 70,
        "malaria_risk_score": 69,
        "heat_exposure_score": 63,
        "health_facility_access_score": 52,
        "safe_water_access_score": 40,
        "sanitation_access_score": 44,
        "field_report": "Seasonal flooding and poor drainage around households.",
        "recommended_action": "Prioritise malaria prevention, household hygiene and community surveillance."
    },
    {
        "community": "Etugbo",
        "latitude": 6.1500,
        "longitude": 4.8200,
        "children_under_5": 430,
        "school_children": 800,
        "flood_frequency_score": 65,
        "water_contamination_score": 61,
        "malaria_risk_score": 67,
        "heat_exposure_score": 71,
        "health_facility_access_score": 58,
        "safe_water_access_score": 48,
        "sanitation_access_score": 46,
        "field_report": "Heat exposure and malaria risk are increasing during seasonal transitions.",
        "recommended_action": "Strengthen heat-risk messaging, malaria prevention and school-based alerts."
    }
]

df = pd.DataFrame(data)

def calculate_risk(row):
    score = (
        row["flood_frequency_score"] * 0.25
        + row["water_contamination_score"] * 0.20
        + row["malaria_risk_score"] * 0.15
        + row["heat_exposure_score"] * 0.15
        + (100 - row["safe_water_access_score"]) * 0.10
        + (100 - row["sanitation_access_score"]) * 0.10
        + (100 - row["health_facility_access_score"]) * 0.05
    )
    return round(score, 1)

def risk_level(score):
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Moderate"
    else:
        return "Low"

def main_hazard(row):
    hazards = {
        "Flood exposure": row["flood_frequency_score"],
        "Water contamination": row["water_contamination_score"],
        "Malaria risk": row["malaria_risk_score"],
        "Heat exposure": row["heat_exposure_score"]
    }
    return max(hazards, key=hazards.get)

df["risk_score"] = df.apply(calculate_risk, axis=1)
df["risk_level"] = df["risk_score"].apply(risk_level)
df["main_hazard"] = df.apply(main_hazard, axis=1)

st.sidebar.header("Prototype Navigation")
page = st.sidebar.radio(
    "Select section",
    [
        "Overview",
        "Community Risk Dashboard",
        "Climate-Health Alert Generator",
        "Live Weather Signal",
        "UNICEF Readiness"
    ]
)

if page == "Overview":
    st.subheader("Prototype Overview")

    total_communities = len(df)
    total_children_under_5 = int(df["children_under_5"].sum())
    total_school_children = int(df["school_children"].sum())
    high_risk_count = len(df[df["risk_level"] == "High"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Communities Monitored", total_communities)
    col2.metric("Children Under 5", total_children_under_5)
    col3.metric("School-Age Children", total_school_children)
    col4.metric("High-Risk Communities", high_risk_count)

    st.markdown("### Community Risk Map")
    st.map(df[["latitude", "longitude"]])

    st.markdown("### What this prototype demonstrates")
    st.write(
        """
        AquaMed360 demonstrates how community vulnerability indicators, climate exposure variables
        and child health risk factors can be combined into a simple risk intelligence platform
        for early warning, preparedness and local response.
        """
    )

elif page == "Community Risk Dashboard":
    st.subheader("Community Risk Dashboard")

    display_df = df[
        [
            "community",
            "children_under_5",
            "school_children",
            "risk_score",
            "risk_level",
            "main_hazard",
            "recommended_action"
        ]
    ].sort_values(by="risk_score", ascending=False)

    st.dataframe(display_df, use_container_width=True)

    st.markdown("### Risk Score Chart")
    chart_df = display_df.set_index("community")[["risk_score"]]
    st.bar_chart(chart_df)

    st.markdown("### Risk Scoring Methodology")
    st.write(
        """
        The risk score combines flood frequency, water contamination, malaria risk, heat exposure,
        safe water access, sanitation access and health facility access. Higher scores indicate
        stronger need for early warning, community health outreach and child-focused preparedness.
        """
    )

elif page == "Climate-Health Alert Generator":
    st.subheader("Climate-Health Alert Generator")

    selected_community = st.selectbox("Select community", df["community"])
    row = df[df["community"] == selected_community].iloc[0]

    st.markdown(f"## Alert for {selected_community}")
    st.metric("Child Climate-Health Risk Score", row["risk_score"])
    st.metric("Risk Level", row["risk_level"])
    st.metric("Main Hazard", row["main_hazard"])

    if row["risk_level"] == "High":
        alert_message = f"""
        **High Risk Alert: {selected_community}**

        Flood exposure, water safety and child health risks are elevated. Community health workers
        should prioritise household water safety messaging, diarrhoeal disease surveillance,
        malaria prevention, referral pathways for children under five, and school-based preparedness.

        **Recommended action:** {row["recommended_action"]}
        """
    elif row["risk_level"] == "Moderate":
        alert_message = f"""
        **Moderate Risk Advisory: {selected_community}**

        Climate-health risks are present and should be monitored. Community volunteers should
        strengthen household awareness, monitor child illness signals, and report flood or water
        contamination changes.

        **Recommended action:** {row["recommended_action"]}
        """
    else:
        alert_message = f"""
        **Low Risk Notice: {selected_community}**

        Current risk is low, but routine monitoring should continue.

        **Recommended action:** {row["recommended_action"]}
        """

    st.info(alert_message)

    st.markdown("### Field report")
    st.write(row["field_report"])

elif page == "Live Weather Signal":
    st.subheader("Live Weather Signal")

    selected_community = st.selectbox("Select community", df["community"])
    row = df[df["community"] == selected_community].iloc[0]

    latitude = row["latitude"]
    longitude = row["longitude"]

    st.write(
        f"This page pulls a live weather signal for **{selected_community}** using latitude {latitude} and longitude {longitude}."
    )

    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}"
            "&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
        )
        response = requests.get(url, timeout=10)
        weather = response.json()
        current = weather.get("current", {})

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{current.get('temperature_2m', 'N/A')} °C")
        col2.metric("Humidity", f"{current.get('relative_humidity_2m', 'N/A')}%")
        col3.metric("Precipitation", f"{current.get('precipitation', 'N/A')} mm")
        col4.metric("Wind Speed", f"{current.get('wind_speed_10m', 'N/A')} km/h")

        st.caption(f"Last updated: {current.get('time', 'Unavailable')}")
    except Exception as error:
        st.error("Live weather signal could not be loaded. The prototype can still run with stored field data.")
        st.write(error)

elif page == "UNICEF Readiness":
    st.subheader("UNICEF Venture Fund Readiness")

    st.markdown(
        """
        ### Prototype Status

        AquaMed360 is an early-stage working prototype that demonstrates climate-health risk scoring,
        community-level hazard monitoring, live weather signal integration and child-focused alert generation.

        ### Target Users

        - Community health workers
        - Local schools
        - Caregivers
        - Local government health and environment teams
        - Humanitarian and child protection responders

        ### Child Impact Pathway

        The prototype supports earlier identification of communities where children face increased risks
        from flooding, contaminated water, malaria exposure, heat stress and weak access to health services.

        ### Open-Source Commitment

        Catalyst Innov Dev Ltd will release the core risk-scoring model, documentation and non-sensitive
        prototype code under an open-source licence.

        ### FCAAI Field Validation Role

        FCAAI will support community entry, safeguarding, field feedback, data validation and pilot learning
        in coastal communities in Ondo State, Nigeria.

        ### Next Development Milestones

        1. Expand from 3 prototype communities to 10 pilot communities.
        2. Connect KoboToolbox field reports to the dashboard.
        3. Improve risk scoring with validated health and climate datasets.
        4. Add SMS or WhatsApp alert delivery.
        5. Publish open-source documentation and implementation toolkit.
        """
    )

st.sidebar.markdown("---")
st.sidebar.caption("Prototype developed for UNICEF Climate and Health 2026 application readiness.")
