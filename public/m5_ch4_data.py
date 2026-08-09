# m5_ch4_data.py — Chapter 4 Mathematical Data Types Validator
# Validates claims about sets, functions, relations, and cardinality.
# MIT 6.042J Chapter 4.

import re


# ================================================================
# 1. KNOWLEDGE BASE (Sections 4.4, 4.5)
# Format: (regex_pattern, is_true, category, explanation)
# ================================================================

CHAPTER_4_CLAIMS = [
    # SET CLAIMS
    (r"empty\s+set.*subset|∅\s*⊆|∅\s*is\s+a\s+subset", True, "set",
     "The empty set is a subset of every set"),
    (r"a\s*⊆\s*a|subset.*itself|reflexive.*subset", True, "set",
     "Subset is reflexive: every set is a subset of itself"),
    (r"a\s*⊆\s*b.*b\s*⊆\s*c.*a\s*⊆\s*c|transitive.*subset", True, "set",
     "Subset is transitive"),
    (r"\|pow\s*\(\s*a\s*\)\|\s*=\s*2\^|2\^n\s*subsets|power\s+set.*2\^", True, "set",
     "Theorem 4.5.5: |pow(A)| = 2^|A|"),
    (r"\|a\s*∪\s*b\|\s*=\s*\|a\|\s*\+\s*\|b\|", False, "set",
     "Counterexample: A={1}, B={1}. Then |A∪B|=1 but |A|+|B|=2. Correct: |A∪B| = |A|+|B|−|A∩B|."),
    (r"a\s*∩\s*b\s*=\s*∅.*disjoint|disjoint.*intersection.*empty", True, "set",
     "Sets are disjoint iff their intersection is empty"),
    (r"a\s*⊆\s*b.*\|a\|\s*>\s*\|b\|", False, "set",
     "Counterexample: A={1}, B={1,2}. A⊆B but |A|=1<2=|B|. If A⊆B then |A|≤|B|."),

    # FUNCTION CLAIMS
    (r"injective\s+and\s+surjective.*bijective|bijective.*injective\s+and\s+surjective", True, "function",
     "Definition 4.4.2: a bijection is a function that is both injective and surjective"),
    (r"bijective.*injective|injective.*bijective|bijection.*injective", True, "function",
     "A bijection is injective by definition"),
    (r"bijective.*surjective|surjective.*bijective|bijection.*surjective", True, "function",
     "A bijection is surjective by definition"),
    (r"surjective.*injective|injective.*surjective", False, "function",
     "Counterexample: f:{1,2}→{1} with f(1)=f(2)=1. Surjective but NOT injective."),
    (r"function.*surjective|surjective.*function", False, "function",
     "Counterexample: f:{1}→{1,2} with f(1)=1. A function but NOT surjective."),
    (r"total.*function|function.*total", False, "function",
     "Counterexample: R={(1,1)} from domain {1,2} to {1}. Function (≤1 out) but NOT total (2 has no out-arrow)."),
    (r"injective.*surjective|surjective.*injective", False, "function",
     "Counterexample: f:{1,2}→{1} with f(1)=f(2)=1 is surjective but not injective."),

    # RELATION CLAIMS (arrow properties)
    (r"function.*≤1\s+arrow\s+out|≤1\s+arrow\s+out.*function", True, "relation",
     "Definition 4.4.2: a function has the [≤ 1 arrow out] property"),
    (r"surjective.*≥1\s+arrow\s+in|≥1\s+arrow\s+in.*surjective", True, "relation",
     "Definition 4.4.2: a surjective relation has the [≥ 1 arrow in] property"),
    (r"total.*≥1\s+arrow\s+out|≥1\s+arrow\s+out.*total", True, "relation",
     "Definition 4.4.2: a total relation has the [≥ 1 arrow out] property"),
    (r"injective.*≤1\s+arrow\s+in|≤1\s+arrow\s+in.*injective", True, "relation",
     "Definition 4.4.2: an injective relation has the [≤ 1 arrow in] property"),
    (r"bijective.*1\s+arrow|1\s+arrow.*bijective|bijection.*1\s+arrow", True, "relation",
     "Definition 4.4.2: a bijection has exactly 1 arrow out and exactly 1 arrow in"),
    (r"total.*surjective|surjective.*total", False, "relation",
     "Counterexample: f:{1,2}→{1,2,3} with f(1)=1, f(2)=2. Total but NOT surjective (3 has no arrow in)."),
    (r"total.*injective|injective.*total", False, "relation",
     "Counterexample: f:{1,2}→{1} with f(1)=f(2)=1. Total but NOT injective (1 has two arrows in)."),

    # CARDINALITY / MAPPING RULES (Theorem 4.5.4)
    (r"\|a\|\s*≥\s*\|b\|\s*iff\s*a\s+surj\s+b|a\s+surj\s+b\s*iff\s*\|a\|\s*≥\s*\|b\|", True, "cardinality",
     "Theorem 4.5.4 (Mapping Rule)"),
    (r"\|a\|\s*≤\s*\|b\|\s*iff\s*a\s+inj\s+b|a\s+inj\s+b\s*iff\s*\|a\|\s*≤\s*\|b\|", True, "cardinality",
     "Theorem 4.5.4 (Mapping Rule)"),
    (r"\|a\|\s*=\s*\|b\|\s*iff\s*a\s+bij\s+b|a\s+bij\s+b\s*iff\s*\|a\|\s*=\s*\|b\|", True, "cardinality",
     "Theorem 4.5.4 (Mapping Rule)"),
    (r"\|a\|\s*>\s*\|b\|.*a\s+surj\s+b|a\s+surj\s+b.*\|a\|\s*>\s*\|b\|", False, "cardinality",
     "Counterexample: A={1,2}, B={1,2}. |A|=|B| and A surj B. Correct: |A|≥|B| iff A surj B."),
]


