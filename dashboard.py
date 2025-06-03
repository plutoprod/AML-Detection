import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="AML Detection Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    transactions = pd.read_csv('synthetic_transactions.csv', parse_dates=['transaction_date'])
    customers = pd.read_csv('synthetic_customers.csv')
    flagged = pd.read_csv('flagged_transactions.csv', parse_dates=['transaction_date'])
    # Convert semicolon separated flags back to a Python list
    flagged['flags'] = flagged['flags'].fillna('').apply(lambda x: x.split(';') if x else [])
    return transactions, customers, flagged

transactions, customers, flagged = load_data()

# Title
st.title("🕵️ AML Detection Dashboard")

# Key Metrics
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", f"{len(transactions):,}")
col2.metric("Flagged Transactions", f"{len(flagged):,}")
col3.metric("Unique Customers", f"{transactions['sender_id'].nunique():,}")

# Detection Flags Distribution
st.subheader("Detection Flags Distribution")
# Explode the flags list into separate rows
flagged_exploded = flagged.explode('flags')
flag_counts = flagged_exploded['flags'].value_counts().reset_index()
flag_counts.columns = ['Detection Scenario', 'Count']
fig_flags = px.bar(flag_counts, x='Detection Scenario', y='Count', color='Detection Scenario',
                   title="Number of Transactions per Detection Scenario")
st.plotly_chart(fig_flags, use_container_width=True)

# Transactions Over Time
st.subheader("Transactions Over Time")
transactions['date'] = transactions['transaction_date'].dt.date
daily_counts = transactions.groupby('date').size().reset_index(name='Transaction Count')
fig_time = px.line(daily_counts, x='date', y='Transaction Count', title="Daily Transaction Volume")
st.plotly_chart(fig_time, use_container_width=True)

# High-Risk Countries Analysis
st.subheader("Transactions to High-Risk Countries")
high_risk_countries = ['CountryA', 'CountryB', 'CountryC']  # Replace with actual high-risk countries
high_risk_txns = flagged[flagged['receiver_country'].isin(high_risk_countries)]
country_counts = high_risk_txns['receiver_country'].value_counts().reset_index()
country_counts.columns = ['Country', 'Count']
fig_countries = px.bar(country_counts, x='Country', y='Count', color='Country',
                       title="Flagged Transactions by High-Risk Country")
st.plotly_chart(fig_countries, use_container_width=True)

# Top Flagged Customers
st.subheader("Top Flagged Customers")
top_customers = flagged['sender_id'].value_counts().head(10).reset_index()
top_customers.columns = ['Customer ID', 'Flagged Transactions']
fig_customers = px.bar(top_customers, x='Customer ID', y='Flagged Transactions',
                       title="Top 10 Customers by Flagged Transactions")
st.plotly_chart(fig_customers, use_container_width=True)

# Detailed Flagged Transactions
st.subheader("Detailed Flagged Transactions")
st.dataframe(flagged[['transaction_date', 'sender_id', 'receiver_id', 'amount', 'transaction_type', 'flags']])
