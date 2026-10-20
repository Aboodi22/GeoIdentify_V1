"""Moteur d'identification en lame mince (version à score et pourcentage).

Principe :
  1. Chaque réponse rapporte des points à chaque minéral. Une réponse typique
     rapporte tout, une réponse acceptable mais moins courante rapporte moins,
     une réponse voisine (relief, biréfringence) rapporte un peu, une
     contradiction ne rapporte rien (et pénalise si la question est importante).
     Une seule erreur d'observation ne suffit donc plus à éliminer un minéral.
  2. Les points deviennent un pourcentage (le total fait 100 %).
  3. Les règles « décisives » (reste noir en LPA = grenat, etc.) arrêtent
     le questionnaire tout de suite.
  4. Sinon, on pose la question suivante tant qu'elle peut départager les
     candidats encore en lice, et on s'arrête dès que la confiance dépasse 90 %.
"""
import math

from thin_data import (QUESTIONS, QUESTION_BY_FIELD, MAIN_FIELDS, SPECIES, ENTRIES,
                       ENTRY_BY_KEY, UNKNOWN, EXPECT_ANY, option_label)

# --- Réglages ---------------------------------------------------------------
SHARPNESS = 0.22          # plus il est grand, plus les écarts de points donnent des % tranchés
MIN_ANSWERS = 7           # sans règle décisive, on pose au moins 7 questions (sauf si plus rien ne départage)
STOP_CONFIDENCE = 0.90    # on arrête de poser des questions au-dessus de ce niveau
CANDIDATE_FLOOR = 0.03    # sous 3 %, un minéral n'oriente plus le choix des questions
PENALTY_RATIO = 0.35      # pénalité en cas de contradiction sur une question importante
PENALTY_WEIGHT = 10       # ... c'est-à-dire de poids >= 10
DECISIVE_BONUS = 40       # points ajoutés par une règle décisive
NEUTRAL = 0.6             # question « peu importante » pour ce minéral
ADJACENT = 0.5            # réponse voisine sur une échelle (faible / moyen / fort)
OTHER_ACCEPTED = 0.75     # réponse acceptable mais moins courante
SOFT_MISS = 0.15          # forme et altération : une contradiction compte à peine

# Échelles ordonnées. « isotropic » n'en fait pas partie : noir ou non est une différence nette.
ORDINAL = {"relief": ["low", "medium", "high"], "biref": ["low", "medium", "high"]}

# Observations qui permettent de conclure immédiatement (règles demandées).
DECISIVE = [
    ({"biref": ["isotropic"]}, ["grenat"],
     "Le cristal reste noir en LPA : parmi ces minéraux, seul le grenat est isotrope."),
    ({"pleo": ["ns"]}, ["tourmaline"],
     "Pléochroïsme inverse (plus foncé quand l'allongement est N-S) : c'est la tourmaline."),
    ({"clv": ["one"], "clv_cont": ["continuous"]}, ["biotite", "muscovite"],
     "Une seule direction de clivage, en lignes continues : c'est un mica."),
]


def accepted(species, field):
    return species["profile"].get(field) or ["any"]


def _factor(species, field, value):
    """(coefficient entre 0 et 1, statut d'affichage)"""
    acc = accepted(species, field)
    soft = bool(QUESTION_BY_FIELD[field].get("soft"))
    if "any" in acc:
        return NEUTRAL, "skipped"
    if value == acc[0]:
        return 1.0, "match"
    if value in acc:
        return OTHER_ACCEPTED, "partial"
    levels = ORDINAL.get(field)
    if levels and value in levels and any(a in levels for a in acc):
        gap = min(abs(levels.index(value) - levels.index(a)) for a in acc if a in levels)
        if gap <= 1:
            return ADJACENT, "partial"
    return (SOFT_MISS if soft else 0.0), "mismatch"


def _answered(answers):
    return {f: v for f, v in answers.items() if v != UNKNOWN and f in QUESTION_BY_FIELD}


