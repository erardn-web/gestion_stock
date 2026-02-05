import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Configuration de la page Streamlit
st.set_page_config(page_title="Stock Ergo Pro", layout="wide")

# --- Configuration des Autorisations ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# --- INITIALISATION ---
try:
    # Ouvrir la feuille de calcul
    spreadsheet = client.open("Nom_de_votre_document")  # Remplacez par le nom de votre document
    df_stock = pd.DataFrame(spreadsheet.worksheet("stock").get_all_records())
    df_hist = pd.DataFrame(spreadsheet.worksheet("historique").get_all_records())
except Exception as e:
    st.error(f"Erreur technique : {e}")
    st.stop()

# Titre de l'application
st.title("📦 Gestion Stock Ergo")

# Création des onglets
tab1, tab2, tab3 = st.tabs(["📋 Inventaire", "🔄 Mouvements", "➕ Ajouter"])

# Onglet 1 : Inventaire
with tab1:
    st.subheader("Articles en stock")
    st.dataframe(df_stock, use_container_width=True, hide_index=True)

# Onglet 2 : Mouvements
with tab2:
    if not df_stock.empty:
        with st.form("mouvement"):
            article = st.selectbox("Article", df_stock["nom"].unique())
            action = st.selectbox("Action", ["Prêt", "Retour", "Vente"])
            note = st.text_input("Note (ex: Mme Martin)")
            if st.form_submit_button("Enregistrer"):
                # Mise à jour du Stock
                statuts = {"Prêt": "Prêté", "Retour": "Disponible", "Vente": "Vendu"}
                df_stock.loc[df_stock["nom"] == article, "statut"] = statuts[action]
                
                # Mise à jour Historique
                new_h = pd.DataFrame([[article, datetime.now().strftime("%d/%m/%Y"), action, note]], 
                                      columns=["nom_article", "date", "action", "notes"])
                df_hist = pd.concat([df_hist, new_h], ignore_index=True)

                # Écrire dans Google Sheets
                spreadsheet.worksheet("stock").update([df_stock.columns.values.tolist()] + df_stock.values.tolist())
                spreadsheet.worksheet("historique").update([df_hist.columns.values.tolist()] + df_hist.values.tolist())
                
                st.success("Mouvement enregistré !")
                st.rerun()

# Onglet 3 : Ajouter
with tab3:
    with st.form("ajout"):
        nom = st.text_input("Nom de l'objet")
        prov = st.selectbox("Provenance", ["Achat", "Don", "Prêt fournisseur"])
        if st.form_submit_button("Ajouter"):
            # Calcul ID
            try:
                nid = int(pd.to_numeric(df_stock["id"]).max() + 1)
            except:
                nid = 1
            new_item = pd.DataFrame([[nid, nom, prov, "", "Disponible"]], 
                                     columns=["id", "nom", "provenance", "options", "statut"])
            df_stock = pd.concat([df_stock, new_item], ignore_index=True)

            # Écrire dans Google Sheets
            spreadsheet.worksheet("stock").update([df_stock.columns.values.tolist()] + df_stock.values.tolist())
            st.success("Ajouté !")
            st.rerun()

# Affichage de l'historique
st.divider()
st.subheader("📜 Historique")
st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, hide_index=True)
