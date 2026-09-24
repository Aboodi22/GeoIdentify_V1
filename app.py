import os
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for, session
from data import MINERALS, ROCKS, QUESTION_CATALOG, expand_catalog

# Expand the reference catalog once at import time. All data remains local to Vercel.
MINERALS, ROCKS = expand_catalog(MINERALS, ROCKS)

# Fill optional observation fields with conservative defaults so every catalog
# record participates in the larger questionnaire without special cases.
for _m in MINERALS:
    _m.setdefault("surface", "rough")
    _m.setdefault("habitVisibility", "partly-defined")
    _m.setdefault("cleavageQuality", "none" if _m.get("cleavage") == "none" else "good")
    _m.setdefault("surfaceAlteration", "none")
for _r in ROCKS:
    _r.setdefault("matrix", "no" if _r.get("texture") in {"crystalline", "coarse-grained"} else "yes")
    _r.setdefault("cement", "none" if _r.get("rockType") in {"igneous", "metamorphic"} else "carbonate")
    _r.setdefault("fabric", "layered" if _r.get("layers") == "yes" else "aligned" if _r.get("foliation") == "yes" else "massive")
    _r.setdefault("weathering", "moderate")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "geoidentify-dev-secret-change-me")

UNKNOWN = "unknown"
HARDNESS_LEVELS = ["soft", "medium", "hard", "very-hard"]
PENALTY_RATIO = 0.35
DECISIVE_WEIGHT = 12

MINERAL_SPECS = [
    ("hardness", "Dureté", 20, "ordinal"),
    ("streak", "Trace", 18, "exact_streak"),
    ("acidReaction", "Réaction à l'acide", 14, "exact"),
    ("cleavage", "Clivage", 14, "exact"),
    ("magnetic", "Magnétisme", 12, "exact"),
    ("luster", "Éclat", 9, "luster"),
    ("crystalHabit", "Forme des cristaux", 8, "exact"),
    ("color", "Couleur", 5, "exact_color"),
    ("transparency", "Transparence", 6, "exact"),
    ("density", "Densité apparente", 6, "exact"),
    ("fracture", "Cassure", 6, "exact"),
    ("magneticStrength", "Intensité magnétique", 5, "exact"),
    ("surface", "Aspect de surface", 4, "exact"),
    ("habitVisibility", "Visibilité des cristaux", 4, "exact"),
    ("cleavageQuality", "Qualité du clivage", 5, "exact"),
    ("surfaceAlteration", "Altération visible", 3, "exact"),
]

ROCK_SPECS = [
    ("texture", "Texture", 22, "exact"),
    ("foliation", "Foliation", 16, "exact"),
    ("acidReaction", "Réaction à l'acide", 14, "exact"),
    ("fossils", "Fossiles", 12, "exact"),
    ("visibleMinerals", "Minéral principal", 12, "exact"),
    ("layers", "Couches", 10, "exact"),
    ("visibleCrystals", "Cristaux visibles", 8, "exact"),
    ("dominantColor", "Teinte", 6, "exact"),
    ("rockType", "Type de roche", 12, "exact"),
    ("grainSize", "Taille des grains", 8, "exact"),
    ("vesicles", "Vacuoles", 8, "exact"),
    ("sorting", "Tri des grains", 6, "exact"),
    ("rounding", "Forme des grains", 6, "exact"),
    ("matrix", "Matrice", 5, "exact"),
    ("cement", "Ciment", 5, "exact"),
    ("fabric", "Organisation", 5, "exact"),
    ("weathering", "Altération", 4, "exact"),
]

RELATED_STREAK = {"brown": {"red-brown", "yellow"}, "red-brown": {"brown"}, "yellow": {"brown"}}
RELATED_LUSTER = {"pearly": {"greasy"}, "greasy": {"pearly"}}
RELATED_COLOR = {"gray": {"black"}, "black": {"gray"}, "pink": {"red"}, "red": {"pink"}}

