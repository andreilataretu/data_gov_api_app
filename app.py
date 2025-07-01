import streamlit as st
import pandas as pd
import requests
from collections import defaultdict

st.set_page_config(page_title="Situații financiare 2024", layout="wide")

st.title("📊 Vizualizator Situații Financiare 2024")
st.markdown("""
Această aplicație te ajută să explorezi fișiere mari din datasetul [data.gov.ro/situatii_financiare_2024](https://data.gov.ro/dataset/situatii_financiare_2024), fără a le încărca integral în memorie.

### Funcționalități:
- 🔍 Căutare eficientă după **Cod fiscal** sau **Denumire firmă**
- 📊 Agregare după **Cod CAEN**
- 👁️ Previzualizare rapidă a fișierelor mari
""")

# === CONFIG ===
DATASET_ID = "situatii_financiare_2024"
API_URL = f"https://data.gov.ro/api/3/action/package_show?id={DATASET_ID}"
CHUNKSIZE = 50000  # Număr de rânduri citite pe bucăți

# === Pas 1: Preluare resurse dataset ===
@st.cache_data(show_spinner=False)
def get_csv_resources():
    response = requests.get(API_URL)
    if not response.ok:
        return []
    result = response.json()["result"]
    return [res for res in result["resources"] if res["format"].lower() == "csv"]

csv_files = get_csv_resources()

if not csv_files:
    st.error("❌ Nu au fost găsite fișiere CSV în dataset.")
    st.stop()

# === Pas 2: Selectează fișier ===
selected_name = st.selectbox("🗂️ Selectează fișierul CSV", [f["name"] for f in csv_files])
selected_file = next(f for f in csv_files if f["name"] == selected_name)
file_url = selected_file["url"]

# === Pas 3: Previzualizare rapidă ===
@st.cache_data(show_spinner=False)
def load_preview(url, nrows=1000):
    return pd.read_csv(url, nrows=nrows, low_memory=False)

st.subheader("👁️ Previzualizare fișier (primele 1000 de rânduri)")
with st.spinner("Se încarcă datele..."):
    try:
        preview_df = load_preview(file_url)
        st.dataframe(preview_df, use_container_width=True)
    except Exception as e:
        st.error(f"Eroare la încărcare: {e}")

# === Pas 4: Căutare firmă ===
st.subheader("🔍 Căutare după Cod fiscal sau Denumire firmă")

col1, col2 = st.columns(2)
with col1:
    cif_search = st.text_input("Cod fiscal exact")
with col2:
    den_search = st.text_input("Denumire firmă (parțial)")

def search_csv(url, cif=None, denumire=None, chunksize=CHUNKSIZE):
    matches = []
    for chunk in pd.read_csv(url, chunksize=chunksize, low_memory=False):
        if cif:
            chunk = chunk[chunk['cod fiscal'].astype(str) == cif.strip()]
        if denumire:
            chunk = chunk[chunk['denumire'].str.contains(denumire.strip(), case=False, na=False)]
        if not chunk.empty:
            matches.append(chunk)
    return pd.concat(matches) if matches else pd.DataFrame()

if cif_search or den_search:
    with st.spinner("Căutare în curs..."):
        results = search_csv(file_url, cif=cif_search, denumire=den_search)
    st.success(f"{len(results)} rânduri găsite.")
    st.dataframe(results, use_container_width=True)

# === Pas 5: Agregare după Cod CAEN ===
st.subheader("📊 Agregare după Cod CAEN")

def aggregate_caen(url, caen_col='cod caen', afaceri_col='cifra de afaceri', chunksize=CHUNKSIZE):
    counts = defaultdict(int)
    sums = defaultdict(float)

    for chunk in pd.read_csv(url, chunksize=chunksize, low_memory=False):
        cols = [col.lower() for col in chunk.columns]
        try:
            caen_real = next(c for c in chunk.columns if c.lower() == caen_col)
            afaceri_real = next(c for c in chunk.columns if afaceri_col in c.lower())
        except StopIteration:
            continue

        chunk = chunk[[caen_real, afaceri_real]].dropna()
        for row in chunk.itertuples(index=False):
            try:
                caen = str(row[0])
                cifra = float(row[1])
                counts[caen] += 1
                sums[caen] += cifra
            except:
                continue

    df = pd.DataFrame({
        'Cod CAEN': list(counts.keys()),
        'Număr firme': list(counts.values()),
        'Sumă cifră afaceri': list(sums.values())
    }).sort_values(by='Sumă cifră afaceri', ascending=False)

    return df

if st.button("🔄 Rulează agregarea"):
    with st.spinner("Se procesează fișierul..."):
        agg_df = aggregate_caen(file_url)
    st.success("Agregare finalizată.")
    st.dataframe(agg_df, use_container_width=True)