# ================================================================
# 2. QUALITY CHECKS (Section 1.9 — reused)
# ================================================================

def check_quality(steps: list[dict]) -> list[dict]:
    issues = []
    if not steps:
        return issues
    full_text = " ".join(step["text"].lower() for step in steps)
    if not re.search(r"\b(theorem|claim|proposition|lemma)\b", full_text):
        issues.append({"step_index": 0, "message": "Section 1.9: State what you're proving"})
    has_proof = any(re.search(r"\bproof\b", s["text"].lower()) for s in steps[:2])
    if not has_proof:
        issues.append({"step_index": 0, "message": "Section 1.9: Begin with 'Proof'"})
    last = steps[-1]["text"].lower()
    if not re.search(r"(∎|qed|q\.e\.d\.)", last):
        issues.append({"step_index": len(steps) - 1, "message": "Section 1.9: End with ∎ or QED"})
    for i, step in enumerate(steps):
        if re.search(r"\b(clearly|obviously)\b", step["text"].lower()):
            issues.append({"step_index": i, "message": "Section 1.9: Avoid 'clearly' or 'obviously'"})
    return issues


# ================================================================
# 3. CLAIM EXTRACTOR
# ================================================================

def extract_claim(steps: list[dict]) -> tuple:
    for i, step in enumerate(steps):
        text = step["text"].strip()
        match = re.search(r"(theorem|claim|proposition|lemma)[\s:]*(.+)", text, re.IGNORECASE)
        if match:
            return match.group(2).strip(), i
    return None, -1


# ================================================================
# 4. CLAIM MATCHER
# ================================================================

def match_claim(claim_text: str) -> tuple:
    claim_lower = claim_text.lower()
    for pattern, is_true, category, explanation in CHAPTER_4_CLAIMS:
        if re.search(pattern, claim_lower, re.IGNORECASE):
            return is_true, category, explanation
    return None, None, None


# ================================================================
# 5. PROOF STRUCTURE CHECKERS
# ================================================================

def has_counterexample(steps: list[dict]) -> bool:
    full_text = " ".join(step["text"].lower() for step in steps)
    return bool(re.search(r"counterexample|counter-example|counter example", full_text))


def has_justification(steps: list[dict], category: str) -> bool:
    full_text = " ".join(step["text"].lower() for step in steps)
    if category == "relation" or category == "function":
        return bool(re.search(r"definition\s+4\.4\.2|def\s+4\.4\.2|arrow\s+(out|in)|by\s+definition", full_text))
    if category == "cardinality":
        return bool(re.search(r"theorem\s+4\.5\.4|mapping\s+rule|lemma\s+4\.5\.3", full_text))
    if category == "set":
        return bool(re.search(r"theorem\s+4\.5\.5|by\s+definition|counting|bijection", full_text))
    return bool(re.search(r"by\s+definition|theorem|lemma|definition", full_text))


