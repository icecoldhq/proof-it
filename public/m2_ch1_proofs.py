# m2_ch1_proofs.py — Chapter 1 Proof Techniques Validator
# Validates natural-language proofs against MIT 6.042J
# Chapter 1 patterns.

import re

def classify_technique(steps: list[dict]) -> str:
    """
    Detect which chapter 1 proof technique the user is attempting.
    Returns one of: 'implication_direct',
    'implication_contrapositive',
    'iff_both', 'iff_chain', 'cases', 'contradiction', 'unknown'
    """

    full_text = " ".join(step["text"].lower() for step in steps)
    if re.search(r"proof by contradiction|we use contradiction", full_text):
        return "contradiction"

    if re.search(r"suppose (the claim is false|not )", full_text):
        return "contradiction"

    # FIX: Check iff BEFORE contrapositive, since iff proofs may use
    # contrapositive in one direction.
    if re.search(r"if and only if|iff", full_text):
        return "iff_both"

    if re.search(r"contrapositive|prove the contrapositive", full_text):
        return "implication_contrapositive"

    if re.search(r"case\s+\d|case\s*:", full_text):
        return "cases"

    if re.search(r"\b(assume|suppose)\b", full_text):
        return "implication_direct"

    return "unknown"

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
   
def validate_contradiction(steps: list[dict]) -> list[dict]:
    """
    Section 1.8 structural check.
    Returns list of issues: [{"step_index": int, "message": str}, ...]
    """
    
    issues = []
    full_text = " ".join(step["text"].lower() for step in steps)

    if not re.search(r"proof by contradiction|we use contradiction", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.8: Declare 'We use proof by contradiction'"
        })

    if not re.search(r"\b(suppose|assume)\b", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.8: Assume the negation of the claim"
        })

    if not re.search(r"(this is a contradiction|contradicts|we have a contradiction|this is impossible|this is absurd|leads to a contradiction)", full_text):
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.8: Derive a contradiction from your assumption"
        })

    assumption_index = -1
    conclusion_index = -1
    for i, step in enumerate(steps):
        if re.search(r"\b(suppose|assume)\b", step["text"].lower()):
            assumption_index = i
        if re.search(r"\b(therefore|thus|so|hence)\b", step["text"].lower()):
            conclusion_index = i
    
    if assumption_index != -1 and conclusion_index != -1 and conclusion_index <= assumption_index + 1:
        issues.append({
            "step_index": conclusion_index,
            "message": "Section 1.8: Need steps between assumption and conclusion to derive the contradiction"
        })

    last = steps[-1]["text"].lower() if steps else ""
    if not re.search(r"\b(therefore|thus|so|hence)\b", last):
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.8: Conclude that the original claim must be true"
        })

    return issues

def validate_implication_direct(steps: list[dict]) -> list[dict]:
    """
    Section 1.5.1 Method #1 structural check.
    Returns list of issues.
    """

    issues = []

    assumption_found = False
    assumption_index = -1
    for i, step in enumerate(steps):
        if re.search(r"\b(assume|suppose)\b", step["text"].lower()):
            assumption_found = True
            assumption_index = i
            break

    if not assumption_found:
        issues.append({
            "step_index": 0,
            "message": "Section 1.5.1: Assume P to begin the implication proof"
        })


    conclusion_found = False
    conclusion_index = -1
    for i, step in enumerate(steps):
        if re.search(r"\b(therefore|thus|so|hence)\b", step["text"].lower()):
            conclusion_found = True
            conclusion_index = i

    if not conclusion_found:
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.5.1: Derive Q and conclude with 'Therefore Q'"
        })

    if assumption_found and conclusion_found and conclusion_index <= assumption_index + 1:
        issues.append({
            "step_index": conclusion_index,
            "message": "Section 1.5.1: Show how Q follows from P with intermediate steps"
        })

    return issues

def validate_implication_contrapositive(steps: list[dict]) -> list[dict]:
    """
    Section 1.5.2 Method #2 structural check.
    Returns list of issues.
    """

    issues = []
    full_text = " ".join(step["text"].lower() for step in steps)

    if not re.search(r"prove the contrapositive|we prove the contrapositive", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.5.2: Declare 'We prove the contrapositive' and state it"
        })

    assumption_found = False
    assumption_index = -1
    for i, step in enumerate(steps):
        if re.search(r"\b(assume|suppose)\b", step["text"].lower()):
            assumption_found = True
            assumption_index = i
            break

    if not assumption_found:
        issues.append({
            "step_index": 0,
            "message": "Section 1.5.2: Assume NOT Q to begin the contrapositive proof"
        })

    conclusion_found = False
    conclusion_index = -1
    for i, step in enumerate(steps):
        if re.search(r"\b(therefore|thus|so|hence)\b", step["text"].lower()):
            conclusion_found = True
            conclusion_index = i

    if not conclusion_found:
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.5.2: Derive NOT P and conclude"
        })

    if assumption_found and conclusion_found and conclusion_index <= assumption_index + 1:
        issues.append({
            "step_index": conclusion_index,
            "message": "Section 1.5.2: Show how NOT P follows from NOT Q with intermediate steps"
        })

    return issues

def validate_cases(steps: list[dict]) -> list[dict]:
    """
    Section 1.7 structural check.
    Returns list of issues.
    """

    issues = []
    full_text = " ".join(step["text"].lower() for step in steps)

    case_count = len(re.findall(r"\bcase\s+\d+\b|\bcase\s*:\b", full_text))
    if case_count < 2:
        issues.append({
            "step_index": 0,
            "message": "Section 1.7: Enumerate at least two cases (Case 1, Case 2, ...)"
        })

    if not re.search(r"\b(all cases|every case|in either case|holds in all|theorem holds|in both cases)\b", full_text):
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.7: Conclude that the theorem holds in all cases"
        })

    return issues

def validate_iff_both(steps: list[dict]) -> list[dict]:
    """
    Section 1.6.1 Method #1 structural check.
    Returns list of issues.
    """

    issues = []
    full_text = " ".join(step["text"].lower() for step in steps)

    if not re.search(r"(vice-versa|both directions|p implies q and q implies p|each statement implies the other)", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.6.1: Declare that you will prove both directions"
        })

    if not re.search(r"(first we show|first, we show|first direction|p implies q)", full_text):
        issues.append({
            "step_index": 0,
            "message": "Section 1.6.1: Show the first direction (P implies Q)"
        })

    if not re.search(r"(now we show|now, we show|second direction|q implies p|conversely)", full_text):
        issues.append({
            "step_index": len(steps) - 1,
            "message": "Section 1.6.1: Show the second direction (Q implies P)"
        })

    return issues


def validate(steps: list[dict]) -> dict:
    """
    Main entry point for Chapter 1 proof validation.
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
    if technique == "contradiction":
        structural_issues = validate_contradiction(steps)

    if technique == "implication_direct":
        structural_issues = validate_implication_direct(steps)

    if technique == "implication_contrapositive":
        structural_issues = validate_implication_contrapositive(steps)

    if technique == "cases":
        structural_issues = validate_cases(steps)

    if technique == "iff_both":
        structural_issues = validate_iff_both(steps)
    
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
