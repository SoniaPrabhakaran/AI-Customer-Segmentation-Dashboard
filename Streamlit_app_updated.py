# Streamlit_app_updated.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# --- Page Config ---
st.set_page_config(page_title="AI-Powered Customer Segmentation Dashboard", layout="wide")

# --- Title ---
st.title("📊 AI-Powered Customer Segmentation Dashboard")
st.markdown("Automated KPIs + AI Narratives + Analyst Insights")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", encoding='unicode_escape')
    df = df.dropna(subset=['CustomerID'])
    df = df[df['Quantity'] > 0]
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Total'] = df['Quantity'] * df['UnitPrice']
    return df

df = load_data()
snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)

# --- KPI Calculations ---
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'count',
    'Total': 'sum'
})
rfm.rename(columns={'InvoiceDate':'Recency','InvoiceNo':'Frequency','Total':'Monetary'}, inplace=True)

# --- KPI Cards ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Top 20% Revenue Share", f"{round(rfm['Monetary'].nlargest(int(len(rfm)*0.2)).sum()/rfm['Monetary'].sum()*100,2)}%")
col2.metric("Inactive Customers (>90d)", f"{round((rfm['Recency']>90).mean()*100,2)}%")
col3.metric("Avg Frequency (Loyal)", f"{round(rfm[rfm['Frequency']>=rfm['Frequency'].median()]['Frequency'].mean(),2)}")
col4.metric("Champions Revenue Share", f"{round(rfm[rfm['Monetary']>=rfm['Monetary'].quantile(0.75)]['Monetary'].sum()/rfm['Monetary'].sum()*100,2)}%")
col5.metric("Average Order Value", f"{round(df.groupby('InvoiceNo')['Total'].sum().mean(),2)}")

# --- AI vs Analyst Interpretations ---
st.subheader("🤖 AI vs 👩 Analyst Interpretations")

interpretations = {
    "CLV": {
        "AI": "Top 20% of customers drive most revenue due to frequent and high-value purchases.",
        "Analyst": """High-value customers are the backbone of revenue. Beyond identifying them, 
        a structured VIP retention program is essential — tiered loyalty rewards, personalized bundles, 
        and exclusive offers. Protecting this segment ensures long-term stability and reduces dependency 
        on costly new customer acquisition."""
    },
    "Recency": {
        "AI": "Customers inactive >90 days are at churn risk.",
        "Analyst": """Inactive customers (>90 days) represent significant churn risk. Re-engagement strategies 
        such as targeted win-back campaigns, seasonal promotions, and personalized communication can help. 
        Segmenting inactive customers by past purchase behavior allows tailored offers that resonate with 
        their preferences, increasing reactivation likelihood."""
    },
    "Frequency": {
        "AI": "Loyal customers form purchase habits, casual buyers need nudges.",
        "Analyst": """Purchase frequency indicates loyalty strength. Habit-building interventions like subscription 
        models, gamified loyalty points, and 'buy again' reminders can transform occasional buyers into repeat 
        customers. This boosts frequency while strengthening emotional connection with the brand."""
    },
    "Revenue Contribution": {
        "AI": "Champions dominate revenue, At-Risk customers are slipping away.",
        "Analyst": """Champions contribute disproportionately to revenue, while At-Risk customers signal leakage. 
        A dual strategy is recommended: nurture Champions with exclusive experiences (priority service, early 
        product access, premium support) while designing retention campaigns for At-Risk customers. This maximizes 
        current revenue and minimizes future losses."""
    },
    "AOV": {
        "AI": "High AOV reflects trust and upsell potential.",
        "Analyst": """AOV reflects customer trust and willingness to spend. Systematic growth tactics include curated 
        product bundles, premium add-ons, and personalized recommendations. By analyzing purchase patterns, businesses 
        can design offers that feel natural, lifting AOV without appearing pushy."""
    }
}

for kpi, insight in interpretations.items():
    st.markdown(f"**{kpi}**")
    st.write(f"🤖 AI Insight: {insight['AI']}")
    st.write(f"👩 Analyst Interpretation: {insight['Analyst']}")
    st.markdown("---")

# --- What-If Simulator ---
st.subheader("🔮 What-If Revenue Simulator")

aov_slider = st.slider("Adjust Average Order Value (%)", -50, 50, 0)
freq_slider = st.slider("Adjust Purchase Frequency (%)", -50, 50, 0)

base_revenue = rfm['Monetary'].sum()
simulated_revenue = base_revenue * (1 + aov_slider/100) * (1 + freq_slider/100)

st.metric("Simulated Revenue", f"${round(simulated_revenue,2)}", f"{round((simulated_revenue-base_revenue)/base_revenue*100,2)}% change")

st.write("🤖 AI Narrative: Increasing AOV and Frequency boosts revenue exponentially. Balanced growth across both metrics is more sustainable than relying on one alone.")
st.write("👩 Analyst Recommendation: Focus on upselling bundles to lift AOV while designing loyalty programs to increase Frequency.")
