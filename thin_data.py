"""Identification en lame mince : version simplifiée (12 minéraux et groupes).

Le questionnaire suit l'ordre d'un TP : d'abord LPNA (polariseur seul), puis LPA
(analyseur inséré). Il s'arrête dès que le minéral est trouvé (voir thin_engine.py).

Chaque minéral a un « profil » : pour chaque question, la liste des réponses
possibles, la première étant la plus typique. Pas de profil pour une question
= elle ne permet pas de départager ce minéral (« peu important »).

Les valeurs sont simplifiées à partir des tables classiques de minéralogie
optique : à vérifier avec votre cours.
"""

UNKNOWN = "unknown"


def _o(value, label, hint=None, swatch=None):
    return {"value": value, "label": label, "hint": hint, "swatch": swatch}


# ---------------------------------------------------------------------------
# Questions (dans l'ordre posé). Une question avec « parent » est une
# sous-question ; « requires » / « excludes » disent quand elle est posée.
#   soft     : la réponse ne sert qu'au classement final, elle n'élimine rien
#   tiebreak : posée seulement à la fin, si plusieurs minéraux restent en lice
# ---------------------------------------------------------------------------
QUESTIONS = [
    # ------------------------------- LPNA -------------------------------
    {"field": "form", "mode": "LPNA", "short": "Forme", "weight": 4, "soft": True,
     "title": "Quelle est la forme du cristal ?",
     "help": "Regardez le contour du cristal.",
     "options": [
         _o("auto", "Automorphe", "Forme géométrique complète, contours nets"),
         _o("sub", "Subautomorphe", "Une partie des contours est nette, l'autre irrégulière"),
         _o("xeno", "Xénomorphe", "Sans forme propre : il remplit l'espace entre les autres cristaux"),
     ]},
    {"field": "fract", "mode": "LPNA", "short": "Fractures", "weight": 10,
     "title": "Y a-t-il des fractures (cassures) dans le cristal ?",
     "help": "Les fractures sont des cassures irrégulières. Ne les confondez pas avec les clivages, qui sont des lignes droites et régulières.",
     "options": [
         _o("strong", "Fort", "Très nombreuses, partout dans le cristal"),
         _o("medium", "Moyenne", "Quelques fractures"),
         _o("weak", "Faible", "Peu ou pas de fractures"),
     ]},
    {"field": "color", "mode": "LPNA", "short": "Couleur", "weight": 12,
     "title": "Quelle est la couleur du cristal en LPNA ?",
     "help": "Observez avec le polariseur seul, sans l'analyseur.",
     "options": [
         _o("colorless", "Incolore", "Transparent comme du verre", "#f4f6f4"),
         _o("gray", "Gris / trouble", "Aspect sale ou laiteux", "#b9bcc0"),
         _o("yellow", "Jaune pâle", None, "#e6d97a"),
         _o("pink", "Rose pâle", None, "#e9a9b8"),
         _o("orange", "Orange / rouge-brun", None, "#c9693a"),
         _o("brown", "Brun", None, "#a87446"),
         _o("green", "Vert", None, "#7bb27a"),
         _o("blue", "Bleu / bleu-vert", None, "#5f8fc4"),
     ]},
    {"field": "pleo", "mode": "LPNA", "short": "Pléochroïsme", "weight": 10,
     "requires": {"color": ["yellow", "pink", "orange", "brown", "green", "blue"]},
     "title": "Tournez la platine : dans quelle position le cristal est-il le plus foncé ?",
     "help": "Repérez l'allongement du cristal (ou son clivage). On suppose que le polariseur vibre E-W (gauche-droite). Si c'est N-S sur votre microscope, inversez les deux réponses.",
     "options": [
         _o("ew", "Plus foncé quand il est E-W", "Allongement ou clivage gauche-droite : pléochroïsme normal"),
         _o("ns", "Plus foncé quand il est N-S", "Allongement haut-bas : pléochroïsme inverse"),
     ]},
    {"field": "clv", "mode": "LPNA", "short": "Clivage", "weight": 14,
     "title": "Voyez-vous des clivages ?",
     "help": "Les clivages sont des traits fins, droits et parallèles dans le cristal.",
     "options": [
         _o("none", "Aucun clivage visible"),
         _o("one", "Une seule direction", "Une seule série de traits parallèles"),
         _o("two", "Deux directions", "Deux séries de traits qui se croisent"),
     ]},
    {"field": "clv_cont", "mode": "LPNA", "short": "Clivage : lignes", "weight": 8, "parent": "clv",
     "requires": {"clv": ["one"]},
     "title": "Les lignes de clivage sont-elles continues ou interrompues ?",
     "help": "Regardez si chaque ligne traverse tout le cristal.",
     "options": [
         _o("continuous", "Continues", "Lignes fines qui traversent tout le cristal"),
         _o("broken", "Interrompues", "Traits courts et irréguliers, qui s'arrêtent"),
     ]},
    {"field": "clv_ang", "mode": "LPNA", "short": "Clivage : angle", "weight": 8, "parent": "clv",
     "requires": {"clv": ["two"]},
     "title": "Quel est l'angle entre les deux directions de clivage ?",
     "help": "Estimez l'angle entre les deux séries de traits.",
     "options": [
         _o("90", "Environ 90°", "Angle droit"),
         _o("120", "Environ 120°", "Angle ouvert (56° et 124°)"),
     ]},
    {"field": "alter", "mode": "LPNA", "short": "Altération", "weight": 5, "soft": True, "tiebreak": True,
     "title": "Le cristal est-il altéré ?",
     "help": "Regardez l'aspect de la surface et des bordures.",
     "options": [
         _o("none", "Non", "Limpide, propre"),
         _o("cloudy", "Oui, trouble", "Aspect sale (argile, séricite)"),
         _o("green", "Oui, vert ou rouille", "Bordures ou veinules vertes, taches rouille"),
     ]},
    {"field": "relief", "mode": "LPNA", "short": "Relief", "weight": 14,
     "title": "Quel est le relief du cristal ?",
     "help": "Plus le contour est marqué et la surface rugueuse, plus le relief est fort.",
     "options": [
         _o("low", "Faible", "Le cristal se voit à peine"),
         _o("medium", "Moyen", "Contour visible"),
         _o("high", "Fort", "Contour très marqué, surface rugueuse"),
     ]},
    # -------------------------------- LPA --------------------------------
    {"field": "biref", "mode": "LPA", "short": "Biréfringence", "weight": 18,
     "title": "Teinte de polarisation : le cristal est-il biréfringent ?",
     "help": "Insérez l'analyseur et tournez la platine. S'il reste noir partout, il n'est pas biréfringent. Sinon, repérez la teinte la plus haute (le quartz est gris-blanc).",
     "options": [
         _o("isotropic", "Non", "Reste noir dans toutes les positions", "#111111"),
         _o("low", "Oui, faible", "Gris, blanc, jaune pâle", "linear-gradient(90deg,#555,#bbb,#f3ecc0)"),
         _o("medium", "Oui, moyenne", "Jaune, orange, rouge, bleu", "linear-gradient(90deg,#e6c84a,#e58a2f,#c8412f,#3f6fbf)"),
         _o("high", "Oui, forte", "Couleurs vives du 2e ordre", "linear-gradient(90deg,#c83a3a,#3a62c8,#3aa860)"),
     ]},
    {"field": "ext", "mode": "LPA", "short": "Extinction", "weight": 12,
     "excludes": {"biref": ["isotropic"]},
     "title": "L'extinction est-elle droite ou oblique ?",
     "help": "Tournez la platine jusqu'à ce que le cristal devienne noir, puis comparez son clivage (ou son allongement) avec le fil du réticule.",
     "options": [
         _o("straight", "Droite", "Le clivage est parallèle au fil (angle ≈ 0°)"),
         _o("oblique", "Oblique", "Le clivage fait un angle avec le fil"),
     ]},
    {"field": "ext_ang", "mode": "LPA", "short": "Angle d'extinction", "weight": 8, "parent": "ext",
     "requires": {"ext": ["oblique"]},
     "title": "L'angle d'extinction est-il supérieur ou inférieur à 27° ?",
     "help": "Mesurez l'angle entre le clivage (ou l'allongement) et le fil du réticule, quand le cristal est éteint.",
     "options": [
         _o("gt27", "Supérieur à 27°"),
         _o("lt27", "Inférieur à 27°"),
     ]},
    {"field": "twin", "mode": "LPA", "short": "Macles", "weight": 12,
     "title": "Voyez-vous des macles ?",
     "help": "Une macle coupe le cristal en zones de teintes différentes, séparées par des lignes droites (analyseur inséré).",
     "options": [
         _o("none", "Non"),
         _o("poly", "Oui, lamelles fines", "Lamelles fines et parallèles, comme un code-barres"),
         _o("simple", "Oui, deux grandes zones", "Macle simple : le cristal est coupé en deux moitiés"),
     ]},
]

