import streamlit as st
import pandas as pd
from gspread_pandas import Spread
from google.oauth2.service_account import Credentials

# Charger les identifiants du compte de service
creds = Credentials.from_service_account_file('service_account.json')

# Initialiser la connexion à Google Sheets
spread = Spread("11P3mxax78oqjQs_J6nHTM0th-_LlnPf7A_c9rJjkKE8", config=creds)

# Essayer de charger les données des feuilles
try:
    df_stock = spread.sheet_to_df(sheet='stock', index=0).reset_index()
    df_hist = spread.sheet_to_df(sheet='historique', index=0).reset_index()
except Exception as e:
    st.error(f"Erreur technique : {e}")
    st.stop()

st.title("📦 Gestion Stock Ergo")
