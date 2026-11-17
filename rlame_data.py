"""Identification d'une roche (magmatique ou métamorphique) à partir d'une lame mince.

Séquence demandée :
  Magmatique   : gisement (plutonique / filonienne / volcanique) -> texture -> minéraux
  Métamorphique: nature chimique de la roche de départ (siliceuse, silico-alumineuse,
                 ferro-magnésienne, calcique) -> roche de départ (grès, shale, calcaire,
                 grauwacke...) -> métamorphisme (régional ou de contact) -> texture -> minéraux

Un profil de roche donne, pour chaque critère, la liste des réponses acceptables
(la première = la plus typique). Pour les minéraux : abs (absent), acc (accessoire,
moins de 10 %), abd (abondant). Un minéral non listé est attendu absent ou accessoire.
Valeurs simplifiées à partir des tableaux classiques de pétrographie : à vérifier avec votre cours.
"""

UNKNOWN = "unknown"


def _o(value, label, hint=None, img=None):
    return {"value": value, "label": label, "hint": hint, "img": ("img/rlame/%s.svg" % img) if img else None}


LEVELS = [("abs", "Absent"), ("acc", "Accessoire"), ("abd", "Abondant"), ("dom", "Dominant")]
LEVEL_LABEL = dict(LEVELS)
LEVEL_ORDER = ["abs", "acc", "abd", "dom"]
LEVEL_RANK = {"abs": 0, "acc": 1, "abd": 2, "dom": 2}  # abondant et dominant comptent pour un même cran

# ---------------------------------------------------------------------------
# Questions à choix unique
# ---------------------------------------------------------------------------
QUESTIONS = {
    "family": {
        "title": "De quel type de roche s'agit-il ?",
        "help": "Cet outil identifie les roches magmatiques et les roches métamorphiques.",
        "weight": 0,
        "options": [
            _o("mag", "Roche magmatique", "Cristaux de quartz, feldspath, pyroxène... issus du refroidissement d'un magma"),
            _o("meta", "Roche métamorphique", "Roche transformée par la pression et la température (foliation, porphyroblastes...)"),
        ],
    },
    # ---------------- magmatique ----------------
    "mtex": {
        "title": "Quelle est la texture de la roche ?",
        "help": "Comparez ce que vous voyez à chaque schéma : taille et organisation des cristaux.",
        "weight": 22, "short": "Texture",
        "options": [
            _o("grenue", "Grenue ou microgrenue", "Tous les cristaux sont visibles, de taille proche, sans pâte entre eux", "grenue"),
            _o("grenue_porph", "Grenue porphyrique", "Quelques gros cristaux dans un fond de cristaux plus petits, tous visibles", "grenue_porph"),
            _o("micro_porph", "Microlitique porphyrique", "Gros cristaux (phénocristaux) dans une pâte de petites baguettes (microlites) et de verre", "micro_porph"),
            _o("ophitique", "Microgrenue ophitique", "Lattes de plagioclase enfermées dans de grands cristaux de pyroxène", "ophitique"),
            _o("intersertale", "Intersertale", "Lattes de plagioclase entrecroisées, avec du verre ou de la chlorite entre elles", "intersertale"),
            _o("perlitique", "Perlitique", "Verre craquelé en fissures arrondies, comme des perles", "perlitique"),
            _o("pyro", "Pyroclastique", "Fragments anguleux de cristaux, de verre et de ponces cimentés", "pyro"),
        ],
    },
    "setting": {
        "title": "Où la roche s'est-elle formée ?",
        "help": "La texture dépend de la vitesse de refroidissement : lent en profondeur (gros cristaux), moyen dans un filon, rapide en surface (microlites et verre). Seuls les gisements possibles pour votre texture sont proposés.",
        "weight": 14, "short": "Gisement",
        "options": [
            _o("pluto", "Plutonique", "Dans une chambre magmatique profonde", "g_pluto"),
            _o("filon", "Filonienne", "Dans une fracture (filon, dyke) à faible profondeur", "g_filon"),
            _o("volc", "Volcanique", "En surface, lors d'une éruption", "g_volc"),
        ],
    },
    "fdom": {
        "title": "Quel feldspath domine ?",
        "help": "Orthose : macle simple, souvent trouble. Plagioclase : macles en fines lamelles.",
        "weight": 14, "short": "Feldspath dominant",
        "options": [
            _o("orthose", "L'orthose", "Feldspath potassique en plus grande quantité"),
            _o("plagio", "Le plagioclase", "Feldspath à macles en lamelles en plus grande quantité"),
            _o("equal", "Les deux à peu près égaux", None),
        ],
    },
    # ---------------- métamorphique ----------------
    "ttex": {
        "title": "Quelle est la texture de la roche ?",
        "help": "Comparez ce que vous voyez à chaque schéma.",
        "weight": 20, "short": "Texture",
        "options": [
            _o("porphyroblastique", "Porphyroblastique", "De gros cristaux (grenat, staurotide, andalousite...) dans une matrice fine", "porphyroblastique"),
            _o("lepidoblastique", "Lépidoblastique", "Micas ou chlorite en lamelles alignées", "lepidoblastique"),
            _o("granoblastique", "Granoblastique", "Grains égaux en mosaïque, joints à 120°, sans orientation", "granoblastique"),
        ],
    },
    "orient": {
        "title": "Les cristaux sont-ils orientés dans une même direction ?",
        "help": "Orientés (micas, amphiboles, cristaux allongés alignés) : la roche a subi une pression, c'est un métamorphisme régional. Non orientés (mosaïque, cristaux dans tous les sens) : la roche a surtout été chauffée par un magma, c'est un métamorphisme de contact.",
        "weight": 16, "short": "Orientation des cristaux",
        "options": [
            _o("oriented", "Oui, orientés", "Indice d'un métamorphisme régional", "orient_oui"),
            _o("random", "Non, dans tous les sens", "Indice d'un métamorphisme de contact", "orient_non"),
        ],
    },
    "foliation": {
        "title": "Quel type de foliation voyez-vous ?",
        "help": "La schistosité est fine et serrée (roches peu métamorphisées). La foliation en bandes sépare des lits clairs (quartz, feldspath) et sombres (micas, amphiboles).",
        "weight": 14, "short": "Foliation",
        "options": [
            _o("schist", "Schistosité", "Plans fins et serrés de micas ou de chlorite", "foliation_schiste"),
            _o("gneiss", "Foliation en bandes", "Lits clairs et lits sombres alternés (gneissique)", "foliation_gneiss"),
        ],
    },
}