QUESTION_BY_FIELD = {q["field"]: q for q in QUESTIONS}
MAIN_FIELDS = [q["field"] for q in QUESTIONS if "parent" not in q]   # les 10 questions principales
MODE_LABELS = {
    "LPNA": "LPNA : lumière polarisée non analysée (polariseur seul)",
    "LPA": "LPA : lumière polarisée analysée (analyseur inséré)",
}

# Pour afficher les réponses attendues dans les tableaux
EXPECT_ANY = "Peu important pour ce minéral"


def option_label(field, value):
    for o in QUESTION_BY_FIELD[field]["options"]:
        if o["value"] == value:
            return o["label"]
    return value


# ---------------------------------------------------------------------------
# Minéraux et groupes (ordre de la liste demandée)
# ---------------------------------------------------------------------------
INDICATRIX_TEXT = {
    "isotropic": "Sphère : un seul indice de réfraction dans toutes les directions. Le minéral reste noir en LPA.",
    "uniaxial": "Ellipsoïde de révolution autour de l'axe optique (axe c) : deux indices, nω et nε. Signe (+) : ellipsoïde allongé (nε > nω). Signe (−) : ellipsoïde aplati (nε < nω).",
    "biaxial": "Ellipsoïde à trois axes : trois indices nα < nβ < nγ et deux axes optiques séparés par l'angle 2V.",
}
OPTIC_LABELS = {"isotropic": "Isotrope", "uniaxial": "Uniaxe", "biaxial": "Biaxe"}