PURPOSES = {
    "quick": {"label": "Identification rapide", "default": 5, "max": 8,
              "priority": ["hardness", "streak", "cleavage", "magnetic", "texture", "rockType", "foliation", "visibleMinerals"]},
    "general": {"label": "Identification générale", "default": 8, "max": 12,
                 "priority": ["hardness", "streak", "luster", "color", "cleavage", "texture", "visibleMinerals", "rockType", "foliation", "acidReaction"]},
    "academic": {"label": "Étude universitaire", "default": 12, "max": 16,
                  "priority": ["hardness", "streak", "cleavage", "crystalHabit", "transparency", "density", "texture", "visibleMinerals", "rockType", "grainSize", "foliation", "fossils"]},
    "field": {"label": "Recherche / terrain", "default": 10, "max": 14,
              "priority": ["color", "texture", "visibleMinerals", "visibleCrystals", "layers", "foliation", "grainSize", "rockType", "vesicles", "hardness"]},
    "laboratory": {"label": "Recherche approfondie", "default": 15, "max": 20,
                   "priority": ["hardness", "streak", "cleavage", "magnetic", "magneticStrength", "luster", "crystalHabit", "transparency", "density", "fracture", "texture", "visibleMinerals", "rockType", "grainSize", "vesicles", "sorting", "rounding", "matrix", "cement", "surface"]},
}


def split_csv(value):
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def is_answered(value):
    return bool(value and value.strip() and value != UNKNOWN)


def exact_factor(answer, expected, related=None):
    related = related or {}
    if answer in expected:
        return 1.0 if expected.index(answer) == 0 else 0.7
    if any(value in related.get(answer, set()) for value in expected):
        return 0.5
    return 0.0


def ordinal_factor(answer, expected):
    try:
        a = HARDNESS_LEVELS.index(answer)
    except ValueError:
        return 0.0
    distances = []
    for value in expected:
        if value in HARDNESS_LEVELS:
            distances.append(abs(a - HARDNESS_LEVELS.index(value)))
    if not distances:
        return 0.0
    best = min(distances)
    return 1.0 if best == 0 else 0.4 if best == 1 else 0.0


def matcher_factor(kind, answer, expected):
    if kind == "ordinal": return ordinal_factor(answer, expected)
    if kind == "exact_streak": return exact_factor(answer, expected, RELATED_STREAK)
    if kind == "exact_color": return exact_factor(answer, expected, RELATED_COLOR)
    if kind == "luster": return exact_factor(answer, expected, RELATED_LUSTER)
    return exact_factor(answer, expected)


def labels_for(field, csv):
    return ", ".join(LABELS.get(field, {}).get(v, v) for v in split_csv(csv))


def label_for(field, value):
    return LABELS.get(field, {}).get(value, value or "")


def build_questions(kind, selected_fields=None):
    wanted = set(selected_fields or [q[0] for q in QUESTION_CATALOG[kind]])
    questions = []
    for field, title, help_text, options in QUESTION_CATALOG[kind]:
        if field not in wanted:
            continue
        prepared = []
        for value, label, hint, swatch in options:
            if swatch == "checker":
                swatch = "repeating-conic-gradient(#cfd6d2 0 25%, #f6f8f6 0 50%) 50% / 12px 12px"
            elif swatch == "rainbow":
                swatch = "conic-gradient(#c0392b, #e0b92e, #2e8b57, #2f6db5, #7b4fa1, #c0392b)"
            prepared.append({"value": value, "label": label, "hint": hint, "swatch": swatch})
        prepared.append({"value": UNKNOWN, "label": "Je ne sais pas", "hint": "Passer cette question", "swatch": None})
        questions.append({"field": field, "title": title, "help": help_text, "options": prepared,
                          "visual": any(o["swatch"] for o in prepared)})
    return questions


LABELS = {}
for q in QUESTION_CATALOG["minerals"] + QUESTION_CATALOG["rocks"]:
    LABELS.setdefault(q[0], {})
    for value, label, *_ in q[3]:
        LABELS[q[0]][value] = label


def candidate_by_id(kind, candidate_id):
    source = MINERALS if kind == "minerals" else ROCKS
    index = int(candidate_id) - 1
    return source[index] if 0 <= index < len(source) else None


def choose_questions(kind, purpose, count):
    """Select high-information observations locally, with a purpose-specific priority bias."""
    candidates = MINERALS if kind == "minerals" else ROCKS
    specs = MINERAL_SPECS if kind == "minerals" else ROCK_SPECS
    priority = PURPOSES[purpose]["priority"]
    rank = {field: i for i, field in enumerate(priority)}
    scored = []
    for field, label, weight, _ in specs:
        values = [split_csv(c.get(field, ""))[0] for c in candidates if c.get(field)]
        distinct = len(set(values))
        if not distinct:
            continue
        counts = Counter(values)
        n = len(values)
        balance = 1 - sum((v / n) ** 2 for v in counts.values())
        priority_bonus = max(0, (len(priority) - rank.get(field, len(priority))) / max(1, len(priority))) * 0.35
        score = weight * (0.6 + balance + priority_bonus)
        scored.append((score, rank.get(field, 999), field))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [field for _, _, field in scored[:max(1, min(count, len(scored)))]]