# Gisements possibles selon la texture (la texture fixe la vitesse de refroidissement)
TEXTURE_SETTINGS = {
    "grenue": ["pluto", "filon"], "grenue_porph": ["pluto", "filon"], "micro_porph": ["volc", "filon"],
    "ophitique": ["filon", "pluto"], "intersertale": ["volc", "filon"], "perlitique": ["volc"], "pyro": ["volc"],
}

# ---------------------------------------------------------------------------
# Minéraux de la case à cocher (nom, indice court)
# ---------------------------------------------------------------------------
MINERALS = {
    "quartz": ("Quartz", "Incolore, relief faible, gris-blanc en LPA"),
    "orthose": ("Orthose", "Feldspath potassique, macle simple, trouble"),
    "plagio": ("Plagioclase", "Macles en fines lamelles"),
    "biotite": ("Biotite", "Brune, pléochroïque, un clivage"),
    "muscovite": ("Muscovite", "Incolore, paillettes, couleurs vives en LPA"),
    "chlorite": ("Chlorite", "Verte, peu de pléochroïsme, gris-bleu anormal en LPA"),
    "epidote": ("Épidote", "Jaune-vert pâle, relief fort, couleurs vives"),
    "grenat": ("Grenat", "Reste noir en LPA, relief très fort"),
    "staurotide": ("Staurotide", "Jaune-brun, relief fort, macles en croix"),
    "andalousite": ("Andalousite", "Incolore ou rosée, section carrée, relief moyen"),
    "disthene": ("Disthène", "Incolore, relief fort, deux clivages, souvent bleuté"),
    "cordierite": ("Cordiérite", "Incolore, macles en secteurs, halos jaunes"),
    "hornblende": ("Hornblende / actinote", "Verte, pléochroïque, clivages à 120°"),
    "glaucophane": ("Glaucophane", "Amphibole bleue à violet, très pléochroïque"),
    "pyroxene": ("Pyroxène", "Clivages à 90°, relief fort"),
    "olivine": ("Olivine", "Très fracturée, sans clivage, couleurs vives"),
    "calcite": ("Calcite", "Relief variable, clivages en losange, gris perle en LPA"),
    "wollastonite": ("Wollastonite", "Incolore, fibres allongées, clivages à 84°"),
    "verre": ("Verre volcanique", "Reste noir en LPA, pas de cristaux"),
}