ENTRIES = [
    {
        "key": "quartz", "name": "Quartz", "abbr": "Qz", "kind": "species", "group": None,
        "formula": "SiO₂", "system": "Trigonal", "optic": "uniaxial", "sign": "Positif (+)",
        "description": "Minéral incolore et très propre, sans clivage. C'est le minéral le plus courant des granites, des grès et des filons.",
        "tip": "Limpide, sans clivage, sans macle, relief faible, gris-blanc en LPA, extinction droite (souvent « roulante »).",
        "lookalikes": "Feldspaths : souvent troubles, avec des macles ou des clivages peu visibles.",
        "profile": {
            "form": ["xeno", "sub", "auto"], "fract": ["weak", "medium", "strong"], "color": ["colorless", "gray"],
            "clv": ["none"], "alter": ["none"], "relief": ["low"], "biref": ["low"],
            "ext": ["straight", "oblique"], "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Souvent xénomorphe (il remplit les vides)"),
            ("Fractures", "Faibles à moyennes"),
            ("Couleur (LPNA)", "Incolore (parfois grisâtre)"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Aucun"),
            ("Altération", "Limpide, propre"),
            ("Relief", "Faible"),
            ("Biréfringence (LPA)", "Faible : gris à blanc, jaune pâle (1er ordre)"),
            ("Extinction", "Droite, souvent « roulante » (l'ombre balaie le cristal)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "feldspath", "name": "Feldspath", "abbr": "Fd", "kind": "group", "group": None,
        "members": ["orthose", "plagioclase"], "split_with": ["twin"],
        "formula": "KAlSi₃O₈ – NaAlSi₃O₈ – CaAl₂Si₂O₈", "system": "Monoclinique (orthose) ou triclinique (plagioclase)",
        "optic": "biaxial", "sign": "Négatif (−) pour l'orthose, variable pour le plagioclase",
        "description": "Famille de minéraux incolores, au relief faible, souvent troubles. On les sépare grâce aux macles : macle simple pour l'orthose, lamelles fines pour le plagioclase.",
        "tip": "Incolore, relief faible, biréfringence faible, souvent trouble, avec des macles.",
        "lookalikes": "Quartz : limpide, sans macle.",
        "refine": [("Orthose", "Macle simple : deux grandes zones"), ("Plagioclase", "Macle en lamelles fines et parallèles")],
        "fiche": [
            ("Forme", "Subautomorphe ou xénomorphe"),
            ("Couleur (LPNA)", "Incolore"),
            ("Clivage", "Peu visible : une ou deux directions à 90°, lignes interrompues"),
            ("Altération", "Souvent trouble (argile, séricite)"),
            ("Relief", "Faible"),
            ("Biréfringence (LPA)", "Faible : gris à blanc"),
            ("Macles", "Orthose : macle simple. Plagioclase : lamelles fines"),
        ],
    },
    {
        "key": "orthose", "name": "Orthose", "abbr": "Orth", "kind": "species", "group": "feldspath",
        "formula": "KAlSi₃O₈", "system": "Monoclinique", "optic": "biaxial", "sign": "Négatif (−)",
        "description": "Feldspath potassique incolore, souvent un peu trouble à cause de l'altération en argile. Fréquent dans les granites.",
        "tip": "Incolore, relief faible, biréfringence faible, macle simple (deux grandes zones), souvent trouble.",
        "lookalikes": "Plagioclase : macle en lamelles fines. Quartz : limpide, sans macle.",
        "profile": {
            "form": ["sub", "xeno", "auto"], "fract": ["weak"], "color": ["colorless", "gray"],
            "clv": ["none", "one", "two"], "clv_cont": ["broken"], "clv_ang": ["90"],
            "alter": ["cloudy", "none"], "relief": ["low"], "biref": ["low"],
            "ext": ["straight", "oblique"], "ext_ang": ["lt27"], "twin": ["simple", "none"],
        },
        "fiche": [
            ("Forme", "Subautomorphe ou xénomorphe"),
            ("Fractures", "Faibles"),
            ("Couleur (LPNA)", "Incolore"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Peu visible : une direction, ou deux à 90°, lignes interrompues"),
            ("Altération", "Souvent trouble (argile)"),
            ("Relief", "Faible"),
            ("Biréfringence (LPA)", "Faible : gris à blanc"),
            ("Extinction", "Presque droite (angle faible, inférieur à 27°)"),
            ("Macles", "Macle simple : deux grandes zones (macle de Carlsbad)"),
        ],
    },
    {
        "key": "plagioclase", "name": "Plagioclase", "abbr": "Pl", "kind": "species", "group": "feldspath",
        "formula": "NaAlSi₃O₈ – CaAl₂Si₂O₈", "system": "Triclinique", "optic": "biaxial",
        "sign": "Variable (selon la composition)",
        "description": "Feldspath sodi-calcique incolore. Très facile à reconnaître grâce à ses macles en lamelles fines.",
        "tip": "Macle en lamelles fines noires et blanches (aspect code-barres), relief faible, extinction oblique d'angle faible.",
        "lookalikes": "Orthose : macle simple. Quartz : sans macle.",
        "profile": {
            "form": ["sub", "auto", "xeno"], "fract": ["weak"], "color": ["colorless", "gray"],
            "clv": ["none", "one", "two"], "clv_cont": ["broken"], "clv_ang": ["90"],
            "alter": ["cloudy", "none"], "relief": ["low"], "biref": ["low"],
            "ext": ["oblique", "straight"], "ext_ang": ["lt27", "gt27"], "twin": ["poly", "none"],
        },
        "fiche": [
            ("Forme", "Subautomorphe (rectangles allongés)"),
            ("Fractures", "Faibles"),
            ("Couleur (LPNA)", "Incolore"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Peu visible : une direction, ou deux à 90°, lignes interrompues"),
            ("Altération", "Souvent trouble (séricite)"),
            ("Relief", "Faible"),
            ("Biréfringence (LPA)", "Faible : gris à blanc"),
            ("Extinction", "Oblique, angle faible (surtout inférieur à 27°)"),
            ("Macles", "Lamelles fines et parallèles (polysynthétiques)"),
        ],
    },
    {
        "key": "mica", "name": "Mica", "abbr": "Mica", "kind": "group", "group": None,
        "members": ["biotite", "muscovite"], "split_with": [],
        "formula": "Famille : biotite, muscovite…", "system": "Monoclinique", "optic": "biaxial", "sign": "Négatif (−)",
        "description": "Famille de minéraux en paillettes, avec un clivage parfait dans une seule direction : des lignes fines et continues.",
        "tip": "Une seule série de clivages continus, biréfringence forte, extinction droite en « œil d'oiseau ».",
        "lookalikes": "Hornblende : deux clivages. Quartz : aucun clivage.",
        "refine": [("Biotite", "Brune, pléochroïsme fort"), ("Muscovite", "Incolore, sans pléochroïsme")],
        "fiche": [
            ("Forme", "Paillettes allongées"),
            ("Clivage", "Une direction, lignes continues"),
            ("Relief", "Moyen"),
            ("Biréfringence (LPA)", "Forte : couleurs vives du 2e ordre"),
            ("Extinction", "Droite (aspect « œil d'oiseau »)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "biotite", "name": "Biotite", "abbr": "Bi", "kind": "species", "group": "mica",
        "formula": "K(Mg,Fe)₃AlSi₃O₁₀(OH)₂", "system": "Monoclinique", "optic": "biaxial", "sign": "Négatif (−)",
        "description": "Mica noir à brun : paillettes brunes, très pléochroïques, avec une seule direction de clivage.",
        "tip": "Brune, clivage continu dans une direction, pléochroïsme fort (plus foncée quand le clivage est parallèle au polariseur), extinction droite en œil d'oiseau.",
        "lookalikes": "Hornblende : deux clivages. Tourmaline : pléochroïsme inverse et pas de clivage.",
        "profile": {
            "form": ["sub", "auto", "xeno"], "fract": ["weak"], "color": ["brown", "orange", "green", "yellow"], "pleo": ["ew"],
            "clv": ["one"], "clv_cont": ["continuous"], "alter": ["none", "green"],
            "relief": ["medium"], "biref": ["high"], "ext": ["straight"], "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Paillettes allongées"),
            ("Fractures", "Faibles"),
            ("Couleur (LPNA)", "Brune, rouge-brun, verte ou jaune"),
            ("Pléochroïsme", "Fort et normal : plus foncée quand le clivage est E-W (polariseur E-W)"),
            ("Clivage", "Une direction, lignes continues"),
            ("Altération", "Peut passer en chlorite (bordures vertes)"),
            ("Relief", "Moyen"),
            ("Biréfringence (LPA)", "Forte (masquée par la couleur brune)"),
            ("Extinction", "Droite (aspect « œil d'oiseau »)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "muscovite", "name": "Muscovite", "abbr": "Ms", "kind": "species", "group": "mica",
        "formula": "KAl₂(AlSi₃O₁₀)(OH)₂", "system": "Monoclinique", "optic": "biaxial", "sign": "Négatif (−)",
        "description": "Mica blanc : paillettes incolores avec une seule direction de clivage parfait.",
        "tip": "Incolore, une série de clivages continus, biréfringence forte (couleurs vives), extinction droite en œil d'oiseau.",
        "lookalikes": "Biotite : brune et pléochroïque. Quartz : sans clivage.",
        "profile": {
            "form": ["sub", "auto", "xeno"], "fract": ["weak"], "color": ["colorless"],
            "clv": ["one"], "clv_cont": ["continuous"], "alter": ["none"],
            "relief": ["medium", "low"], "biref": ["high"], "ext": ["straight"], "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Paillettes allongées"),
            ("Fractures", "Faibles"),
            ("Couleur (LPNA)", "Incolore"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Une direction, lignes continues"),
            ("Altération", "Limpide"),
            ("Relief", "Moyen (faible à moyen)"),
            ("Biréfringence (LPA)", "Forte : couleurs vives du 2e ordre"),
            ("Extinction", "Droite (aspect « œil d'oiseau »)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "grenat", "name": "Grenat", "abbr": "Grt", "kind": "species", "group": None,
        "formula": "(Fe,Mg,Ca,Mn)₃Al₂(SiO₄)₃", "system": "Cubique", "optic": "isotropic", "sign": "Sans objet (isotrope)",
        "description": "Minéral rond ou à contours géométriques, au relief très fort, qui reste toujours noir en LPA.",
        "tip": "Reste noir en LPA (isotrope), relief très fort, nombreuses fractures, aucun clivage, incolore ou rose très pâle.",
        "lookalikes": "Olivine : elle devient colorée en LPA et ne reste jamais noire.",
        "profile": {
            "form": ["auto", "sub", "xeno"], "fract": ["strong", "medium"], "color": ["colorless", "pink"],
            "clv": ["none"], "alter": ["none", "green"], "relief": ["high"], "biref": ["isotropic", "low"],
            "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Automorphe ou subautomorphe (arrondi)"),
            ("Fractures", "Fortes : nombreuses fractures irrégulières"),
            ("Couleur (LPNA)", "Incolore ou rose pâle"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Aucun"),
            ("Altération", "Frais, ou bordures de chlorite"),
            ("Relief", "Très fort"),
            ("Biréfringence (LPA)", "Aucune : reste noir (isotrope)"),
            ("Extinction", "Sans objet (reste noir)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "tourmaline", "name": "Tourmaline", "abbr": "Tur", "kind": "species", "group": None,
        "formula": "Na(Mg,Fe,Li,Al)₃Al₆(BO₃)₃Si₆O₁₈(OH)₄", "system": "Trigonal", "optic": "uniaxial", "sign": "Négatif (−)",
        "description": "Prismes bruns ou verts, sans clivage. Son pléochroïsme est « inverse » : c'est son meilleur critère.",
        "tip": "Brune ou verte, sans clivage, plus foncée quand l'allongement est perpendiculaire au polariseur (N-S si le polariseur est E-W) : pléochroïsme inverse.",
        "lookalikes": "Biotite : clivage et pléochroïsme normal. Hornblende : clivages à 120°.",
        "profile": {
            "form": ["auto", "sub", "xeno"], "fract": ["weak", "medium"], "color": ["brown", "green", "blue", "yellow", "pink", "colorless"], "pleo": ["ns"],
            "clv": ["none"], "alter": ["none"], "relief": ["high", "medium"], "biref": ["medium", "high"],
            "ext": ["straight"], "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Automorphe : prismes allongés, sections triangulaires arrondies"),
            ("Fractures", "Faibles à moyennes (cassures transversales)"),
            ("Couleur (LPNA)", "Brune, verte, bleue, jaune, rose ou incolore"),
            ("Pléochroïsme", "Fort et inverse : plus foncée quand l'allongement est N-S (polariseur E-W)"),
            ("Clivage", "Aucun"),
            ("Altération", "Frais"),
            ("Relief", "Moyen à fort"),
            ("Biréfringence (LPA)", "Moyenne"),
            ("Extinction", "Droite (parallèle à l'allongement)"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "olivine", "name": "Olivine", "abbr": "Ol", "kind": "species", "group": None,
        "formula": "(Mg,Fe)₂SiO₄", "system": "Orthorhombique", "optic": "biaxial", "sign": "Variable (selon Mg et Fe)",
        "description": "Minéral incolore, très fracturé, sans clivage. Typique des roches sombres : basalte, gabbro, péridotite.",
        "tip": "Incolore, fractures très nombreuses, sans clivage, relief fort, couleurs vives en LPA, extinction droite, souvent altérée en serpentine (veinules vertes).",
        "lookalikes": "Grenat : il reste noir en LPA. Pyroxène : il a des clivages.",
        "profile": {
            "form": ["sub", "xeno", "auto"], "fract": ["strong", "medium"], "color": ["colorless", "yellow"],
            "clv": ["none"], "alter": ["green", "none"], "relief": ["high"], "biref": ["high"],
            "ext": ["straight"], "twin": ["none"],
        },
        "fiche": [
            ("Forme", "Subautomorphe ou xénomorphe (grains arrondis)"),
            ("Fractures", "Fortes : réseau de fractures irrégulières"),
            ("Couleur (LPNA)", "Incolore ou jaune très pâle"),
            ("Pléochroïsme", "Aucun"),
            ("Clivage", "Aucun"),
            ("Altération", "Souvent en serpentine (veinules vertes) ou en rouille"),
            ("Relief", "Fort"),
            ("Biréfringence (LPA)", "Forte : couleurs vives du 2e ordre"),
            ("Extinction", "Droite"),
            ("Macles", "Aucune"),
        ],
    },
    {
        "key": "pyroxene", "name": "Pyroxène", "abbr": "Pyr", "kind": "species", "group": None,
        "formula": "(Ca,Mg,Fe)₂Si₂O₆", "system": "Monoclinique (augite) ou orthorhombique (enstatite)",
        "optic": "biaxial", "sign": "Positif (+) pour l'augite",
        "description": "Minéral incolore à vert ou brun très pâle, avec deux clivages presque à angle droit (90°) et un fort relief.",
        "tip": "Deux clivages à environ 90° (sections carrées ou octogonales), relief fort, extinction oblique avec un angle supérieur à 27° (clinopyroxène).",
        "lookalikes": "Hornblende : clivages à 120°, vert plus foncé, angle d'extinction inférieur à 27°.",
        "profile": {
            "form": ["sub", "xeno", "auto"], "fract": ["medium", "weak"], "color": ["colorless", "green", "brown", "pink", "yellow"],
            "clv": ["two", "one"], "clv_cont": ["broken"], "clv_ang": ["90"], "alter": ["none", "green"],
            "relief": ["high"], "biref": ["medium", "high"], "ext": ["oblique", "straight"], "ext_ang": ["gt27"],
        },
        "fiche": [
            ("Forme", "Subautomorphe ou xénomorphe (prismes courts)"),
            ("Fractures", "Moyennes (cassures transversales)"),
            ("Couleur (LPNA)", "Incolore, vert, brun, rose ou jaune très pâle"),
            ("Pléochroïsme", "Aucun ou très faible"),
            ("Clivage", "Deux directions à environ 90°"),
            ("Altération", "Frais, ou chlorite sur les bords"),
            ("Relief", "Fort"),
            ("Biréfringence (LPA)", "Moyenne à forte"),
            ("Extinction", "Oblique, angle supérieur à 27° (augite : 35 à 45°)"),
            ("Macles", "Possibles (macle simple)"),
        ],
    },
    {
        "key": "hornblende", "name": "Hornblende verte", "abbr": "Hb v", "kind": "species", "group": None,
        "formula": "Ca₂(Mg,Fe,Al)₅(Si,Al)₈O₂₂(OH)₂", "system": "Monoclinique", "optic": "biaxial", "sign": "Négatif (−)",
        "description": "Amphibole verte : cristaux allongés avec deux clivages qui se croisent à environ 120° (56° et 124°) et un pléochroïsme net.",
        "tip": "Verte, pléochroïsme normal (plus foncée quand l'allongement est E-W avec un polariseur E-W), deux clivages à environ 120°, extinction oblique avec un angle inférieur à 27°.",
        "lookalikes": "Pyroxène : clivages à 90° et angle d'extinction supérieur à 27°. Biotite : un seul clivage.",
        "profile": {
            "form": ["sub", "auto", "xeno"], "fract": ["weak", "medium"], "color": ["green", "brown", "blue", "yellow"], "pleo": ["ew"],
            "clv": ["two", "one"], "clv_cont": ["broken"], "clv_ang": ["120"], "alter": ["none", "green"],
            "relief": ["medium", "high"], "biref": ["medium"], "ext": ["oblique"], "ext_ang": ["lt27"],
        },
        "fiche": [
            ("Forme", "Subautomorphe (prismes allongés, sections en losange)"),
            ("Fractures", "Faibles à moyennes"),
            ("Couleur (LPNA)", "Verte, brune, bleu-vert ou jaune-vert"),
            ("Pléochroïsme", "Net et normal : plus foncée quand l'allongement est E-W (polariseur E-W)"),
            ("Clivage", "Deux directions à environ 120°"),
            ("Altération", "Peut passer en chlorite"),
            ("Relief", "Moyen à fort"),
            ("Biréfringence (LPA)", "Moyenne (masquée par la couleur verte)"),
            ("Extinction", "Oblique, angle inférieur à 27° (environ 12 à 25°)"),
            ("Macles", "Possibles (macle simple)"),
        ],
    },
]

for _i, _e in enumerate(ENTRIES, start=1):
    _e["id"] = _i

ENTRY_BY_KEY = {e["key"]: e for e in ENTRIES}
SPECIES = [e for e in ENTRIES if e["kind"] == "species"]
