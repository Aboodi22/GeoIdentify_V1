# GeoIdentify

Application web éducative (Flask, déployable sur Vercel) pour identifier des **minéraux**, des **roches** et des **lames minces** à partir d'observations simples. Tout le calcul est local : aucune IA ni API externe.

## Les 4 modes

| Mode | Page | Contenu |
|---|---|---|
| Un minéral | `/identify` | 143 minéraux, avec leurs variétés (ex. gypse) |
| Une roche | `/identify` | 90 roches |
| Une lame mince (minéral) | `/thin/identify` | 12 minéraux ou groupes : questions LPNA puis LPA, résultat en % |
| Une roche en lame mince | `/rlame/identify` | 29 roches magmatiques et métamorphiques, avec schémas |

Une barre de recherche (haut de page) tolère les fautes d'orthographe et propose des suggestions.

## Comment ça marche

- **Minéraux et roches** : « Étude universitaire », avec le choix du nombre de questions.
- **Minéral en lame mince** : toutes les questions sont posées (LPNA puis LPA), sauf si une observation décisive identifie le minéral (reste noir en LPA = grenat ; pléochroïsme N-S = tourmaline ; un seul clivage en lignes continues = mica). Un tableau montre les minéraux possibles, douteux ou écartés à chaque réponse.
- **Roche magmatique en lame mince** : texture (schémas) → gisement (limité aux gisements compatibles avec la texture) → minéraux (Absent / Accessoire / Abondant / Dominant) → feldspath dominant si besoin.
- **Roche métamorphique en lame mince** : texture (schémas) → cristaux orientés ? (oui = régional, non = contact) → foliation → minéraux. La roche de départ probable et le type de métamorphisme sont donnés dans le résultat.
- **Résultat** : pourcentage de confiance, tableau « concorde / ne correspond pas », autres candidats, fiche détaillée.

## Lancer en local

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate        Linux/macOS : source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Ouvrir l'adresse affichée par Flask (en général http://127.0.0.1:5000).

## Déployer sur Vercel

1. Mettre le contenu de ce dossier dans le dépôt GitHub.
2. Importer le dépôt dans Vercel (il détecte `app.py` et `requirements.txt`).
3. Optionnel : variable d'environnement `SECRET_KEY`.

Pour mettre à jour un dépôt existant, ne poussez que les fichiers modifiés (`git status`, `git add <fichiers>`, `git commit`, `git push`).

## Structure

| Fichier ou dossier | Rôle |
|---|---|
| `app.py` | Routes Flask (accueil, recherche, 4 modes) |
| `data.py` | Base des minéraux et des roches |
| `thin_data.py`, `thin_engine.py` | Base et moteur « minéral en lame mince » |
| `rlame_data.py`, `rlame_engine.py` | Base et moteur « roche en lame mince » |
| `templates/` | Pages HTML (Jinja2) ; `rlame-*` et `thin-*` pour les lames minces |
| `static/css/style.css` | Thème noir, bleu et blanc |
| `static/favicon.svg` | Icône de l'onglet (logo coloré) |
| `static/img/rlame/` | 17 schémas (textures, orientation, gisements) |
| `tools/make_drawings.py` | Régénère les schémas (numpy et scipy requis, facultatif) |
| `docs/` | Listes des minéraux et des roches en lame mince, et fichiers du logo |

## Moteur de score (lames minces)

Chaque réponse donne des points à chaque candidat : réponse typique = tous les points, réponse acceptable moins courante = 75 %, réponse voisine = un peu, contradiction = 0 (et une pénalité si le critère est important). Une seule erreur d'observation n'élimine donc pas le bon résultat. Les points deviennent un pourcentage (total 100 %).

## Limites

- Estimation éducative : une identification certaine peut demander une analyse en laboratoire.
- Les valeurs des lames minces sont simplifiées : à vérifier avec votre cours.
- Quartz et feldspath non maclé se ressemblent en lame mince : le résultat reste honnêtement incertain.

Sécurité : ne goûtez pas les échantillons, n'inhalez pas les poussières et faites réaliser les tests chimiques par un professionnel.

© Abderrazak Bounsif
