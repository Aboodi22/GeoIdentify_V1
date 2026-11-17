"""Moteur « roche en lame mince » : étapes, score, pourcentage et tableau d'élimination."""
import math

from rlame_data import (QUESTIONS, MINERALS, MINERALS_BY_FAMILY, ROCKS, ROCK_BY_KEY, UNKNOWN, TEXTURE_SETTINGS,
                        LEVEL_RANK, LEVEL_LABEL, DEFAULT_LEVELS, FAMILY_LABEL, options_for, option_label)

SHARPNESS = 0.12
NEUTRAL = 0.6          # critère sans importance pour cette roche
OTHER_ACCEPTED = 0.75  # réponse acceptable mais moins typique
ADJACENT = 0.35        # minéral : un cran d'écart (accessoire au lieu d'abondant)
PENALTY = 0.35
MIN_PENALTY = 0.5

SINGLE_FIELDS = ("mtex", "setting", "fdom", "ttex", "orient", "foliation")


# ---------------------------------------------------------------- étapes
def forced_setting(answers):
    """Si la texture n'autorise qu'un seul gisement, il est déduit sans poser la question."""
    ok = TEXTURE_SETTINGS.get(answers.get("mtex"))
    return ok[0] if ok and len(ok) == 1 else None


def steps(answers):
    fam = answers.get("family")
    if fam == "mag":
        st = ["family", "mtex"]
        if not (answers.get("mtex") in TEXTURE_SETTINGS and forced_setting(answers)):
            st.append("setting")
        st.append("minerals")
        if answers.get("min_orthose", "abs") != "abs" and answers.get("min_plagio", "abs") != "abs":
            st.append("fdom")  # seulement si les deux feldspaths sont présents
        return st
    if fam == "meta":
        st = ["family", "ttex", "orient"]
        if answers.get("orient") == "oriented":
            st.append("foliation")
        st.append("minerals")
        return st
    return ["family"]


def _step_done(step, answers):
    if step == "minerals":
        return any(k.startswith("min_") for k in answers)
    return step in answers


def next_step(answers):
    """Prochaine étape : (nom) ou None quand tout est répondu."""
    for st in steps(answers):
        if not _step_done(st, answers):
            return st
    return None


def mineral_keys(answers):
    return MINERALS_BY_FAMILY.get(answers.get("family"), [])


def progress(answers, current):
    states = []
    for st in steps(answers):
        states.append("is-current" if st == current else "is-done" if _step_done(st, answers) else "")
    if answers.get("family") is None and len(states) == 1:
        states += ["", "", ""]
    return states


# ---------------------------------------------------------------- score
def _rock_pool(family):
    return [r for r in ROCKS if r["family"] == family]


def _single(rock, field, value):
    acc = rock["profile"].get(field)
    if not acc:
        return NEUTRAL, "skipped"
    if value == acc[0]:
        return 1.0, "match"
    if value in acc:
        return OTHER_ACCEPTED, "partial"
    return 0.0, "mismatch"


def _mineral_weight(rock, key):
    if key in rock["key_minerals"]:
        return 14
    return 9  # même poids pour tous les autres minéraux : lister un minéral ne doit pas donner d'avantage


def _mineral(rock, key, value):
    acc = rock["minerals"].get(key, DEFAULT_LEVELS)
    if value == acc[0]:
        return 1.0, "match"
    if value in acc:
        return OTHER_ACCEPTED, "partial"
    rank = LEVEL_RANK[value]
    if rank == 2 and any(LEVEL_RANK[a] == 2 for a in acc):  # abondant et dominant : même cran
        return 0.9, "match"
    dist = min(abs(rank - LEVEL_RANK[a]) for a in acc)
    if dist == 1:
        return ADJACENT, "partial"
    return 0.0, "mismatch"


def _facts(answers):
    singles = {f: v for f, v in answers.items() if f in SINGLE_FIELDS and v != UNKNOWN}
    forced = forced_setting(answers)
    if forced and "setting" not in singles:
        singles["setting"] = forced
    mins = {k[4:]: v for k, v in answers.items() if k.startswith("min_") and k[4:] in MINERALS}
    return singles, mins


def points(rock, answers):
    singles, mins = _facts(answers)
    total = 0.0
    for f, v in singles.items():
        w = QUESTIONS[f]["weight"]
        factor, status = _single(rock, f, v)
        total += w * factor - (w * PENALTY if status == "mismatch" else 0)
    for k, v in mins.items():
        w = _mineral_weight(rock, k)
        factor, status = _mineral(rock, k, v)
        total += w * factor - (w * MIN_PENALTY if status == "mismatch" else 0)
    return total


