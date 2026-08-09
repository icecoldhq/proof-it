# m9_ch8_infinite_sets.py — Proof It Infinite Sets Validator (M9)
# Validates structural correctness of diagonalization, countability,
# and cardinality arguments. Stress-tests the engine.

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
    Classify a step into an infinite-sets proof component.
    Structural roles (conclusion, contradiction) are checked BEFORE
    content claims (countable/uncountable) so that a conclusion step
    like 'Therefore the reals are uncountable' is classified as CONCLUSION.
    """
    t = text.lower()

    # --- Assumption of surjection / enumeration / bijection ---
    surjection_patterns = [
        r'\bassume\b.*\b(bijection|surjection|surjective|enumeration|enumerate|enumerating|list|counting|count)\b',
        r'\bassume\b.*\b(f|g|h)\b.*\b(is\s+a)?\s*(bijection|surjection|enumeration)\b',
        r'\bfor\s+the\s+sake\s+of\s+contradiction\b.*\b(bijection|surjection|enumeration|enumerate|list)\b',
        r'\bsuppose\b.*\b(bijection|surjection|surjective|enumeration|enumerate|list)\b',
        r'\bassume\b.*\bcan\s+be\s+(listed|enumerated|counted)\b',
        r'\bassume\b.*\bthere\s+is\s+a\b.*\b(bijection|surjection|enumeration)\b',
    ]
    for pat in surjection_patterns:
        if re.search(pat, t):
            return "ASSUMPTION_SURJECTION"

    # --- Construction of missing element (diagonalization core) ---
    construction_patterns = [
        r'\bconstruct\b.*\b(element|set|string|number|diagonal|digit|digits|sequence)\b',
        r'\bconstruct\b.*\b(d|s|x)\b',
        r'\bdefine\b.*\b(d|s|x)\b.*\b(not\s+in|different\s+from|differs)\b',
        r'\bdefine\b.*\bdiagonal\b',
        r'\blet\b.*\b(d|s|x)\b.*\b(be\s+the\s+element|be\s+defined\s+as)\b',
        r'\bdefine\b.*\bnew\b.*\b(set|string|sequence|number)\b',
        r'\bflip\b.*\b(bit|digit|digits|diagonal)\b',
        r'\bcomplement\b.*\b(the\s+diagonal|diagonal)\b',
    ]
    for pat in construction_patterns:
        if re.search(pat, t):
            return "CONSTRUCTION"

    # --- Contradiction (checked before claims) ---
    contradiction_patterns = [
        r'\bcontradiction\b',
        r'\bnot\s+in\s+the\s+(image|list|range|enumeration)\b',
        r'\bnot\s+enumerated\b',
        r'\bnot\s+counted\b',
        r'\bmissing\s+from\s+the\s+list\b',
        r'\btherefore\b.*\b(cannot|can\s+not)\b.*\b(bijection|surjection|enumeration)\b',
        r'\bno\s+such\b.*\b(bijection|surjection|enumeration)\b',
    ]
    for pat in contradiction_patterns:
        if re.search(pat, t):
            return "CONTRADICTION"

    # --- Conclusion (checked BEFORE countable/uncountable claims) ---
    conclusion_patterns = [
        r'\btherefore\b',
        r'\bthus\b',
        r'\bby\s+cantor\b',
        r'\bby\s+diagonalization\b',
        r'\bby\s+cantor.s\s+theorem\b',
        r'\bqed\b',
        r'∎',
        r'\bproven\b.*\bfor\s+all\b',
        r'\bproven\b.*\buncountable\b',
    ]
    for pat in conclusion_patterns:
        if re.search(pat, t):
            return "CONCLUSION"

    # --- Countability claim ---
    countable_patterns = [
        r'\bcountable\b',
        r'\bcountably\s+infinite\b',
        r'\bbijec(tion|tive)\b.*\b(n|natural|naturals|ω)\b',
        r'\benumeration\b.*\b(n|natural|naturals)\b',
        r'\bcan\s+be\s+(listed|enumerated)\b',
        r'\b(rationals|q|integers|z)\b.*\bcountable\b',
    ]
    for pat in countable_patterns:
        if re.search(pat, t):
            return "COUNTABLE_CLAIM"

    # --- Uncountability / cardinality claim ---
    uncountable_patterns = [
        r'\buncountable\b',
        r'\buncountably\s+infinite\b',
        r'\bstrictly\s+(larger|greater)\b.*\b(cardinality|size)\b',
        r'\b\|pow\b.*\|>\b',
        r'\b\|a\|\s*<\s*\|pow\s*\(a\)\|\b',
        r'\b\|n\|\s*<\s*\|r\|\b',
        r'\b\|r\|\s*>\s*\|n\|\b',
        r'\bno\b.*\b(bijection|surjection)\b.*\b(from\b.*\bto\b)',
        r'\bdiagonalization\b.*\b(uncountable|larger|greater)\b',
        r'\bcantor\b.*\b(theorem|diagonalization|uncountable)\b',
        r'\bcontinuum\b.*\b(hypothesis|uncountable)\b',
    ]
    for pat in uncountable_patterns:
        if re.search(pat, t):
            return "UNCOUNTABLE_CLAIM"

    return "OTHER"


def _detect_argument_type(steps: list[dict], classifications: list[str]) -> str:
    """Determine what kind of infinite-sets argument this is."""
    full_text = " ".join([s["text"].lower() for s in steps])

    # Diagonalization: assume a surjection exists, then either construct a missing
    # element or reach a contradiction. Either pattern signals intent.
    has_diagonalization = (
        "ASSUMPTION_SURJECTION" in classifications and
        ("CONSTRUCTION" in classifications or "CONTRADICTION" in classifications)
    )
    has_cantor_keyword = bool(re.search(r'\bcantor\b', full_text))
    has_diagonal_keyword = bool(re.search(r'\bdiagonal(ization)?\b', full_text))
    has_uncountable = "UNCOUNTABLE_CLAIM" in classifications
    has_countable = "COUNTABLE_CLAIM" in classifications

    if has_diagonalization or (has_cantor_keyword and has_uncountable):
        return "diagonalization"
    elif has_countable and not has_uncountable:
        return "countability"
    elif has_uncountable and not has_countable:
        return "uncountability"
    else:
        return "cardinality_general"


def validate(steps: list[dict]) -> dict:
    """
    Validate infinite-sets proof structure.

    Returns:
        {
            "valid": bool,
            "step_results": [{"number": int, "ok": bool, "reason": str}, ...],
            "overall_reason": str,
            "technique": "diagonalization" | "countability" | "uncountability" | "cardinality_general" | "unknown"
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

    # 2. Detect argument type
    arg_type = _detect_argument_type(steps, classifications)

    # 3. Locate first occurrence of each component
    def first_index(targets: list[str]) -> int:
        for i, c in enumerate(classifications):
            if c in targets:
                return i
        return -1

    assume_idx = first_index(["ASSUMPTION_SURJECTION"])
    construct_idx = first_index(["CONSTRUCTION"])
    contra_idx = first_index(["CONTRADICTION"])
    conclusion_idx = first_index(["CONCLUSION"])

    has_assume = assume_idx != -1
    has_construct = construct_idx != -1
    has_contra = contra_idx != -1
    has_conclusion = conclusion_idx != -1

    # 4. Per-step validation
    step_results = []
    all_ok = True

    for i, step in enumerate(steps):
        ok = True
        reason = "OK"
        cls = classifications[i]

        # Ordering checks (canonical diagonalization flow)
        if arg_type == "diagonalization":
            if cls == "ASSUMPTION_SURJECTION" and construct_idx != -1 and i > construct_idx:
                ok = False
                reason = "Assumption should appear before construction of missing element"
                all_ok = False
            elif cls == "CONSTRUCTION" and contra_idx != -1 and i > contra_idx:
                ok = False
                reason = "Construction should appear before contradiction"
                all_ok = False
            elif cls == "CONTRADICTION" and conclusion_idx != -1 and i > conclusion_idx:
                ok = False
                reason = "Contradiction should appear before conclusion"
                all_ok = False

        step_results.append({
            "number": step["number"],
            "ok": ok,
            "reason": reason
        })

    # 5. Global structural checks
    missing = []
    messages = []

    if arg_type == "diagonalization":
        if not has_assume:
            missing.append("assumption of surjection/enumeration")
        if not has_construct:
            missing.append("construction of missing element")
        if not has_contra:
            missing.append("contradiction")
        if not has_conclusion:
            missing.append("conclusion")

        if missing:
            overall_reason = "Diagonalization argument incomplete. Missing: " + ", ".join(missing) + "."
            all_ok = False
        else:
            overall_reason = "Diagonalization structure complete."

        # Extra sanity: construction must follow assumption
        if has_assume and has_construct and assume_idx > construct_idx:
            overall_reason += " Note: construction appears before assumption."
            all_ok = False

    elif arg_type == "countability":
        if not has_assume and not has_conclusion:
            missing.append("countability argument (bijection or enumeration)")
        if not has_conclusion:
            missing.append("conclusion")
        if missing:
            overall_reason = "Countability proof incomplete. Missing: " + ", ".join(missing) + "."
            all_ok = False
        else:
            overall_reason = "Countability structure complete."

    elif arg_type == "uncountability":
        if not has_assume and not has_contra:
            missing.append("uncountability argument (diagonalization or reduction)")
        if not has_conclusion:
            missing.append("conclusion")
        if missing:
            overall_reason = "Uncountability proof incomplete. Missing: " + ", ".join(missing) + "."
            all_ok = False
        else:
            overall_reason = "Uncountability structure complete."

    else:
        overall_reason = "General cardinality argument."
        if not has_conclusion:
            overall_reason += " Missing conclusion."
            all_ok = False

    # 6. Common fallacy: claiming bijection between A and pow(A)
    full_text = " ".join([s["text"].lower() for s in steps])
    bijection_pow_pattern = re.search(r'\b(bijection|bijective)\b.*\b(pow|power\s+set|2\^|℘)\b', full_text)
    if bijection_pow_pattern and arg_type != "countability":
        overall_reason += " Warning: Cantor's Theorem says |A| < |pow(A)|. A bijection between A and pow(A) is impossible."
        all_ok = False

    # 7. Common fallacy: claiming R is countable
    r_countable = re.search(r'\b(reals?|r)\b.*\bcountable\b', full_text)
    if r_countable:
        overall_reason += " Warning: The real numbers are uncountable (Cantor's diagonalization). Claiming they are countable is false."
        all_ok = False

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": overall_reason,
        "technique": arg_type
    }
