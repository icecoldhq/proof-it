# m6_ch5_induction.py — Proof It Induction Validator (M6)
# Validates structural correctness of induction proofs.
# Distinguishes ordinary induction from strong induction.

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
    Classify a single proof step into an induction component.
    Returns one of: BASE_CASE, STRONG_IH, ORDINARY_IH,
                    INDUCTIVE_STEP, CONCLUSION, OTHER
    """
    t = text.lower()

    # --- Explicit structural labels take highest priority ---
    if re.search(r'\b(inductive|induction)\s+step\b', t):
        return "INDUCTIVE_STEP"
    if re.search(r'\bbase\s+(case|step|basis)\b', t):
        return "BASE_CASE"
    if re.search(r'\bconclusion\b', t):
        return "CONCLUSION"

    # --- Strong Inductive Hypothesis (specific patterns) ---
    strong_ih_patterns = [
        r'\bstrong\s+induction\s+hypothesis\b',
        r'\bassume\b.*\b(all|every)\b.*\b(k|j|i|m)\b.*\b(≤|<=|less\s+than\s+or\s+equal|up\s+to)\b.*\bn\b',
        r'\bassume\b.*\b[a-z]\s*\(\s*\d+\s*\)\b.*\b(and|through|to|,\s*)\b.*\b[a-z]\s*\(\s*n\s*\)',
        r'\bassume\b.*\b[a-z]\s*\(\s*k\s*\)\b.*\b(for\s+all|∀)\b.*\b(k|j)\b.*\b(≤|<=)\b.*\bn\b',
        r'\b[a-z]\s*\(\s*0\s*\).*\b[a-z]\s*\(\s*1\s*\).*\b[a-z]\s*\(\s*n\s*\)',
    ]
    for pat in strong_ih_patterns:
        if re.search(pat, t):
            return "STRONG_IH"

    # --- Ordinary Inductive Hypothesis ---
    ordinary_ih_patterns = [
        r'\b(inductive|induction)\s+hypothesis\b',
        r'\bih\b',
        r'\bassume\b.*\b[a-z]\s*\(\s*n\s*\)',
        r'\bsuppose\b.*\b[a-z]\s*\(\s*n\s*\)',
    ]
    for pat in ordinary_ih_patterns:
        if re.search(pat, t):
            return "ORDINARY_IH"

    # --- Base Case by content (specific number verification) ---
    if re.search(r'\bn\s*=\s*\d+\b.*\b(is\s+true|holds|even|odd|prime|verified|trivial)\b', t):
        return "BASE_CASE"
    if re.search(r'\b[a-z]\s*\(\s*\d+\s*\)\s*(is\s+true|holds|even|odd|prime|verified|trivial)', t):
        return "BASE_CASE"

    # --- Inductive Step by content ---
    if re.search(r'\bprove\b.*\b[a-z]\s*\(\s*n\s*[\+\-]\s*\d+\s*\)', t):
        return "INDUCTIVE_STEP"
    if re.search(r'\bshow\b.*\b[a-z]\s*\(\s*n\s*[\+\-]\s*\d+\s*\)', t):
        return "INDUCTIVE_STEP"
    if re.search(r'\bmust\s+show\b.*\b[a-z]\s*\(\s*n\s*[\+\-]\s*\d+\s*\)', t):
        return "INDUCTIVE_STEP"
    if re.search(r'\bwant\s+to\s+prove\b', t):
        return "INDUCTIVE_STEP"

    # --- Conclusion by content ---
    conclusion_patterns = [
        r'\btherefore\b.*\b(all|every|for\s+all|∀)\b',
        r'\bthus\b.*\b(all|every|for\s+all|∀)\b',
        r'\bby\s+(strong\s+)?induction\b',
        r'\bby\s+the\s+principle\s+of\s+(strong\s+)?induction\b',
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
    Validate induction proof structure.

    Returns:
        {
            "valid": bool,
            "step_results": [{"number": int, "ok": bool, "reason": str}, ...],
            "overall_reason": str,
            "technique": "ordinary_induction" | "strong_induction" | "unknown"
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

    # 2. Detect induction type from actual IH classifications
    has_strong_ih = "STRONG_IH" in classifications
    has_ordinary_ih = "ORDINARY_IH" in classifications

    if has_strong_ih:
        detected_type = "strong_induction"
    elif has_ordinary_ih:
        detected_type = "ordinary_induction"
    else:
        detected_type = "unknown"

    # 3. Locate first occurrence of each component
    def first_index(targets: list[str]) -> int:
        for i, c in enumerate(classifications):
            if c in targets:
                return i
        return -1

    base_idx = first_index(["BASE_CASE"])
    ih_idx = first_index(["ORDINARY_IH", "STRONG_IH"])
    step_idx = first_index(["INDUCTIVE_STEP"])
    conclusion_idx = first_index(["CONCLUSION"])

    has_base = base_idx != -1
    has_ih = ih_idx != -1
    has_step = step_idx != -1
    has_conclusion = conclusion_idx != -1

    # 4. Per-step validation
    step_results = []
    all_ok = True

    for i, step in enumerate(steps):
        ok = True
        reason = "OK"
        cls = classifications[i]

        # Ordering checks
        if cls == "BASE_CASE" and ih_idx != -1 and i > ih_idx:
            ok = False
            reason = "Base case should appear before inductive hypothesis"
            all_ok = False
        elif cls in ("ORDINARY_IH", "STRONG_IH") and step_idx != -1 and i > step_idx:
            ok = False
            reason = "Inductive hypothesis should appear before inductive step"
            all_ok = False
        elif cls == "INDUCTIVE_STEP" and conclusion_idx != -1 and i > conclusion_idx:
            ok = False
            reason = "Inductive step should appear before conclusion"
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

    if detected_type == "strong_induction" and not has_strong_ih:
        missing.append("strong inductive hypothesis")
    elif detected_type == "ordinary_induction" and not has_ordinary_ih:
        missing.append("inductive hypothesis")
    elif detected_type == "unknown" and not has_ih:
        missing.append("inductive hypothesis")

    if not has_step:
        missing.append("inductive step")
    if not has_conclusion:
        missing.append("conclusion")

    if missing:
        overall_reason = "Missing required induction components: " + ", ".join(missing) + "."
        all_ok = False
    else:
        overall_reason = "Induction structure complete."
        if detected_type == "strong_induction":
            overall_reason += " Strong induction pattern detected."
        elif detected_type == "ordinary_induction":
            overall_reason += " Ordinary induction pattern detected."

    # 6. Type mismatch: strong induction claimed but only ordinary IH provided
    full_text = " ".join([s["text"].lower() for s in steps])
    has_strong_keyword = bool(re.search(r'\bstrong\s+induction\b', full_text))

    if has_strong_keyword and has_ordinary_ih and not has_strong_ih:
        overall_reason = (
            "Type mismatch: 'strong induction' is mentioned, but the hypothesis only assumes P(n). "
            "Strong induction requires assuming P(k) for all k ≤ n."
        )
        all_ok = False

    # 7. Extra ordering sanity checks (global summary)
    if has_base and has_ih and base_idx > ih_idx:
        overall_reason += " Note: base case appears after inductive hypothesis."
        all_ok = False
    if has_ih and has_step and ih_idx > step_idx:
        overall_reason += " Note: inductive hypothesis appears after inductive step."
        all_ok = False
    if has_step and has_conclusion and step_idx > conclusion_idx:
        overall_reason += " Note: inductive step appears after conclusion."
        all_ok = False

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": overall_reason,
        "technique": detected_type
    }
