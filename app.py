import streamlit as st
import pandas as pd
import plotly.express as px
from meridian_model_template import run_meridian_model, recommend_budget_allocation

st.set_page_config(page_title="AI MMM Tool", layout="centered")
st.title("📊 AI MMM Tool (with Budget & Revenue Target)")

uploaded_file = st.file_uploader("Upload Campaign Data (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    st.markdown("### 🎯 Choose Planning Objective")
    plan_choice = st.radio("Select one:", ["Enter Revenue Target", "Enter Spend Budget"])

    input_value = None
    if plan_choice == "Enter Revenue Target":
        input_value = st.number_input("💡 Enter your Revenue Target (₹ Crores)", min_value=0.0, step=0.5)
    elif plan_choice == "Enter Spend Budget":
        input_value = st.number_input("💰 Enter your Total Spend Budget (₹ Crores)", min_value=0.0, step=0.5)

    expected_media_cols = [
        "Affiliate_Spend", "AppleSearchAds_spend", "Contentnative_spend", "Coupon_spend",
        "DisplayBanner_spend", "DisplayVideo_spend", "DV360_spend", "FacebookAds_spend",
        "GoogleAds_spend", "IGPg_spend", "Influencer_spend", "JioAdPerformance_spend",
        "Outdoor_spend", "Performance_spend", "Print_spend", "Programmatic_spend",
        "Radio_spend", "ROIHunter_spend", "RTB_spend", "SEO_spend", "Snapchat_spend",
        "StarGreetz_spend", "TV_spend", "TwitterPerformance_spend"
    ]

    media_cols = [col for col in expected_media_cols if col in df.columns]
    target = "revenue"

    if not media_cols or target not in df.columns:
        st.error("❌ Required columns missing. Please check column names.")
    elif input_value == 0:
        st.warning("⚠️ Please input a non-zero value.")
    else:
        with st.spinner("Running MMM..."):
            results = run_meridian_model(df, media_cols, target)

        st.subheader("📈 MMM Results")
        st.dataframe(results)

        st.subheader("🧠 AI Recommendations")
        recs, scenarios = recommend_budget_allocation(results, input_value, plan_choice)
        st.dataframe(recs)

        st.subheader("🧪 Scenario Plans")
        for label, scenario_df in scenarios.items():
            st.markdown(f"#### {label}")
            st.dataframe(scenario_df)

        st.subheader("📉 ROI by Channel")
        fig1 = px.bar(results, x='media_channel', y='estimated_roi', color='media_channel')
        st.plotly_chart(fig1)

        st.subheader("📊 Contribution by Channel")
        fig2 = px.bar(results, x='media_channel', y='normalized_contribution', color='media_channel')
        st.plotly_chart(fig2)

        csv = recs.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Recommendation CSV", csv, "recommendation.csv", "text/csv")
else:
    st.info("⬆️ Please upload a CSV file to begin.")
