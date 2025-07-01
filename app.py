import pandas as pd
import streamlit as st

# Căile locale către fișiere
CSV_PATH = "data/web_bl_bs_sl_an2023.csv"                 # legenda
DATA_PATH = "data/web_bl_bs_sl_an2024_convertit.csv"      # datele reale

@st.cache_data(show_spinner="Se încarcă datele...")
def incarca_date_si_legenda():
    # 1) Încarcă datele reale, cu autodetectare de separator
    df_data = pd.read_csv(DATA_PATH, sep=None, engine='python', dtype=str)
    df_data.columns = df_data.columns.str.strip()

    # 2) Încarcă legenda: fiecare rând "Explicație;Cod"
    df_legend_raw = pd.read_csv(CSV_PATH, sep=";", header=None, names=["Label"], dtype=str)
    legend_dict = {}
    for line in df_legend_raw["Label"].dropna():
        if ";" in line:
            descriere, cod = line.split(";", 1)
            legend_dict[cod.strip()] = descriere.strip()

    return df_data, legend_dict

# TITLU
st.title("🔍 Căutare situații financiare 2023")

# INPUT-URI
cui = st.text_input("Caută după CUI:")
caen = st.text_input("Caută după cod CAEN:")

# ÎNCĂRCARE DATE + LEGENDA
df, legenda = incarca_date_si_legenda()

# Verifică că există coloanele obligatorii
mandatory = ["CUI", "CAEN"]
missing = [col for col in mandatory if col not in df.columns]
if missing:
    st.error(f"Lipsește coloana(e): {', '.join(missing)} din fișierul de date.")
    st.write("Coloane disponibile:", df.columns.tolist())
    st.stop()

# FILTRARE
rezultate = df
if cui:
    rezultate = rezultate[rezultate["CUI"].str.strip() == cui.strip()]
if caen:
    rezultate = rezultate[rezultate["CAEN"].str.strip() == caen.strip()]

# AFIȘARE REZULTATE
st.subheader("📄 Rezultate")
if rezultate.empty:
    st.warning("⚠️ Nicio înregistrare găsită.")
else:
    st.success(f"✅ {len(rezultate)} înregistrare(gă) găsită(e).")
    st.dataframe(rezultate, use_container_width=True)

    # AFIȘARE LEGENDA
    st.subheader("📘 Legenda coloanelor")
    df_legenda = pd.DataFrame.from_dict(legenda, orient="index", columns=["Descriere"])
    df_legenda.index.name = "Cod coloană"
    st.dataframe(df_legenda, use_container_width=True)
