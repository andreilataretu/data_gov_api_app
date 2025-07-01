# 📊 Aplicație: Vizualizator Situații Financiare 2024 (data.gov.ro)

Această aplicație Streamlit permite accesarea și explorarea ușoară a fișierelor CSV publicate pe [data.gov.ro](https://data.gov.ro/dataset/situatii_financiare_2024), fără a le descărca manual sau a le încărca integral în memorie.

## ✅ Funcționalități principale

- 👁️ Previzualizare rapidă (primele 1000 de rânduri din fiecare fișier)
- 🔍 Căutare eficientă după:
  - Cod fiscal (CIF)
  - Denumire firmă (parțial)
- 📊 Agregare după Cod CAEN:
  - Număr de firme
  - Sumă cifră de afaceri
- 📁 Gestionarea fișierelor mari (citire în bucăți – `chunksize`)

---

## ▶️ Rulare locală

### 1. Clonează repo-ul:

```bash
git clone https://github.com/USERNAME/REPO-NAME.git
cd REPO-NAME
