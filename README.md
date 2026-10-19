# GeoIdentify — Vercel Edition

GeoIdentify is a local Flask web application for educational identification of minerals and rocks.

## What changed

- Keeps the original GeoIdentify visual language and wizard UI.
- Adds a research-purpose selector:
  - Identification rapide
  - Identification générale
  - Étude universitaire
  - Recherche / terrain
  - Recherche approfondie
- Lets the user choose the desired number of questions.
- Selects high-information questions locally instead of always asking the same fixed questionnaire.
- Expanded reference catalog: **83 minerals + 59 rocks** in this version.
- Adds additional observations such as transparency, density, fracture, crystal visibility, rock type, grain size, vesicles, sorting, rounding, matrix, cement and fabric.
- Keeps the identification engine local: no AI/API request is required for classification.
- Keeps the footer, email link and browser favicon.
- Uses Flask and is suitable for Vercel's Python runtime.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the local address printed by Flask.

## Deploy to Vercel

1. Put the contents of this directory in a GitHub repository.
2. Import the repository into Vercel.
3. Vercel detects `app.py` and `requirements.txt`.
4. Optional: set `SECRET_KEY` as a Vercel environment variable.

The geological reference data is stored locally in `data.py`, so no database service is required.

## Catalog note

There is no finite list called "all rocks and minerals": mineralogy contains thousands of mineral species and rocks have many names, varieties and classification systems. This release therefore provides a substantially broader curated reference catalog while keeping the data easy to extend.