MINERALS_BY_FAMILY = {
    "mag": ["quartz", "orthose", "plagio", "biotite", "muscovite", "hornblende", "pyroxene", "olivine", "verre"],
    "meta": ["quartz", "orthose", "plagio", "biotite", "muscovite", "chlorite", "epidote", "grenat", "staurotide",
             "andalousite", "disthene", "cordierite", "hornblende", "glaucophane", "pyroxene", "calcite", "wollastonite"],
}

FAMILY_LABEL = {"mag": "Roche magmatique", "meta": "Roche métamorphique"}
DEFAULT_LEVELS = ["abs", "acc"]


def _rock(key, name, family, desc, tip, setting=None, mtex=None, chem=None, proto=None, mtype=None, ttex=None,
          fdom=None, minerals=None, key_minerals=None, lookalikes="", examples=""):
    return {"key": key, "name": name, "family": family, "description": desc, "tip": tip,
            "profile": {"setting": setting, "mtex": mtex, "chem": chem, "proto": proto, "mtype": mtype, "ttex": ttex, "fdom": fdom},
            "minerals": minerals or {}, "key_minerals": key_minerals or [],
            "lookalikes": lookalikes, "examples": examples}


G = "grenue"
GP = "grenue_porph"
MP = "micro_porph"

ROCKS = [
    # ============================ MAGMATIQUES ============================
    _rock("granite", "Granite", "mag", "Roche plutonique claire, riche en quartz, avec orthose et plagioclase, et du mica.",
          "Quartz abondant + orthose + plagioclase + biotite, texture grenue.",
          ["pluto"], [G, GP], fdom=["equal","orthose"], minerals={"quartz": ["abd"], "orthose": ["abd"], "plagio": ["abd"], "biotite": ["abd", "acc"],
          "muscovite": ["acc", "abd", "abs"], "hornblende": ["acc", "abs"]}, key_minerals=["quartz", "orthose"],
          lookalikes="Granodiorite : moins d'orthose que de plagioclase. Rhyolite : même composition, texture microlitique.",
          examples="Granites de l'Atlas, de Zaër, du Massif central"),
    _rock("granodiorite", "Granodiorite", "mag", "Roche plutonique où le plagioclase domine sur l'orthose, avec quartz, biotite et hornblende.",
          "Plagioclase dominant, un peu d'orthose, quartz, biotite et hornblende.",
          ["pluto"], [G, GP], fdom=["plagio"], minerals={"quartz": ["abd", "acc"], "orthose": ["acc", "abd"], "plagio": ["abd"], "biotite": ["abd", "acc"],
          "hornblende": ["abd", "acc"]}, key_minerals=["plagio", "quartz"],
          lookalikes="Granite (plus d'orthose) et diorite (peu de quartz).", examples="Batholites des cordillères"),
    _rock("syenite", "Syénite", "mag", "Roche plutonique à orthose dominante, avec peu ou pas de quartz.",
          "Orthose dominante, quartz absent ou rare, hornblende ou biotite.",
          ["pluto"], [G, GP], fdom=["orthose"], minerals={"quartz": ["abs", "acc"], "orthose": ["abd"], "plagio": ["acc", "abd"], "hornblende": ["abd", "acc"],
          "biotite": ["acc", "abd"], "pyroxene": ["acc", "abs"]}, key_minerals=["orthose"],
          lookalikes="Granite : il contient beaucoup de quartz.", examples="Syénites alcalines")
    ,
    _rock("diorite", "Diorite", "mag", "Roche plutonique intermédiaire : plagioclase et hornblende, peu de quartz.",
          "Plagioclase + hornblende, très peu de quartz, pas d'olivine.",
          ["pluto"], [G, GP], fdom=["plagio"], minerals={"quartz": ["acc", "abs"], "plagio": ["abd"], "hornblende": ["abd"], "biotite": ["acc", "abd"],
          "pyroxene": ["acc", "abs"], "orthose": ["abs", "acc"]}, key_minerals=["plagio", "hornblende"],
          lookalikes="Gabbro : pyroxène et olivine au lieu de hornblende.", examples="Diorites de contact des granites"),
    _rock("gabbro", "Gabbro", "mag", "Roche plutonique basique et sombre : plagioclase et pyroxène, parfois olivine.",
          "Plagioclase + pyroxène, olivine possible, pas de quartz.",
          ["pluto"], [G, GP], fdom=["plagio"], minerals={"plagio": ["abd"], "pyroxene": ["abd"], "olivine": ["acc", "abd", "abs"], "hornblende": ["acc", "abs"],
          "biotite": ["acc", "abs"]}, key_minerals=["plagio", "pyroxene"],
          lookalikes="Diorite (hornblende) ; dolérite (même minéraux mais texture ophitique en filon).", examples="Gabbros d'ophiolites"),
    _rock("peridotite", "Péridotite", "mag", "Roche ultrabasique du manteau : olivine et pyroxène, sans feldspath.",
          "Olivine + pyroxène, pas de feldspath.",
          ["pluto"], [G, GP], minerals={"olivine": ["abd"], "pyroxene": ["abd"], "plagio": ["abs", "acc"], "hornblende": ["acc", "abs"]},
          key_minerals=["olivine", "pyroxene"], lookalikes="Gabbro : il contient du plagioclase abondant.", examples="Péridotites du manteau, ophiolites"),
    _rock("microgranite", "Microgranite", "mag", "Équivalent filonien du granite : mêmes minéraux, cristaux plus petits.",
          "Quartz + orthose + plagioclase, texture microgrenue, en filon.",
          ["filon"], [G, GP, MP], fdom=["equal","orthose"], minerals={"quartz": ["abd"], "orthose": ["abd"], "plagio": ["abd", "acc"], "biotite": ["acc", "abd"],
          "muscovite": ["acc", "abs"]}, key_minerals=["quartz", "orthose"],
          lookalikes="Granite (plutonique) et rhyolite (volcanique).", examples="Filons et dykes autour des granites"),
    _rock("microdiorite", "Microdiorite", "mag", "Équivalent filonien de la diorite.",
          "Plagioclase + hornblende en cristaux fins, en filon.",
          ["filon"], [G, GP], fdom=["plagio"], minerals={"plagio": ["abd"], "hornblende": ["abd"], "quartz": ["acc", "abs"], "biotite": ["acc", "abs"]},
          key_minerals=["plagio", "hornblende"], lookalikes="Dolérite : pyroxène au lieu de hornblende.", examples="Dykes intermédiaires"),
    _rock("dolerite", "Dolérite", "mag", "Roche filonienne basique à texture ophitique : lattes de plagioclase dans de grands pyroxènes.",
          "Plagioclase + pyroxène, texture ophitique.",
          ["filon"], ["ophitique", G], fdom=["plagio"], minerals={"plagio": ["abd"], "pyroxene": ["abd"], "olivine": ["abs", "acc"], "quartz": ["abs"]},
          key_minerals=["plagio", "pyroxene"], lookalikes="Gabbro (plutonique) et basalte (microlites).", examples="Dykes de dolérite du Maroc"),
    _rock("rhyolite", "Rhyolite", "mag", "Roche volcanique acide : phénocristaux de quartz et de feldspath dans une pâte fine ou vitreuse.",
          "Quartz + feldspath alcalin, pâte microlitique ou verre.",
          ["volc"], [MP, "perlitique"], fdom=["orthose","equal"], minerals={"quartz": ["abd"], "orthose": ["abd"], "plagio": ["acc", "abd"], "biotite": ["acc", "abs"],
          "verre": ["acc", "abd", "abs"]}, key_minerals=["quartz", "orthose"],
          lookalikes="Granite : même minéraux, texture grenue.", examples="Rhyolites du Précambrien de l'Anti-Atlas"),
    _rock("trachyte", "Trachyte", "mag", "Roche volcanique à feldspath alcalin dominant, sans quartz.",
          "Orthose (sanidine) dominante, quartz absent, pâte microlitique.",
          ["volc"], [MP], fdom=["orthose"], minerals={"orthose": ["abd"], "plagio": ["acc"], "quartz": ["abs", "acc"], "hornblende": ["acc", "abs"],
          "biotite": ["acc", "abs"], "pyroxene": ["acc", "abs"], "verre": ["acc", "abs"]}, key_minerals=["orthose"],
          lookalikes="Syénite (équivalent plutonique).", examples=""),
    _rock("andesite", "Andésite", "mag", "Roche volcanique intermédiaire : phénocristaux de plagioclase, hornblende ou pyroxène.",
          "Plagioclase + hornblende ou pyroxène, pâte microlitique.",
          ["volc"], [MP], fdom=["plagio"], minerals={"plagio": ["abd"], "hornblende": ["abd", "acc"], "pyroxene": ["abd", "acc"], "biotite": ["acc", "abs"],
          "quartz": ["abs", "acc"], "verre": ["acc", "abs"]}, key_minerals=["plagio"],
          lookalikes="Basalte (olivine, plus de pyroxène) ; diorite (texture grenue).", examples="Andésites des arcs volcaniques"),
    _rock("basalte", "Basalte", "mag", "Roche volcanique basique et sombre : plagioclase, pyroxène et olivine.",
          "Plagioclase + pyroxène + olivine, microlites, parfois verre entre les lattes (intersertale).",
          ["volc"], [MP, "intersertale"], fdom=["plagio"], minerals={"plagio": ["abd"], "pyroxene": ["abd"], "olivine": ["abd", "acc"],
          "verre": ["acc", "abs"], "quartz": ["abs"]}, key_minerals=["plagio", "pyroxene"],
          lookalikes="Andésite (hornblende) ; dolérite (texture ophitique, en filon).", examples="Basaltes du Moyen Atlas, de l'Islande"),
    _rock("obsidienne", "Obsidienne / perlite", "mag", "Verre volcanique : presque aucun cristal, fissures arrondies (perlitique).",
          "Verre dominant, reste noir en LPA, fissures perlitiques.",
          ["volc"], ["perlitique"], minerals={"verre": ["abd"], "quartz": ["abs", "acc"], "orthose": ["abs", "acc"], "plagio": ["abs", "acc"]},
          key_minerals=["verre"], lookalikes="Rhyolite : elle contient des microlites et de nombreux phénocristaux.", examples=""),
    _rock("tuf", "Tuf volcanique / ignimbrite", "mag", "Roche pyroclastique : fragments de cristaux, de verre et de ponces soudés.",
          "Cristaux brisés + verre + ponces, texture pyroclastique.",
          ["volc"], ["pyro"], minerals={"verre": ["abd", "acc"], "quartz": ["acc", "abd"], "plagio": ["acc", "abd"], "orthose": ["acc"],
          "biotite": ["acc", "abs"]}, key_minerals=["verre"], lookalikes="Rhyolite : elle est une coulée, pas un dépôt de fragments.", examples="Ignimbrites"),

    # ============================ MÉTAMORPHIQUES ============================
    _rock("quartzite", "Quartzite", "meta", "Grès transformé : mosaïque de grains de quartz soudés.",
          "Quartz presque seul, texture granoblastique.",
          chem=["sil"], proto=["gres"], mtype=["regional", "contact"], ttex=["granoblastique"],
          minerals={"quartz": ["abd"], "muscovite": ["acc", "abs"], "biotite": ["acc", "abs"]}, key_minerals=["quartz"],
          lookalikes="Grès (grains avec ciment) ; marbre (calcite).", examples="Quartzites de l'Anti-Atlas"),
    _rock("phyllade", "Phyllade / ardoise", "meta", "Roche argileuse faiblement métamorphisée : schistosité nette, très fins micas et chlorite.",
          "Muscovite (séricite) + chlorite + quartz, schistosité fine.",
          chem=["silal"], proto=["shale", "grauwacke"], mtype=["regional"], ttex=["lepidoblastique"],
          minerals={"muscovite": ["abd"], "chlorite": ["abd", "acc"], "quartz": ["abd"], "biotite": ["acc", "abs"], "plagio": ["acc", "abs"]},
          key_minerals=["muscovite", "chlorite"], lookalikes="Micaschiste : plus gros micas et biotite, grenat.", examples="Ardoises, phyllades du Paléozoïque"),
    _rock("micaschiste", "Micaschiste", "meta", "Roche à gros micas nets, quartz et souvent un grenat, avec une schistosité très marquée.",
          "Muscovite + biotite + quartz, souvent grenat, staurotide ou disthène.",
          chem=["silal"], proto=["shale", "grauwacke"], mtype=["regional"], ttex=["lepidoblastique", "porphyroblastique"],
          minerals={"muscovite": ["abd"], "biotite": ["abd", "acc"], "quartz": ["abd"], "grenat": ["acc", "abd", "abs"],
          "staurotide": ["acc", "abs"], "disthene": ["acc", "abs"], "plagio": ["acc", "abs"], "chlorite": ["acc", "abs"]},
          key_minerals=["muscovite", "biotite"], lookalikes="Gneiss : il contient beaucoup de feldspath.", examples="Micaschistes à grenat des Alpes"),
    _rock("gneiss", "Gneiss", "meta", "Roche de haut degré, à feldspath, quartz et biotite, avec bandes claires et sombres.",
          "Quartz + orthose + plagioclase + biotite, bandes alternées.",
          chem=["silal"], proto=["granite", "arkose", "grauwacke", "shale"], mtype=["regional"], ttex=["granoblastique", "lepidoblastique"],
          minerals={"quartz": ["abd"], "orthose": ["abd", "acc"], "plagio": ["abd", "acc"], "biotite": ["abd", "acc"],
          "muscovite": ["acc", "abs", "abd"], "grenat": ["acc", "abs"]}, key_minerals=["quartz", "orthose", "plagio"],
          lookalikes="Micaschiste : sans feldspath abondant. Granite : sans foliation.", examples="Orthogneiss, paragneiss"),
    _rock("schiste_tachete", "Schiste tacheté", "meta", "Schiste argileux transformé au contact d'un granite : taches dues à des cristaux naissants.",
          "Muscovite + biotite + quartz, avec des taches d'andalousite ou de cordiérite.",
          chem=["silal"], proto=["shale"], mtype=["contact"], ttex=["porphyroblastique", "lepidoblastique"],
          minerals={"muscovite": ["abd", "acc"], "biotite": ["abd", "acc"], "quartz": ["abd"], "andalousite": ["acc", "abs"],
          "cordierite": ["acc", "abs"]}, key_minerals=["biotite", "quartz"], lookalikes="Cornéenne pélitique (plus dure, sans schistosité).",
          examples="Auréole de contact des granites"),
    _rock("corneenne_pelitique", "Cornéenne pélitique", "meta", "Roche dure et compacte née du contact avec un magma, à andalousite et cordiérite.",
          "Quartz + biotite + andalousite ou cordiérite, texture granoblastique.",
          chem=["silal"], proto=["shale", "grauwacke"], mtype=["contact"], ttex=["granoblastique", "porphyroblastique"],
          minerals={"quartz": ["abd"], "biotite": ["abd", "acc"], "andalousite": ["abd", "acc", "abs"], "cordierite": ["acc", "abd", "abs"],
          "muscovite": ["acc", "abs"], "plagio": ["acc", "abs"]}, key_minerals=["quartz", "biotite"],
          lookalikes="Schiste tacheté (encore schisteux).", examples="Auréoles de contact"),
    _rock("marbre", "Marbre", "meta", "Calcaire recristallisé : mosaïque de grains de calcite.",
          "Calcite presque seule, texture granoblastique, clivages en losange.",
          chem=["calc"], proto=["calcaire"], mtype=["contact", "regional"], ttex=["granoblastique"],
          minerals={"calcite": ["abd"], "quartz": ["acc", "abs"], "wollastonite": ["acc", "abs"], "pyroxene": ["acc", "abs"],
          "hornblende": ["acc", "abs"]}, key_minerals=["calcite"], lookalikes="Quartzite (quartz).", examples="Marbres de Carrare"),
    _rock("skarn", "Skarn (cornéenne calcique)", "meta", "Roche née au contact d'un magma avec un calcaire : grenat, pyroxène, épidote, wollastonite.",
          "Grenat + wollastonite + pyroxène + épidote.",
          chem=["calc"], proto=["calcaire", "marne"], mtype=["contact"], ttex=["granoblastique", "porphyroblastique"],
          minerals={"grenat": ["abd", "acc"], "wollastonite": ["abd", "acc"], "pyroxene": ["abd", "acc"], "epidote": ["abd", "acc"],
          "calcite": ["abd", "acc"], "quartz": ["acc", "abs"]}, key_minerals=["grenat", "wollastonite"],
          lookalikes="Marbre (calcite presque seule).", examples="Gisements de skarn"),
    _rock("calcschiste", "Calcschiste", "meta", "Marne métamorphisée : calcite et micas alignés.",
          "Calcite + muscovite + quartz, schistosité.",
          chem=["calc"], proto=["marne", "calcaire"], mtype=["regional"], ttex=["lepidoblastique"],
          minerals={"calcite": ["abd"], "muscovite": ["abd", "acc"], "quartz": ["abd", "acc"], "chlorite": ["acc", "abs"],
          "biotite": ["acc", "abs"]}, key_minerals=["calcite", "muscovite"], lookalikes="Marbre (sans micas abondants).", examples=""),
    _rock("schiste_vert", "Schiste vert", "meta", "Roche basique de bas degré : chlorite, épidote et actinote en feuillets verts.",
          "Chlorite + épidote + actinote + albite, schistosité.",
          chem=["ferro"], proto=["basalte", "gabbro"], mtype=["regional"], ttex=["lepidoblastique"],
          minerals={"chlorite": ["abd"], "epidote": ["abd", "acc"], "hornblende": ["abd", "acc"], "plagio": ["abd", "acc"],
          "quartz": ["acc", "abs"]}, key_minerals=["chlorite", "epidote"], lookalikes="Amphibolite (hornblende dominante, degré plus haut).", examples=""),
    _rock("amphibolite", "Amphibolite", "meta", "Roche basique de degré moyen à fort : hornblende et plagioclase.",
          "Hornblende + plagioclase, grenat possible.",
          chem=["ferro"], proto=["basalte", "gabbro"], mtype=["regional"], ttex=["granoblastique", "lepidoblastique", "porphyroblastique"],
          minerals={"hornblende": ["abd"], "plagio": ["abd"], "grenat": ["acc", "abs"], "quartz": ["acc", "abs"], "biotite": ["acc", "abs"],
          "epidote": ["acc", "abs"]}, key_minerals=["hornblende", "plagio"], lookalikes="Schiste vert, diorite.", examples=""),
    _rock("schiste_bleu", "Schiste bleu", "meta", "Roche basique de haute pression et basse température : glaucophane bleu.",
          "Glaucophane (amphibole bleue) + grenat + épidote.",
          chem=["ferro"], proto=["basalte", "gabbro"], mtype=["regional"], ttex=["lepidoblastique"],
          minerals={"glaucophane": ["abd"], "grenat": ["acc", "abs"], "epidote": ["acc", "abs"], "muscovite": ["acc", "abs"],
          "chlorite": ["acc", "abs"], "quartz": ["acc", "abs"]}, key_minerals=["glaucophane"], lookalikes="", examples="Zones de subduction"),
    _rock("eclogite", "Éclogite", "meta", "Roche basique de très haute pression : grenat et pyroxène (omphacite).",
          "Grenat + pyroxène, sans plagioclase.",
          chem=["ferro"], proto=["gabbro", "basalte"], mtype=["regional"], ttex=["granoblastique", "porphyroblastique"],
          minerals={"grenat": ["abd"], "pyroxene": ["abd"], "quartz": ["acc", "abs"], "glaucophane": ["acc", "abs"],
          "hornblende": ["acc", "abs"], "epidote": ["acc", "abs"]}, key_minerals=["grenat", "pyroxene"],
          lookalikes="Skarn (calcique, au contact).", examples="Subduction profonde"),
    _rock("corneenne_basique", "Cornéenne basique", "meta", "Roche basique transformée par la chaleur d'une intrusion.",
          "Pyroxène + plagioclase en mosaïque fine.",
          chem=["ferro"], proto=["basalte", "gabbro"], mtype=["contact"], ttex=["granoblastique"],
          minerals={"pyroxene": ["abd"], "plagio": ["abd"], "hornblende": ["acc", "abd", "abs"], "biotite": ["acc", "abs"],
          "quartz": ["acc", "abs"]}, key_minerals=["pyroxene", "plagio"], lookalikes="Amphibolite (régionale).", examples=""),
]


