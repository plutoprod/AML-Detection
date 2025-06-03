import pandas as pd
import numpy as np
from datetime import timedelta

# Load synthetic data
transactions = pd.read_csv('synthetic_transactions.csv', parse_dates=['transaction_date'])
customers = pd.read_csv('synthetic_customers.csv')

# Merge receiver country information
transactions = transactions.merge(
    customers[['customer_id', 'country']],
    left_on='receiver_id',
    right_on='customer_id',
    how='left'
).rename(columns={'country': 'receiver_country'}).drop(columns=['customer_id'])

# Initialize flags column
transactions['flags'] = [[] for _ in range(len(transactions))]

# Rule 1: High-Value Transactions
def apply_high_value_rule(df, threshold=10000):
    condition = df['amount'] > threshold
    df.loc[condition, 'flags'] = df.loc[condition, 'flags'].apply(lambda x: x + ['High-Value Transaction'])
    return df

# Rule 2: Rapid Movement of Funds
def apply_rapid_movement_rule(df):
    df_sorted = df.sort_values(by=['sender_id', 'transaction_date'])
    df_sorted['prev_receiver'] = df_sorted.groupby('sender_id')['receiver_id'].shift(1)
    df_sorted['prev_date'] = df_sorted.groupby('sender_id')['transaction_date'].shift(1)
    df_sorted['time_diff'] = (df_sorted['transaction_date'] - df_sorted['prev_date']).dt.total_seconds() / 3600  # in hours

    rapid_movement_indices = df_sorted[
        (df_sorted['receiver_id'] == df_sorted['prev_receiver']) &
        (df_sorted['time_diff'] <= 24)
    ].index

    df.loc[rapid_movement_indices, 'flags'] = df.loc[rapid_movement_indices, 'flags'].apply(lambda x: x + ['Rapid Movement of Funds'])
    return df

# Rule 3: Structuring (Smurfing)
def apply_structuring_rule(df, structuring_threshold=9900, high_value_threshold=10000, structuring_timeframe=timedelta(days=1)):
    df_sorted = df.sort_values(by=['sender_id', 'transaction_date'])
    structuring_indices = []

    for sender, group in df_sorted.groupby('sender_id'):
        group = group.reset_index()
        for i in range(len(group)):
            count = 1
            total_amount = group.loc[i, 'amount']
            j = i + 1
            while j < len(group) and (group.loc[j, 'transaction_date'] - group.loc[i, 'transaction_date']) <= structuring_timeframe:
                if group.loc[j, 'amount'] < structuring_threshold:
                    count += 1
                    total_amount += group.loc[j, 'amount']
                j += 1
            if count >= 3 and total_amount >= high_value_threshold:
                structuring_indices.extend(group.loc[i:j-1, 'index'].tolist())

    df.loc[structuring_indices, 'flags'] = df.loc[structuring_indices, 'flags'].apply(lambda x: x + ['Structuring'])
    return df

# Rule 4: Transactions to High-Risk Countries
def apply_high_risk_country_rule(df, high_risk_countries):
    condition = df['receiver_country'].isin(high_risk_countries)
    df.loc[condition, 'flags'] = df.loc[condition, 'flags'].apply(lambda x: x + ['High-Risk Country'])
    return df

# Apply all rules
transactions = apply_high_value_rule(transactions)
transactions = apply_rapid_movement_rule(transactions)
transactions = apply_structuring_rule(transactions)
high_risk_countries = ["Afghanistan", "Albania", "Barbados", "Burkina Faso", "Cambodia", "Cayman Islands", "Democratic People's Republic of Korea (North Korea)", "Democratic Republic of the Congo", "Haiti", "Iran", "Jamaica", "Jordan", "Mali", "Malta", "Mozambique", "Myanmar", "Nicaragua", "Panama", "Philippines", "Senegal", "South Sudan", "Syria", "Tanzania", "Trinidad and Tobago", "Uganda", "United Arab Emirates", "Vanuatu", "Yemen", "Zimbabwe"] # Replace with actual high-risk countries
transactions = apply_high_risk_country_rule(transactions, high_risk_countries)

# Extract flagged transactions
flagged_transactions = transactions[transactions['flags'].apply(len) > 0].copy()

# Convert list of flags to a string so it round-trips via CSV
flagged_transactions['flags'] = flagged_transactions['flags'].apply(lambda x: ';'.join(x))

# Save flagged transactions to CSV
flagged_transactions.to_csv('flagged_transactions.csv', index=False)

print("Detection scenarios applied. Flagged transactions saved as 'flagged_transactions.csv'.")