# ================================================================
# 6. STRUCTURAL VALIDATOR
# ================================================================

def validate_data_types(steps: list[dict]) -> list[dict]:
    issues = []
    claim_text, claim_index = extract_claim(steps)

    if claim_text is None:
        issues.append({
            "step_index": 0,
            "message": "Section 4.x: State a claim about sets, functions, relations, or cardinality"
        })
        return issues

    is_true, category, explanation = match_claim(claim_text)

    if is_true is None:
        issues.append({
            "step_index": claim_index,
            "message": f"Section 4.x: Unrecognized claim '{claim_text}'. Known: sets, functions, relations, cardinality."
        })
        return issues

    if is_true:
        if not has_justification(steps, category):
            issues.append({
                "step_index": claim_index,
                "message": f"Section 4.x: True claim ({explanation}), but proof lacks citation. Cite Definition 4.4.2, Theorem 4.5.4, or Theorem 4.5.5."
            })
    else:
        if not has_counterexample(steps):
            issues.append({
                "step_index": claim_index,
                "message": f"Section 4.x: FALSE CLAIM — {explanation}"
            })

    return issues


# ================================================================
# 7. TECHNIQUE CLASSIFIER
# ================================================================

def classify_technique(steps: list[dict]) -> str:
    full_text = " ".join(step["text"].lower() for step in steps)

    wop_signals = [r"well ordering", r"\bwop\b", r"smallest counterexample",
                   r"smallest element", r"minimum element", r"least element"]
    if any(re.search(p, full_text) for p in wop_signals):
        return "well_ordering"

    # M5 checks BEFORE M4, because M5 keywords are more specific
    has_cardinality = re.search(
        r"\b(cardinality|mapping\s+rule|surj|inj|bij)\b|\|a\||\|b\||\|c\|",
        full_text
    )
    has_set = re.search(
        r"\b(set|sets|subset|subsets|union|intersection|power\s+set|pow|disjoint|∪|∩|⊆|⊇|∅)\b",
        full_text
    )
    has_function = re.search(
        r"\b(function|total|one-to-one|onto)\b",
        full_text
    )
    has_relation = re.search(
        r"\b(relation|binary\s+relation|arrow\s+out|arrow\s+in|inverse\s+relation|inverse\s+image)\b",
        full_text
    )

    if has_cardinality:
        return "cardinality"
    if has_set:
        return "set_operation"
    if has_function:
        return "function_property"
    if has_relation:
        return "relation_property"

    # M4 checks
    if re.search(r"\bequivalent\b|\bequivalence\b|\biff\b|↔", full_text):
        return "equivalence_check"

    has_therefore = re.search(r"\b(therefore|thus|hence)\b", full_text)
    has_formula_ops = re.search(
        r"\b(implies|and|or|not|iff|xor)\b|→|∧|∨|¬|↔|⊕", full_text
    )
    if has_therefore and has_formula_ops:
        return "logical_argument"

    if re.search(r"\bvalid\b|\btautology\b|\bsatisfiable\b", full_text):
        return "validity_check"

    # M2 checks
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


# ================================================================
# 8. MAIN ENTRY POINT
# ================================================================

def validate(steps: list[dict]) -> dict:
    if not steps:
        return {"valid": False, "step_results": [], "overall_reason": "No steps provided", "technique": "unknown"}

    technique = classify_technique(steps)
    quality_issues = check_quality(steps)
    structural_issues = []

    if technique in ("set_operation", "function_property", "relation_property", "cardinality"):
        structural_issues = validate_data_types(steps)

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
        step_results.append({"number": step.get("number", i + 1), "ok": ok, "reason": reason})

    overall = f"Technique: {technique.replace('_', ' ')}. "
    total = len(all_issues)
    if total == 0:
        overall += "All checks passed."
    else:
        overall += f"{total} issue(s) found."

    return {"valid": all_ok, "step_results": step_results, "overall_reason": overall, "technique": technique}