# Orientation des cristaux et foliation (métamorphiques) : (orient, foliation)
META_ORIENT = {
    "quartzite": (["random", "oriented"], None), "phyllade": (["oriented"], ["schist"]),
    "micaschiste": (["oriented"], ["schist"]), "gneiss": (["oriented"], ["gneiss", "schist"]),
    "schiste_tachete": (["oriented", "random"], ["schist"]), "corneenne_pelitique": (["random"], None),
    "marbre": (["random", "oriented"], None), "skarn": (["random"], None), "calcschiste": (["oriented"], ["schist"]),
    "schiste_vert": (["oriented"], ["schist"]), "amphibolite": (["oriented", "random"], ["gneiss", "schist"]),
    "schiste_bleu": (["oriented"], ["schist"]), "eclogite": (["random", "oriented"], ["gneiss"]),
    "corneenne_basique": (["random"], None),
}
for _k, (_o_, _f_) in META_ORIENT.items():
    _p = next(r for r in ROCKS if r["key"] == _k)["profile"]
    _p["orient"], _p["foliation"] = _o_, _f_

# Minéraux qui dominent nettement dans la roche (« dominant » en premier choix)
DOMINANT = {("quartzite", "quartz"): ["dom", "abd"], ("marbre", "calcite"): ["dom", "abd"], ("obsidienne", "verre"): ["dom", "abd"],
            ("peridotite", "olivine"): ["dom", "abd"], ("syenite", "orthose"): ["dom", "abd"], ("trachyte", "orthose"): ["dom", "abd"],
            ("amphibolite", "hornblende"): ["abd", "dom"], ("schiste_bleu", "glaucophane"): ["abd", "dom"]}
