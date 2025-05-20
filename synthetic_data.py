import pandas as pd
import numpy as np
from faker import Faker
import random

# Initialize Faker and set seeds for reproducibility
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Parameters
n_customers = 10000
n_transactions = 500000

# Generate synthetic customers
customer_ids = [f"CUST{str(i).zfill(5)}" for i in range(n_customers)]
customers = pd.DataFrame({
    'customer_id': customer_ids,
    'name': [fake.name() for _ in range(n_customers)],
    'dob': [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(n_customers)],
    'address': [fake.address().replace('\n', ', ') for _ in range(n_customers)],
    'account_open_date': [fake.date_between(start_date='-10y', end_date='today') for _ in range(n_customers)],
    'country': [fake.country() for _ in range(n_customers)]
})

# Helper function to generate a single transaction
def generate_transaction():
    sender = random.choice(customer_ids)
    receiver = random.choice(customer_ids)
    while receiver == sender:
        receiver = random.choice(customer_ids)
    amount = round(np.random.exponential(scale=3000), 2)  # Skewed distribution
    transaction_date = fake.date_time_between(start_date='-2y', end_date='now')
    transaction_type = random.choices(
        ['wire_transfer', 'cash_deposit', 'cash_withdrawal', 'ACH_transfer', 'POS_purchase'],
        weights=[0.15, 0.25, 0.2, 0.25, 0.15],
        k=1
    )[0]
    return [sender, receiver, amount, transaction_date, transaction_type]

# Generate transactions
transactions = pd.DataFrame(
    [generate_transaction() for _ in range(n_transactions)],
    columns=['sender_id', 'receiver_id', 'amount', 'transaction_date', 'transaction_type']
)

# Save to CSV
customers.to_csv('synthetic_customers.csv', index=False)
transactions.to_csv('synthetic_transactions.csv', index=False)

print("Synthetic data generation complete. Files saved as 'synthetic_customers.csv' and 'synthetic_transactions.csv'.")