def identify(kind, answers, selected_fields):
    candidates = MINERALS if kind == "minerals" else ROCKS
    specs = [s for s in (MINERAL_SPECS if kind == "minerals" else ROCK_SPECS) if s[0] in selected_fields]
    total_weight = sum(s[2] for s in specs)
    answered_count = sum(is_answered(answers.get(s[0])) for s in specs)
    if answered_count == 0:
        return None

    scored = []
    for index, candidate in enumerate(candidates, start=1):
        checks, earned, penalty, answered_weight = [], 0.0, 0.0, 0
        for field, label, weight, matcher in specs:
            answer = answers.get(field)
            expected_csv = candidate.get(field, "")
            expected = split_csv(expected_csv)
            if not is_answered(answer):
                checks.append({"label": label, "observed": "Non renseigné", "expected": labels_for(field, expected_csv), "status": "skipped", "weight": weight})
                continue
            answered_weight += weight
            factor = matcher_factor(matcher, answer, expected)
            earned += weight * factor
            status = "match" if factor >= 0.99 else "partial" if factor > 0 else "mismatch"
            if status == "mismatch" and weight >= DECISIVE_WEIGHT:
                penalty += weight * PENALTY_RATIO
            checks.append({"label": label, "observed": label_for(field, answer), "expected": labels_for(field, expected_csv), "status": status, "weight": weight})
        ratio = max(0.0, earned - penalty) / answered_weight if answered_weight else 0
        coverage = answered_weight / total_weight if total_weight else 0
        score = ratio * (0.65 + 0.35 * coverage)
        scored.append({"candidate": candidate, "id": index, "score": score, "earned": earned,
                       "confidence": min(99, round(score * 100)), "checks": checks})

    scored.sort(key=lambda s: (-s["score"], -s["earned"], s["candidate"]["name"]))
    top = scored[:3]
    best = top[0]
    second = top[1] if len(top) > 1 else None
    margin = 100 if second is None else best["confidence"] - second["confidence"]
    if second is not None and margin < 8 and second["confidence"] >= 50:
        level, verdict = "hesitation", f"Hésitation entre {best['candidate']['name']} et {second['candidate']['name']}"
    elif best["confidence"] >= 85 and margin >= 12:
        level, verdict = "high", "Identification très probable"
    elif best["confidence"] >= 70:
        level, verdict = "good", "Identification probable"
    elif best["confidence"] >= 50:
        level, verdict = "medium", "Hypothèse plausible, à confirmer"
    else:
        level, verdict = "low", "Correspondance faible : vérifiez vos observations"

    differences = []
    if second is not None and margin < 25:
        for field, label, weight, _ in sorted(specs, key=lambda s: -s[2]):
            a, b = split_csv(best["candidate"].get(field, "")), split_csv(second["candidate"].get(field, ""))
            if not a or not b or any(v in b for v in a):
                continue
            differences.append({"label": label, "firstValue": labels_for(field, best["candidate"].get(field, "")),
                                "secondValue": labels_for(field, second["candidate"].get(field, "")),
                                "unanswered": not is_answered(answers.get(field))})
            if len(differences) == 3:
                break
    return {"results": top, "best": best, "second": second, "others": top[1:], "verdict": verdict,
            "level": level, "answeredCount": answered_count, "totalQuestions": len(specs), "differences": differences}


@app.context_processor
def inject_globals():
    return {"label_for": label_for, "labels_for": labels_for}


def render_setup(kind, error=None):
    return render_template("setup.html", kind=kind, purposes=PURPOSES, error=error,
                           count_max=max(p["max"] for p in PURPOSES.values()))