def decisive_rule(answers):
    """Première règle décisive satisfaite, ou None."""
    answered = _answered(answers)
    for conditions, targets, text in DECISIVE:
        if all(answered.get(f) in vals for f, vals in conditions.items()):
            return targets, text
    return None


def points(species, answers, decisive=None):
    """Points nets d'un minéral pour les réponses données."""
    earned = penalty = 0.0
    for field, value in _answered(answers).items():
        weight = QUESTION_BY_FIELD[field]["weight"]
        factor, status = _factor(species, field, value)
        earned += weight * factor
        if status == "mismatch" and weight >= PENALTY_WEIGHT:
            penalty += weight * PENALTY_RATIO
    bonus = DECISIVE_BONUS if decisive and species["key"] in decisive[0] else 0
    return earned - penalty + bonus


def probabilities(answers):
    """Pourcentage (0 à 1) pour chacun des minéraux, total = 100 %."""
    answered = _answered(answers)
    if not answered:
        return {s["key"]: 1 / len(SPECIES) for s in SPECIES}
    decisive = decisive_rule(answers)
    raw = {s["key"]: SHARPNESS * points(s, answers, decisive) for s in SPECIES}
    top = max(raw.values())
    exp = {k: math.exp(v - top) for k, v in raw.items()}
    total = sum(exp.values())
    return {k: v / total for k, v in exp.items()}


# ---------------------------------------------------------------------------
# Choix de la question suivante
# ---------------------------------------------------------------------------
def _applies(q, answers):
    for f, vals in q.get("requires", {}).items():
        if answers.get(f) not in vals:
            return False
    for f, vals in q.get("excludes", {}).items():
        if answers.get(f) in vals:
            return False
    return True


def _accepts(species, field, value):
    acc = accepted(species, field)
    if "any" in acc or value in acc:
        return True
    levels = ORDINAL.get(field)
    if levels and value in levels:
        return any(a in levels and abs(levels.index(value) - levels.index(a)) <= 1 for a in acc)
    return False


def _splits(q, candidates):
    """La question peut-elle encore départager les minéraux en lice ?"""
    field = q["field"]
    if q.get("soft"):
        typical = {(accepted(s, field)[0] if "any" not in accepted(s, field) else None) for s in candidates}
        return len(typical) > 1
    n = len(candidates)
    return any(0 < sum(_accepts(s, field, o["value"]) for s in candidates) < n for o in q["options"])


def _group_state(probs):
    """Un groupe (mica, feldspath) est-il très probable sans qu'on sache lequel de ses membres ?"""
    for g in ENTRIES:
        if g["kind"] != "group":
            continue
        members = g["members"]
        pg = sum(probs[m] for m in members)
        best = max(probs[m] for m in members)
        if pg >= 0.6 and (best / pg if pg else 1) < 0.75:
            return g, pg
    return None, 0.0


def next_question(answers):
    """Prochaine question, dans l'ordre LPNA puis LPA.

    On ne saute une question que si c'est nécessaire :
      - une observation décisive a identifié le minéral (grenat, mica, tourmaline) ;
      - la question ne s'applique pas (ex. angle du clivage sans clivage,
        pléochroïsme sur un minéral incolore, angle d'extinction si extinction droite).
    """
    if decisive_rule(answers):
        return None
    for q in QUESTIONS:
        if q["field"] not in answers and _applies(q, answers):
            return q
    return None


def board(answers):
    """Tableau d'élimination : un état pour chacun des 10 minéraux, dans l'ordre de la base.

    ok = compatible avec toutes les réponses, doubt = 1 contradiction, out = éliminé (2 contradictions
    ou plus, ou règle décisive qui désigne un autre minéral). Le pourcentage reste calculé par le score.
    """
    answered = _answered(answers)
    decisive = decisive_rule(answers)
    probs = probabilities(answers)
    rows = []
    for s in SPECIES:
        misses = [f for f, v in answered.items()
                  if _factor(s, f, v)[1] == "mismatch" and not QUESTION_BY_FIELD[f].get("soft")]
        if decisive and s["key"] not in decisive[0]:
            state = "out"
        else:
            state = "ok" if not misses else "doubt" if len(misses) == 1 else "out"
        rows.append({"entry": s, "state": state, "misses": len(misses),
                     "percent": round(probs[s["key"]] * 100) if answered else None})
    return rows


