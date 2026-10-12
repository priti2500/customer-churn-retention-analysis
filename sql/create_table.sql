-- Customer churn table (PostgreSQL)
-- Loads the cleaned file created by src/data_cleaning.py.
-- Run from the project folder: psql -d churn_db -f sql/create_table.sql

DROP TABLE IF EXISTS customer_churn;

CREATE TABLE customer_churn (
    customer_id          VARCHAR(10) PRIMARY KEY,
    gender               VARCHAR(10),
    age                  INT,
    tenure_months        INT,
    contract_type        VARCHAR(20),
    monthly_charges      NUMERIC(10, 2),
    total_charges        NUMERIC(12, 2),
    payment_method       VARCHAR(20),
    service_type         VARCHAR(30),
    internet_service     VARCHAR(20),
    support_tickets      INT,
    usage_frequency      INT,
    region               VARCHAR(20),
    customer_segment     VARCHAR(20),
    churn                VARCHAR(3) CHECK (churn IN ('Yes', 'No')),
    tenure_group         VARCHAR(20),
    charge_band          VARCHAR(20),
    support_ticket_band  VARCHAR(5)
);

-- \copy runs in psql. In pgAdmin, use Import/Export on the table instead.
\copy customer_churn FROM 'data/cleaned_customer_data.csv' WITH (FORMAT csv, HEADER true)

SELECT COUNT(*) AS rows_loaded FROM customer_churn;
