import streamlit as st
import pandas as pd
from gspread_pandas import Spread
from datetime import datetime

st.set_page_config(page_title="Stock Ergo Pro", layout="wide")

# --- CLE PRIVEE (COPIER-COLLER SANS \n MAIS AVEC DE VRAIS SAUTS DE LIGNE) ---
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCXmLNyCfYDgYPk
QLcRittmVdJOLm4mmlRLmrjva3moMQBdSw36OFdw0w2SLQMhGsxbP7yFaTlAXv4s
AwH6nF/MOJ1JqFE5gIMIbz18lqbEHEXqMHl80mnXz6ZyreFZrjQfz5yaEpC7k6nf
zQaX17iQ3iCuBjUR+qcb6TW0xsItJjU4srw8ITA1/EbRmxLnBSEza6EYpm3ZkJqr
fWGwA4oQAHB5AjeHvy/Wdb3Ji4b6eLDad75ttY6niia9n91GnYrf0mzCHDUvAqNG
IixGPV4Bt7M/s7o6m8JiLFtgMQ5iPXXDFFVb1xV7yw7AzvESurmwcMbDUH/WLyvU
lnPqUDLJAgMBAAECgf8gBrfiSmMZhS3CoD63YLPOgChYhqE+sTFIclIfl9UGc1O1
tzrSDJUXK39HzQ/xg80oeePvS2DiTdnknRNjSSXz6aymTajbPQscUmPrA5NiWuwU
+FNcy2xmQLgpV2gESjPjhI4mU/BqWwfIVXLPIVkclyYlnaoYjPDrie6OrRmDRVE5
QwF7+xTmjyfk+BOkIGDI09AYK6OtPSv6+YCGDBTTGrDPJhP2htMx2OiqQ0vJQja0
aYw6iCZzuz1vITadtYvg3sV+EtPWk/HN5r0D9ikkKkfE4QhzVA6xJfHPwuWvgmDI
DtbrST8OemZpvUWX0eLowKampbkyHFP5eNyTauECgYEAyF5po23n0ykxDZ+xBGvj
VpoNXf53aRM44LwPJI3ZoEJSCLAeBTGRSklpTBYUmqhJ8Rfh2F89bpe+fB+e89jo
6ab+pIc+K8WxgQ+zEyNUotjdC4oam8wA5SdByFRh0IGwdg6VaMNTYnqhbXk4tRFN
ntFYV1EiYffH3k2ttbNigJHECgYEAwa+0fDn5JmNNICtoBhII2Z2GCRflVS15+Mxr
j5UcZkS3Z8zOpDL43Dg28wXhnAPScp7iBCggV1x8QuGtYPe8ie3hqubLKpGavcpL
ZUPixO24tW6hjOWY2sRlZEvrcWhKbfV9KwcnzDSP/6yyJ3+cc+YffpKNNk63SR36
ExHxv9kCgYAZpqyTdZCGIfHbsqPw0vcJsTMg42DaHNHdQ3YU0ewYbiUeY52UQKI/
BmLqkLEWk5DTwqDxGFA/BkImlc29nflDYFOdMIsvA2IUCbR9MLq3FlhGD+oUI+vB
amMriFH1ZYT3uCo8fTUBmH1uDGTMGWj/Oz4ULS8IgJ+XSdt6YckuoQKBgQCjA/Y9
RDHt3FASjlX8Hfuy5MDmMGWFvkPVYn/5FgAUFyviQl99laUc/HdLLZ0ISbM7Y3xJ
EVi/DolLZVQetAPMdxmjVKKUjn4V1QiGD4/yPT5j/dwckTWIkxnfQ4LDLYrPZ3nU
2C3n0imMgFZlpiMQ7RN+3Wva1H+xG3jZyhWVaQKBgCFuQs+EllaHZYS/EVRgKqKs
/MMrHJyAzJSc5ItUjGJVXDamjy38MKh50mQ6L1iXWmf4ilw8xdWYHhqjfVWYEKWn
KaCKiw3wJZqpCHZC3ZP+6qAclgxczDe/AStCeYv/c7EU5P7lTLVEQf2XoETqAX6e
B3pqwbNSZBox8qUCgY5G
-----END PRIVATE KEY-----"""

creds = {
    "type": "service_account",
    "project_id": "stock-ergo",
    "private_key": PRIVATE_KEY,
    "client_email": "id-6neuf@stock-ergo.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com",
}

# --- INITIALISATION ---
try:
    spread = Spread("11P3mxax78oqjQs_J6nHTM0th-_LlnPf7A_c9rJjkKE8", config=creds)
    df_stock = spread.sheet_to_df(sheet='stock', index=0).reset_index()
    df_hist = spread.sheet_to_df(sheet='historique', index=0).reset_index()
except Exception as e:
    st.error(f"Erreur technique : {e}")
    st.stop()

st.title("📦 Gestion Stock Ergo")

tab1, tab2, tab3 = st.tabs(["📋 Inventaire", "🔄 Mouvements", "➕ Ajouter"])

with tab1:
    st.subheader("Articles en stock")
    st.dataframe(df_stock, use_container_width=True, hide_index=True)

with tab2:
    if not df_stock.empty:
        with st.form("mouvement"):
            article = st.selectbox("Article", df_stock["nom"].unique())
            action = st.selectbox("Action", ["Prêt", "Retour", "Vente"])
            note = st.text_input("Note (ex: Mme Martin)")
            if st.form_submit_button("Enregistrer"):
                # Mise à jour Stock
                statuts = {"Prêt": "Prêté", "Retour": "Disponible", "Vente": "Vendu"}
                df_stock.loc[df_stock["nom"] == article, "statut"] = statuts[action]
                spread.df_to_sheet(df_stock, sheet='stock', index=False, replace=True)
                
                # Mise à jour Historique
                new_h = pd.DataFrame([[article, datetime.now().strftime("%d/%m/%Y"), action, note]], 
                                    columns=["nom_article", "date", "action", "notes"])
                df_hist = pd.concat([df_hist, new_h], ignore_index=True)
                spread.df_to_sheet(df_hist, sheet='historique', index=False, replace=True)
                
                st.success("Mouvement enregistré !")
                st.rerun()

with tab3:
    with st.form("ajout"):
        nom = st.text_input("Nom de l'objet")
        prov = st.selectbox("Provenance", ["Achat", "Don", "Prêt fournisseur"])
        if st.form_submit_button("Ajouter"):
            # Calcul ID (on gère si la colonne id est vide)
            try:
                nid = int(pd.to_numeric(df_stock["id"]).max() + 1)
            except:
                nid = 1
            new_item = pd.DataFrame([[nid, nom, prov, "", "Disponible"]], 
                                   columns=["id", "nom", "provenance", "options", "statut"])
            df_stock = pd.concat([df_stock, new_item], ignore_index=True)
            spread.df_to_sheet(df_stock, sheet='stock', index=False, replace=True)
            st.success("Ajouté !")
            st.rerun()

st.divider()
st.subheader("📜 Historique")
st.dataframe(df_hist.sort_index(ascending=False), use_container_width=True, hide_index=True)