def progress(answers, current):
    """États des 10 segments de la barre de progression."""
    current_main = (current.get("parent") or current["field"]) if current else None
    states = []
    for field in MAIN_FIELDS:
        states.append("is-current" if field == current_main else "is-done" if field in answers else "")
    return states


# ---------------------------------------------------------------------------
# Résultat
# ---------------------------------------------------------------------------
def _checks(entry, answers):
    answered = _answered(answers)
    members = [ENTRY_BY_KEY[k] for k in entry["members"]] if entry["kind"] == "group" else [entry]
    rows = []
    for q in QUESTIONS:
        field = q["field"]
        if field not in answered:
            continue
        value = answered[field]
        accs = [accepted(m, field) for m in members]
        if any("any" in a for a in accs):
            expected, status = EXPECT_ANY, "skipped"
        else:
            union = []
            for a in accs:
                union += [v for v in a if v not in union]
            expected = " ou ".join(option_label(field, v) for v in union)
            results = [_factor(m, field, value)[1] for m in members]
            status = "match" if "match" in results else "partial" if "partial" in results else "mismatch"
        rows.append({"label": q["short"], "observed": option_label(field, value),
                     "expected": expected, "status": status})
    return rows


def _verdict(conf, margin, best_name, second_name, second_conf):
    if second_name and margin < 8 and second_conf >= 40:
        return "hesitation", f"Hésitation entre {best_name} et {second_name}"
    if conf >= 85 and margin >= 12:
        return "high", "Identification très probable"
    if conf >= 70:
        return "good", "Identification probable"
    if conf >= 50:
        return "medium", "Hypothèse plausible, à confirmer"
    return "low", "Correspondance faible : vérifiez vos observations"


def evaluate(answers):
    answered = _answered(answers)
    if not answered:
        return None
    probs = probabilities(answers)
    decisive = decisive_rule(answers)
    ranked = sorted(SPECIES, key=lambda s: -probs[s["key"]])
    group, pg = _group_state(probs)

    if group:
        entry, conf = group, round(pg * 100)
        rest = [s for s in ranked if s["key"] not in group["members"]]
        others = [{"entry": s, "confidence": round(probs[s["key"]] * 100)} for s in rest[:2]]
        second = rest[0] if rest else None
        second_conf = round(probs[second["key"]] * 100) if second else 0
    else:
        entry, conf = ranked[0], round(probs[ranked[0]["key"]] * 100)
        others = [{"entry": s, "confidence": round(probs[s["key"]] * 100)} for s in ranked[1:3]]
        second = ranked[1] if len(ranked) > 1 else None
        second_conf = others[0]["confidence"] if others else 0

    conf = min(conf, 99)
    margin = conf - second_conf
    level, verdict = _verdict(conf, margin, entry["name"], second["name"] if second else None, second_conf)
    if decisive and not group and entry["key"] in decisive[0]:
        level, verdict = "high", "Identification très probable"
    members = [ENTRY_BY_KEY[k] for k in entry["members"]] if entry["kind"] == "group" else []
    reason = None
    if decisive:
        targets = set(decisive[0])
        if (entry["kind"] == "species" and entry["key"] in targets) or \
           (entry["kind"] == "group" and targets <= set(entry["members"])):
            reason = decisive[1]
    return {
        "entry": entry, "confidence": conf, "level": level, "verdict": verdict,
        "reason": reason,
        "checks": _checks(entry, answers), "others": others, "members": members,
        "answered_count": len(answered), "total_questions": len(MAIN_FIELDS),
    }
