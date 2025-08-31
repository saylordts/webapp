import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ---------- CONFIG ----------
# Use Streamlit secrets for your database credentials
DB_URL = st.secrets["DB_URL"]
engine = create_engine(DB_URL)

st.title("Financial CSV Tracker")

# ---------- CSV Upload ----------
uploaded_files = st.file_uploader(
    "Upload CSV files from your credit cards",
    type=["csv"],
    accept_multiple_files=True
)

for uploaded_file in uploaded_files:
    df = pd.read_csv(uploaded_file)

    # ---------- Extract only relevant columns ----------
    # Adjust column names to match your CSVs
    columns_needed = ['date', 'amount', 'merchant', 'category']
    df = df[[col for col in columns_needed if col in df.columns]]

    if df.empty:
        st.warning(f"No relevant columns found in {uploaded_file.name}")
        continue

    st.write(f"Preview of {uploaded_file.name}")
    st.dataframe(df.head())

    # ---------- Save to PostgreSQL ----------
    try:
        df.to_sql('transactions', engine, if_exists='append', index=False)
        st.success(f"{uploaded_file.name} saved to database!")
    except Exception as e:
        st.error(f"Error saving {uploaded_file.name}: {e}")

# ---------- Simple Reporting ----------
if st.button("Show Monthly Summary"):
    try:
        df_all = pd.read_sql(text("SELECT * FROM transactions"), engine)
        if 'date' in df_all.columns and 'amount' in df_all.columns:
            df_all['date'] = pd.to_datetime(df_all['date'])
            monthly = df_all.groupby(df_all['date'].dt.to_period("M"))['amount'].sum()
            st.write("Monthly Totals:")
            st.bar_chart(monthly)
        else:
            st.warning("No 'date' and 'amount' columns found for summary.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
