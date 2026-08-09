# m3_ch2_wop.py — Chapter 2 Well Ordering Principle Validator
# Validates natural-language WOP proofs against MIT 6.042J Chapter 2.

import re


# ------------------------------------------------------------------
# QUALITY CHECKS (reused from M2 — Section 1.9 style)
# ------------------------------------------------------------------
def check_quality(steps: list[dict]) -> list[dict]:
    """
    Section 1.9 quality checks. Returns list of issues.
    Each issue: {"step_index": int, "message": str}
    """
    issues = []
    if not steps:
        return issues

    full_text = " ".join(step["text"].lower() for step in steps)

    if not re.search(r"\b(theorem|claim|proposition|lemma)\b", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.9: State what you're proving"
        })

    has_proof = any(re.search(r"\bproof\b", s["text"].lower()) for s in steps[:2])
    if not has_proof:
        issues.append({
            "step_index": 0,
            "message": "Section 1.9: Begin with 'Proof'"
        })

    last = steps[-1]["text"].lower()
    if not re.search(r"(∎|qed|q\.e\.d\.)", last):
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.9: End with ∎ or QED"
        })

    for i, step in enumerate(steps):
        if re.search(r"\b(clearly|obviously)\b", step["text"].lower()):
            issues.append({
                "step_index": i,
                "message": "Section 1.9: Avoid 'clearly' or 'obviously'"
            })

    return issues


# ------------------------------------------------------------------
# TECHNIQUE CLASSIFIER
# ------------------------------------------------------------------
def classify_technique(steps: list[dict]) -> str:
    """
    Detect WOP proof. Checked BEFORE regular contradiction
    because WOP proofs use contradiction internally.
    """
    full_text = " ".join(step["text"].lower() for step in steps)

    wop_signals = [
        r"well ordering",
        r"\bwop\b",
        r"smallest counterexample",
        r"smallest element",
        r"minimum element",
        r"least element",
    ]
    if any(re.search(p, full_text) for p in wop_signals):
        return "well_ordering"

    # Fall back to M2 classifiers
    if re.search(r"proof by contradiction|we use contradiction", full_text):
        return "contradiction"
    if re.search(r"suppose (the claim is false|not )", full_text):
        return "contradiction"
    if re.search(r"if and only if|iff", full_text):
        return "iff_both"
    if re.search(r"contrapositive|prove the contrapositive", full_text):
        return "implication_contrapositive"
    if re.search(r"case\s+\d|case\s*:", full_text):
        return "cases"
    if re.search(r"\b(assume|suppose)\b", full_text):
        return "implication_direct"

    return "unknown"


# ------------------------------------------------------------------
# WOP STRUCTURAL VALIDATOR
# ------------------------------------------------------------------
def validate_wop(steps: list[dict]) -> list[dict]:
    """
    Section 2.2 template structural check.
    Returns list of issues: [{"step_index": int, "message": str}, ...]
    """
    issues = []
    full_text = " ".join(step["text"].lower() for step in steps)

    # --- 1. Define set C of counterexamples ---
    set_defined = re.search(
        r"(let\s+c\s+be|define\s+c|set\s+of\s+counterexamples|"
        r"collect\s+them\s+in\s+a\s+set|counterexamples?\s+to)",
        full_text
    )
    if not set_defined:
        issues.append({
            "step_index": 0,
            "message": "Section 2.2: Define the set C of counterexamples"
        })

    # --- 2. Assume C is nonempty ---
    nonempty_assumed = re.search(
        r"(assume.*c\s+is\s+nonempty|suppose\s+c\s+is\s+not\s+empty|"
        r"assume\s+there\s+are\s+counterexamples|assume\s+c\s+is\s+not\s+empty|"
        r"assuming.*counterexamples)",
        full_text
    )
    if not nonempty_assumed:
        issues.append({
            "step_index": 0,
            "message": "Section 2.2: Assume for contradiction that C is nonempty"
        })

    # --- 3. Invoke WOP and name the smallest element ---
    wop_invoked = re.search(
        r"(by\s+wop|by\s+the\s+well\s+ordering\s+principle|"
        r"smallest\s+element|minimum\s+element|least\s+element)",
        full_text
    )
    if not wop_invoked:
        issues.append({
            "step_index": 0,
            "message": "Section 2.2: Invoke WOP to obtain a smallest element of C"
        })

    # --- 4. Derive a contradiction ---
    contradiction_found = re.search(
        r"(this\s+is\s+a\s+contradiction|contradicts|contradicting|"
        r"we\s+have\s+a\s+contradiction|leads\s+to\s+a\s+contradiction)",
        full_text
    )
    if not contradiction_found:
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 2.2: Derive a contradiction from the smallest counterexample"
        })

    # --- 5. Conclude C is empty ---
    # Accepts explicit "C is empty", "assumption is false", or "we are done"
    conclusion_found = re.search(
        r"(c\s+must\s+be\s+empty|c\s+is\s+empty|no\s+counterexamples|"
        r"assumption.*false|therefore\s+false|must\s+therefore\s+be\s+false|"
        r"we\s+are\s+done|done\.|proof\s+is\s+complete|"
        r"this\s+completes\s+the\s+proof)",
        full_text
    )
    if not conclusion_found:
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 2.2: Conclude that C is empty (no counterexamples exist)"
        })

    # --- 6. Gap check: need steps between WOP invocation and contradiction ---
    wop_index = -1
    contradiction_index = -1
    for i, step in enumerate(steps):
        if re.search(r"(by\s+wop|well\s+ordering|smallest\s+element|"
                     r"minimum\s+element|least\s+element)", step["text"].lower()):
            wop_index = i
        if re.search(r"(contradiction|contradicts|contradicting)", step["text"].lower()):
            contradiction_index = i

    if wop_index != -1 and contradiction_index != -1 and contradiction_index <= wop_index + 1:
        issues.append({
            "step_index": contradiction_index,
            "message": "Section 2.2: Need steps between invoking WOP and deriving the contradiction"
        })

    return issues


# ------------------------------------------------------------------
# MAIN ENTRY POINT (same contract as M2)
# ------------------------------------------------------------------
def validate(steps: list[dict]) -> dict:
    """
    Main entry point for Chapter 2 WOP validation.
    Returns: {
        "valid": bool,
        "step_results": [{"number": int, "ok": bool, "reason": str}, ...],
        "overall_reason": str,
        "technique": str
    }
    """
    if not steps:
        return {
            "valid": False,
            "step_results": [],
            "overall_reason": "No steps provided",
            "technique": "unknown"
        }

    technique = classify_technique(steps)
    quality_issues = check_quality(steps)
    structural_issues = []

    if technique == "well_ordering":
        structural_issues = validate_wop(steps)

    all_issues = quality_issues + structural_issues
    all_ok = len(all_issues) == 0

    step_results = []
    for i, step in enumerate(steps):
        ok = True
        reason = "OK"
        for issue in all_issues:
            if issue["step_index"] == i:
                ok = False
                reason = issue["message"]
                break
        step_results.append({
            "number": step.get("number", i + 1),
            "ok": ok,
            "reason": reason
        })

    overall = f"Technique: {technique.replace('_', ' ')}. "
    total_issues = len(all_issues)
    if total_issues == 0:
        overall += "All checks passed."
    else:
        overall += f"{total_issues} issue(s) found."

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": overall,
        "technique": technique
    }
