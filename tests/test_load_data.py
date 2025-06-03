import pandas as pd
from pathlib import Path
import os
from dashboard import load_data


def test_load_data_flag_conversion(tmp_path, monkeypatch):
    # Create minimal CSV files expected by load_data
    transactions = pd.DataFrame({
        'sender_id': ['A'],
        'receiver_id': ['B'],
        'amount': [100],
        'transaction_date': pd.to_datetime(['2021-01-01']),
        'transaction_type': ['wire_transfer']
    })
    customers = pd.DataFrame({
        'customer_id': ['B'],
        'country': ['CountryA']
    })
    flagged = pd.DataFrame({
        'transaction_date': pd.to_datetime(['2021-01-01']),
        'sender_id': ['A'],
        'receiver_id': ['B'],
        'amount': [100],
        'transaction_type': ['wire_transfer'],
        'receiver_country': ['CountryA'],
        'flags': ["['High-Value Transaction']"]
    })

    transactions.to_csv(tmp_path / 'synthetic_transactions.csv', index=False)
    customers.to_csv(tmp_path / 'synthetic_customers.csv', index=False)
    flagged.to_csv(tmp_path / 'flagged_transactions.csv', index=False)

    monkeypatch.chdir(tmp_path)
    t, c, f = load_data()

    assert f['flags'].iloc[0] == ['High-Value Transaction']
    exploded = f.explode('flags')
    counts = exploded['flags'].value_counts().to_dict()
    assert counts == {'High-Value Transaction': 1}