for (_r_, _m_), _lv in DOMINANT.items():
    next(r for r in ROCKS if r["key"] == _r_)["minerals"][_m_] = _lv

for i, r in enumerate(ROCKS, start=1):
    r["id"] = i
ROCK_BY_KEY = {r["key"]: r for r in ROCKS}
ROCK_BY_ID = {r["id"]: r for r in ROCKS}


def options_for(field, answers):
    q = QUESTIONS[field]
    if field == "setting":
        ok = TEXTURE_SETTINGS.get(answers.get("mtex"))
        return [o for o in q["options"] if not ok or o["value"] in ok]
    return q["options"]


# libellés des champs qui ne sont plus des questions (affichage des fiches)
EXTRA_LABELS = {
    "chem": {"sil": "Siliceuse", "silal": "Silico-alumineuse", "ferro": "Ferro-magnésienne", "calc": "Calcique"},
    "proto": {"gres": "Grès", "shale": "Shale (argilite)", "grauwacke": "Grauwacke", "arkose": "Arkose", "granite": "Granite",
              "basalte": "Basalte", "gabbro": "Gabbro", "calcaire": "Calcaire", "marne": "Marne"},
    "mtype": {"regional": "Régional", "contact": "De contact"},
}


def option_label(field, value, answers=None):
    if field in EXTRA_LABELS:
        return EXTRA_LABELS[field].get(value, value)
    for o in QUESTIONS[field]["options"]:
        if o["value"] == value:
            return o["label"]
    return value


def option_img(field, value):
    for o in QUESTIONS.get(field, {}).get("options", []):
        if o["value"] == value:
            return o.get("img")
    return None