def misses(rock, answers):
    singles, mins = _facts(answers)
    n = sum(1 for f, v in singles.items() if _single(rock, f, v)[1] == "mismatch")
    n += sum(1 for k, v in mins.items() if _mineral(rock, k, v)[1] == "mismatch")
    return n


def probabilities(answers):
    pool = _rock_pool(answers.get("family"))
    if not pool:
        return {}
    singles, mins = _facts(answers)
    if not singles and not mins:
        return {r["key"]: 1 / len(pool) for r in pool}
    raw = {r["key"]: SHARPNESS * points(r, answers) for r in pool}
    top = max(raw.values())
    exp = {k: math.exp(v - top) for k, v in raw.items()}
    tot = sum(exp.values())
    return {k: v / tot for k, v in exp.items()}


def board(answers):
    """Une ligne par roche de la famille : ok / doubt / out et pourcentage."""
    pool = _rock_pool(answers.get("family"))
    probs = probabilities(answers)
    singles, mins = _facts(answers)
    asked = bool(singles or mins)
    rows = []
    for r in pool:
        m = misses(r, answers)
        rows.append({"entry": r, "state": "ok" if m == 0 else "doubt" if m == 1 else "out", "misses": m,
                     "percent": round(probs[r["key"]] * 100) if asked else None})
    return rows


# ---------------------------------------------------------------- résultat
def _checks(rock, answers):
    singles, mins = _facts(answers)
    rows = []
    for f in SINGLE_FIELDS:
        if f not in singles:
            continue
        acc = rock["profile"].get(f)
        factor, status = _single(rock, f, singles[f])
        rows.append({"label": QUESTIONS[f]["short"], "observed": option_label(f, singles[f]),
                     "expected": " ou ".join(option_label(f, a) for a in acc) if acc else "Peu important",
                     "status": status})
    for k in MINERALS_BY_FAMILY[rock["family"]]:
        if k not in mins:
            continue
        acc = rock["minerals"].get(k, DEFAULT_LEVELS)
        v = mins[k]
        if v == "abs" and acc[0] != "abd":
            continue
        factor, status = _mineral(rock, k, v)
        rows.append({"label": MINERALS[k][0], "observed": LEVEL_LABEL[v],
                     "expected": " ou ".join(LEVEL_LABEL[a] for a in acc), "status": status})
    return rows


def _verdict(conf, margin, best, second, second_conf):
    if second and margin < 8 and second_conf >= 40:
        return "hesitation", f"Hésitation entre {best} et {second}"
    if conf >= 85 and margin >= 12:
        return "high", "Identification très probable"
    if conf >= 70:
        return "good", "Identification probable"
    if conf >= 50:
        return "medium", "Hypothèse plausible, à confirmer"
    return "low", "Correspondance faible : vérifiez vos observations"


def evaluate(answers):
    fam = answers.get("family")
    singles, mins = _facts(answers)
    if fam not in FAMILY_LABEL or not (singles or any(v != "abs" for v in mins.values())):
        return None
    probs = probabilities(answers)
    pool = _rock_pool(fam)
    ranked = sorted(pool, key=lambda r: -probs[r["key"]])
    best, second = ranked[0], (ranked[1] if len(ranked) > 1 else None)
    conf = min(round(probs[best["key"]] * 100), 99)
    others = [{"entry": r, "confidence": round(probs[r["key"]] * 100)} for r in ranked[1:4]]
    second_conf = others[0]["confidence"] if others else 0
    level, verdict = _verdict(conf, conf - second_conf, best["name"], second["name"] if second else None, second_conf)
    prof = best["profile"]
    lab = lambda f, vals: " ou ".join(option_label(f, v) for v in vals)
    if fam == "mag":
        deduced = [("Gisement", lab("setting", prof["setting"])), ("Texture", lab("mtex", prof["mtex"]))]
    else:
        deduced = [("Roche de départ probable", ", ".join(option_label("proto", v) for v in prof["proto"])),
                   ("Nature chimique de départ", lab("chem", prof["chem"])),
                   ("Métamorphisme", lab("mtype", prof["mtype"]))]
        hint = {"oriented": "Cristaux orientés : plutôt un métamorphisme régional (pression).",
                "random": "Cristaux non orientés : plutôt un métamorphisme de contact (chaleur)."}.get(answers.get("orient"))
        if hint:
            deduced.append(("Indice de votre observation", hint))
    return {"entry": best, "deduced": deduced, "confidence": conf, "level": level, "verdict": verdict, "checks": _checks(best, answers),
            "others": others, "family_label": FAMILY_LABEL[fam],
            "answered_count": len(singles) + (1 if mins else 0), "total_questions": len(steps(answers)) - 1}