def setup_and_form(kind):
    if request.method == "GET":
        return render_setup(kind)
    purpose = request.form.get("purpose", "general")
    if purpose not in PURPOSES:
        return render_setup(kind, "Choisissez un objectif valide."), 400
    try:
        count = int(request.form.get("question_count", PURPOSES[purpose]["default"]))
    except ValueError:
        count = PURPOSES[purpose]["default"]
    count = max(3, min(count, PURPOSES[purpose]["max"]))
    fields = choose_questions(kind, purpose, count)
    session["geoidentify_setup"] = {"kind": kind, "purpose": purpose, "count": len(fields), "fields": fields}
    noun = "minéral" if kind == "minerals" else "roche"
    return render_template("identify-form.html", kind=kind,
        page_title=f"Identifier un {noun}",
        lead=f"{len(fields)} questions sélectionnées pour : {PURPOSES[purpose]['label']}. Les questions sont choisies localement pour être les plus discriminantes possibles.",
        form_action=url_for("mineral_result" if kind == "minerals" else "rock_result"),
        submit_label="Voir le résultat", questions=build_questions(kind, fields), error=None,
        purpose_label=PURPOSES[purpose]["label"])


@app.get("/")
def home():
    return render_template("index.html", mineral_count=len(MINERALS), rock_count=len(ROCKS))


@app.route("/minerals/identify", methods=["GET", "POST"])
def mineral_form():
    return setup_and_form("minerals")


@app.route("/minerals/result", methods=["GET", "POST"])
def mineral_result():
    setup = session.get("geoidentify_setup")
    if not setup or setup.get("kind") != "minerals":
        return redirect(url_for("mineral_form"))
    if request.method == "POST":
        fields = setup["fields"]
        answers = {field: request.form.get(field, UNKNOWN) for field in fields}
        outcome = identify("minerals", answers, fields)
        if outcome is None:
            return render_template("identify-form.html", kind="minerals", page_title="Identifier un minéral",
                lead=f"{setup['count']} questions sélectionnées pour : {PURPOSES[setup['purpose']]['label']}.",
                form_action=url_for("mineral_result"), submit_label="Voir le résultat",
                questions=build_questions("minerals", fields), error="Répondez à au moins une question pour lancer l'identification.",
                purpose_label=PURPOSES[setup['purpose']]['label']), 400
        session["geoidentify"] = {"kind": "minerals", "answers": answers, "fields": fields}
        return redirect(url_for("mineral_result"))
    saved = session.get("geoidentify")
    if not saved or saved.get("kind") != "minerals":
        return redirect(url_for("mineral_form"))
    return render_template("results.html", outcome=identify("minerals", saved["answers"], saved["fields"]),
                           kind="minerals", noun="minéral", restart_url=url_for("mineral_form"))


@app.get("/minerals/<int:identifier>")
def mineral_detail(identifier):
    mineral = candidate_by_id("minerals", identifier)
    if mineral is None: return render_template("error.html"), 404
    return render_template("mineral-detail.html", mineral=mineral)


@app.route("/rocks/identify", methods=["GET", "POST"])
def rock_form():
    return setup_and_form("rocks")


@app.route("/rocks/result", methods=["GET", "POST"])
def rock_result():
    setup = session.get("geoidentify_setup")
    if not setup or setup.get("kind") != "rocks":
        return redirect(url_for("rock_form"))
    if request.method == "POST":
        fields = setup["fields"]
        answers = {field: request.form.get(field, UNKNOWN) for field in fields}
        outcome = identify("rocks", answers, fields)
        if outcome is None:
            return render_template("identify-form.html", kind="rocks", page_title="Identifier une roche",
                lead=f"{setup['count']} questions sélectionnées pour : {PURPOSES[setup['purpose']]['label']}.",
                form_action=url_for("rock_result"), submit_label="Voir le résultat",
                questions=build_questions("rocks", fields), error="Répondez à au moins une question pour lancer l'identification.",
                purpose_label=PURPOSES[setup['purpose']]['label']), 400
        session["geoidentify"] = {"kind": "rocks", "answers": answers, "fields": fields}
        return redirect(url_for("rock_result"))
    saved = session.get("geoidentify")
    if not saved or saved.get("kind") != "rocks":
        return redirect(url_for("rock_form"))
    return render_template("results.html", outcome=identify("rocks", saved["answers"], saved["fields"]),
                           kind="rocks", noun="roche", restart_url=url_for("rock_form"))


@app.get("/rocks/<int:identifier>")
def rock_detail(identifier):
    rock = candidate_by_id("rocks", identifier)
    if rock is None: return render_template("error.html"), 404
    return render_template("rock-detail.html", rock=rock)


@app.errorhandler(404)
def not_found(_error): return render_template("error.html"), 404


if __name__ == "__main__": app.run(debug=True)
