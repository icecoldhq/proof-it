# m8_ch7_recursive_types.py — Proof It Structural Induction Validator (M8)
# Validates structural induction proofs for recursive data types.
# Checks base cases, structural IH, and constructor cases.

import re


def parse_input(raw_text: str) -> list[dict]:
    """Split raw text into numbered steps."""
    steps = []
    for line in raw_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(".", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            num = int(parts[0].strip())
            text = parts[1].strip()
        else:
            num = len(steps) + 1
            text = line
        steps.append({"number": num, "text": text})
    return steps


def _classify_step(text: str) -> str:
    """
    Classify a step into a structural-induction component.
    Returns: BASE_CASE, STRUCTURAL_IH, CONSTRUCTOR_CASE,
             RECURSIVE_DEF, CONCLUSION, OTHER
    """
    t = text.lower()

    # --- Explicit structural labels ---
    if re.search(r'\bstructural\s+induction\s+hypothesis\b', t):
        return "STRUCTURAL_IH"
    if re.search(r'\bbase\s+(case|cases|step|basis)\b', t):
        return "BASE_CASE"
    if re.search(r'\bconstructor\s+(case|step)\b', t):
        return "CONSTRUCTOR_CASE"
    if re.search(r'\binductive\s+step\b', t):
        return "CONSTRUCTOR_CASE"
    if re.search(r'\bconclusion\b', t):
        return "CONCLUSION"

    # --- Structural IH by content ---
    # Assumes property holds for subcomponents / proper subtrees / branches / children
    structural_ih_patterns = [
        r'\bassume\b.*\b(property|predicate|p)\b.*\b(holds?|is\s+true)\b.*\b(subtree|subtrees|branch|branches|component|components|child|children|proper\s+sub|substructure)\b',
        r'\bassume\b.*\b(subtree|subtrees|branch|branches|component|components|child|children|proper\s+sub|substructure)\b.*\b(holds?|is\s+true|satisfy)\b',
        r'\bassume\b.*\b(left|right)\b.*\b(subtree|branch)\b.*\b(holds?|is\s+true)\b',
        r'\bstructural\s+ih\b',
        r'\bsih\b',
        r'\bby\s+structural\s+induction\s+hypothesis\b',
        r'\bassume\b.*\bfor\s+all\s+proper\b',
    ]
    for pat in structural_ih_patterns:
        if re.search(pat, t):
            return "STRUCTURAL_IH"

    # --- Constructor case by content ---
    constructor_patterns = [
        r'\bprove\b.*\b(constructor|constructed|composite|non-leaf|branching)\b',
        r'\bprove\b.*\bfor\s+the\s+(case|step)\b.*\b(constructor|constructed)\b',
        r'\bshow\b.*\b(constructor|constructed|composite|non-leaf|branching)\b',
        r'\bprove\b.*\b[a-z]\s*\(\s*t\s*\).*(\bwhere\b|\bconstructed\b|\bfrom\b)',
    ]
    for pat in constructor_patterns:
        if re.search(pat, t):
            return "CONSTRUCTOR_CASE"

    # --- Base case by content ---
    base_patterns = [
        r'\b(t|it|this)\b.*\b(is\s+a)?\s*(leaf|leaves|empty|string|nil|null|base\s+element)\b',
        r'\bempty\s+(string|list|tree|set)\b',
        r'\bbase\s+element\b',
        r'\b(t|it)\b.*\bhas\s+no\s+(subtree|branch|component|children)\b',
        r'\b(t|it)\b.*\bis\s+atomic\b',
    ]
    for pat in base_patterns:
        if re.search(pat, t):
            return "BASE_CASE"

    # --- Recursive definition (informational, not required) ---
    if re.search(r'\brecursive\s+(definition|data\s+type)\b', t):
        return "RECURSIVE_DEF"
    if re.search(r'\bbase\s+case\s*:\s*\(.*\)\b', t) and 'proof' not in t:
        return "RECURSIVE_DEF"
    if re.search(r'\bconstructor\s+case\s*:\s*\(.*\)\b', t) and 'proof' not in t:
        return "RECURSIVE_DEF"

    # --- Conclusion by content ---
    conclusion_patterns = [
        r'\btherefore\b.*\b(all|every|for\s+all|∀|any)\b.*\b(recursive|tree|structur)\b',
        r'\bthus\b.*\b(all|every|for\s+all|∀)\b',
        r'\bby\s+structural\s+induction\b',
        r'\bby\s+the\s+principle\s+of\s+structural\s+induction\b',
        r'\bqed\b',
        r'∎',
        r'\bproven\b.*\bfor\s+all\b',
    ]
    for pat in conclusion_patterns:
        if re.search(pat, t):
            return "CONCLUSION"

    return "OTHER"


def validate(steps: list[dict]) -> dict:
    """
    Validate structural induction proof structure.

    Returns:
        {
            "valid": bool,
            "step_results": [{"number": int, "ok": bool, "reason": str}, ...],
            "overall_reason": str,
            "technique": "structural_induction" | "unknown"
        }
    """
    if not steps:
        return {
            "valid": False,
            "step_results": [],
            "overall_reason": "No proof steps provided.",
            "technique": "unknown"
        }

    # 1. Classify every step
    classifications = [_classify_step(s["text"]) for s in steps]
    full_text = " ".join([s["text"].lower() for s in steps])

    # 2. Detect technique
    has_structural_keyword = bool(re.search(r'\bstructural\s+induction\b', full_text))
    has_structural_ih = "STRUCTURAL_IH" in classifications

    if has_structural_keyword or has_structural_ih:
        detected_type = "structural_induction"
    else:
        detected_type = "unknown"

    # 3. Locate first occurrence of each component
    def first_index(targets: list[str]) -> int:
        for i, c in enumerate(classifications):
            if c in targets:
                return i
        return -1

    base_idx = first_index(["BASE_CASE"])
    sih_idx = first_index(["STRUCTURAL_IH"])
    constructor_idx = first_index(["CONSTRUCTOR_CASE"])
    conclusion_idx = first_index(["CONCLUSION"])

    has_base = base_idx != -1
    has_sih = sih_idx != -1
    has_constructor = constructor_idx != -1
    has_conclusion = conclusion_idx != -1

    # 4. Per-step validation
    step_results = []
    all_ok = True

    for i, step in enumerate(steps):
        ok = True
        reason = "OK"
        cls = classifications[i]

        # Ordering checks
        if cls == "BASE_CASE" and sih_idx != -1 and i > sih_idx:
            ok = False
            reason = "Base case should appear before structural inductive hypothesis"
            all_ok = False
        elif cls == "STRUCTURAL_IH" and constructor_idx != -1 and i > constructor_idx:
            ok = False
            reason = "Structural IH should appear before constructor case"
            all_ok = False
        elif cls == "CONSTRUCTOR_CASE" and conclusion_idx != -1 and i > conclusion_idx:
            ok = False
            reason = "Constructor case should appear before conclusion"
            all_ok = False

        step_results.append({
            "number": step["number"],
            "ok": ok,
            "reason": reason
        })

    # 5. Global structural checks
    missing = []
    if not has_base:
        missing.append("base case")
    if not has_sih:
        missing.append("structural inductive hypothesis")
    if not has_constructor:
        missing.append("constructor case")
    if not has_conclusion:
        missing.append("conclusion")

    if missing:
        overall_reason = "Missing required structural induction components: " + ", ".join(missing) + "."
        all_ok = False
    else:
        overall_reason = "Structural induction structure complete."
        if detected_type == "structural_induction":
            overall_reason += " Structural induction pattern detected."

    # 6. Distinguish from ordinary induction
    has_ordinary_ih = bool(re.search(r'\bassume\b.*\b[a-z]\s*\(\s*n\s*\)', full_text))
    if detected_type == "structural_induction" and has_ordinary_ih and not has_structural_ih:
        overall_reason = (
            "Type mismatch: proof mentions structural induction, "
            "but the hypothesis assumes P(n) (ordinary induction style). "
            "Structural induction requires assuming P holds for all proper subcomponents/subtrees."
        )
        all_ok = False

    # 7. Extra ordering sanity checks
    if has_base and has_sih and base_idx > sih_idx:
        overall_reason += " Note: base case appears after structural IH."
        all_ok = False
    if has_sih and has_constructor and sih_idx > constructor_idx:
        overall_reason += " Note: structural IH appears after constructor case."
        all_ok = False
    if has_constructor and has_conclusion and constructor_idx > conclusion_idx:
        overall_reason += " Note: constructor case appears after conclusion."
        all_ok = False

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": overall_reason,
        "technique": detected_type
    }
