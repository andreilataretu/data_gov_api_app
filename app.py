import streamlit as st
import pandas as pd

st.set_page_config(page_title="Căutare avansată firme", layout="wide")

st.title("🔎 Căutare avansată în Situații Financiare 2024")
st.markdown("""
Aplicație pentru căutarea firmelor în fișierul financiar publicat pe [data.gov.ro](https://data.gov.ro/dataset/d3caacb6-2c08-445e-94e6-8d36d00ab250/resource/b9f399d8-b641-4a23-9de7-a1dd4427b4b0/download/web_bl_bs_sl_an2024.csv)

---

### ✅ Criterii disponibile:
- Cod fiscal exact **sau interval**
- Denumire firmă (parțial)
- Cod CAEN (exact sau parțial)
- Județ (selectabil)

Fișierul poate avea milioane de înregistrări — aplicația folosește procesare pe bucăți pentru eficiență.
""")

# === CONFIG
CSV_URL = "https://data.gov.ro/dataset/d3caacb6-2c08-445e-94e6-8d36d00ab250/resource/b9f399d8-b641-4a23-9de7-a1dd4427b4b0/download/web_bl_bs_sl_an2024.csv"
CHUNKSIZE = 50000

# === INPUT FILTERS
st.subheader("🎯 Criterii de filtrare")

col1, col2, col3 = st.columns(3)
with col1:
    cui_exact = st.text_input("🔑 CUI exact")
    cui_min = st.text_input("CUI minim (interval)")
with col2:
    cui_max = st.text_input("CUI maxim (interval)")
    denumire = st.text_input("Denumire firmă (parțial)")
with col3:
    caen = st.text_input("Cod CAEN (exact sau parțial)")
    judet = st.text_input("Județ (exact/parțial)")

# === FUNCȚIE DE CĂUTARE AVANSATĂ
def search_csv_advanced(url, cui_exact=None, cui_min=None, cui_max=None, den=None, caen_val=None, judet_val=None):
    results = []

    for chunk in pd.read_csv(url, chunksize=CHUNKSIZE, low_memory=False):
        cols = {col.lower().strip(): col for col in chunk.columns}
        
        col_cui = next((v for k, v in cols.items() if "cod fiscal" in k or "cui" in k), None)
        col_denumire = next((v for k, v in cols.items() if "denumire" in k), None)
        col_caen = next((v for k, v in cols.items() if "caen" in k), None)
        col_judet = next((v for k, v in cols.items() if "judet" in k or "județ" in k), None)

        if not any([col_cui, col_denumire, col_caen, col_judet]):
            continue

        # Filtrări
        if col_cui:
            if cui_exact:
                chunk = chunk[chunk[col_cui].astype(str) == cui_exact.strip()]
            else:
                if cui_min:
                    chunk = chunk[chunk[col_cui].astype(float) >= float(cui_min)]
                if cui_max:
                    chunk = chunk[chunk[col_cui].astype(float) <= float(cui_max)]

        if col_denumire and den:
            chunk = chunk[chunk[col_denumire].str.contains(den.strip(), case=False, na=False)]

        if col_caen and caen_val:
            chunk = chunk[chunk[col_caen].astype(str).str.contains(caen_val.strip(), na=False)]

        if col_judet and judet_val:
            chunk = chunk[chunk[col_judet].str.contains(judet_val.strip(), case=False, na=False)]

        if not chunk.empty:
            results.append(chunk)

    return pd.concat(results) if results else pd.DataFrame()

# === EXECUTARE
if cui_exact or cui_min or cui_max or denumire or caen or judet:
    with st.spinner("🔄 Se caută în fișier..."):
        df = search_csv_advanced(
            CSV_URL,
            cui_exact=cui_exact,
            cui_min=cui_min,
            cui_max=cui_max,
            den=denumire,
            caen_val=caen,
            judet_val=judet
        )

    if df.empty:
        st.error("❌ Nicio înregistrare găsită.")
    else:
        st.success(f"✅ Găsite {len(df)} înregistrări.")
        st.dataframe(df, use_container_width=True)

        # Export CSV
        csv_out = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descarcă rezultatele (CSV)", csv_out, "rezultate_filtrate.csv", "text/csv")

else:
    st.info("ℹ️ Introdu cel puțin un criteriu pentru a începe căutarea.")
