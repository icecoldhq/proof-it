# m4_ch3_logic.py — Chapter 3 Logical Formulas Validator
# Truth-table engine for propositional logic. MIT 6.042J Chapter 3.

import re
from itertools import product


# ================================================================
# 1. AST NODE CLASSES (Section 3.1: Propositions from Propositions)
# ================================================================

class Formula:
    pass

class Var(Formula):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name

class Not(Formula):
    def __init__(self, child: Formula):
        self.child = child
    def __repr__(self):
        return f"¬{self.child}"

class And(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} ∧ {self.right})"

class Or(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} ∨ {self.right})"

class Implies(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} → {self.right})"

class Iff(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} ↔ {self.right})"

class Xor(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} ⊕ {self.right})"


# ================================================================
# 2. TOKENIZER (Section 3.1.2: Cryptic Notation)
# Handles words AND symbols: AND/∧, OR/∨, NOT/¬, IMPLIES/→, IFF/↔, XOR/⊕
# ================================================================

def tokenize(text: str) -> list:
    text = text.lower().strip()
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue

        # Single uppercase letter variables
        if 'a' <= text[i] <= 'z' and (i + 1 >= len(text) or not text[i + 1].isalpha()):
            tokens.append(('VAR', text[i].upper()))
            i += 1
            continue

        # Multi-letter words (longest first)
        if text.startswith('implies', i):
            tokens.append(('IMPLIES', 'implies')); i += 7; continue
        if text.startswith('iff', i):
            tokens.append(('IFF', 'iff')); i += 3; continue
        if text.startswith('xor', i):
            tokens.append(('XOR', 'xor')); i += 3; continue
        if text.startswith('and', i):
            tokens.append(('AND', 'and')); i += 3; continue
        if text.startswith('or', i):
            tokens.append(('OR', 'or')); i += 2; continue
        if text.startswith('not', i):
            tokens.append(('NOT', 'not')); i += 3; continue

        # Single-char symbols
        if text[i] in '¬!~':
            tokens.append(('NOT', text[i])); i += 1; continue
        if text[i] in '∧&':
            tokens.append(('AND', text[i])); i += 1; continue
        if text[i] in '∨|':
            tokens.append(('OR', text[i])); i += 1; continue
        if text[i] == '→' or text.startswith('->', i) or text.startswith('=>', i):
            tokens.append(('IMPLIES', '→')); i += 1 if text[i] == '→' else 2; continue
        if text[i] == '↔' or text.startswith('<->', i) or text.startswith('<=>', i):
            tokens.append(('IFF', '↔')); i += 1 if text[i] == '↔' else 3; continue
        if text[i] == '⊕' or text[i] == '^':
            tokens.append(('XOR', '⊕')); i += 1; continue
        if text[i] == '(':
            tokens.append(('LPAREN', '(')); i += 1; continue
        if text[i] == ')':
            tokens.append(('RPAREN', ')')); i += 1; continue

        if text[i].isalpha():
            tokens.append(('VAR', text[i].upper())); i += 1; continue

        i += 1
    return tokens


# ================================================================
# 3. PARSER — Recursive Descent
# Precedence: IFF → IMPLIES → OR → XOR → AND → NOT
# ================================================================

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        tok = self.peek(); self.pos += 1; return tok

    def parse(self) -> Formula:
        return self.parse_iff()

    def parse_iff(self):
        left = self.parse_implies()
        while self.peek() and self.peek()[0] == 'IFF':
            self.consume(); right = self.parse_implies(); left = Iff(left, right)
        return left

    def parse_implies(self):
        left = self.parse_or()
        while self.peek() and self.peek()[0] == 'IMPLIES':
            self.consume(); right = self.parse_or(); left = Implies(left, right)
        return left

    def parse_or(self):
        left = self.parse_xor()
        while self.peek() and self.peek()[0] == 'OR':
            self.consume(); right = self.parse_xor(); left = Or(left, right)
        return left

    def parse_xor(self):
        left = self.parse_and()
        while self.peek() and self.peek()[0] == 'XOR':
            self.consume(); right = self.parse_and(); left = Xor(left, right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek() and self.peek()[0] == 'AND':
            self.consume(); right = self.parse_not(); left = And(left, right)
        return left

    def parse_not(self):
        if self.peek() and self.peek()[0] == 'NOT':
            self.consume(); child = self.parse_not(); return Not(child)
        return self.parse_atom()

    def parse_atom(self):
        tok = self.peek()
        if tok and tok[0] == 'VAR':
            self.consume(); return Var(tok[1])
        if tok and tok[0] == 'LPAREN':
            self.consume(); expr = self.parse_iff()
            if self.peek() and self.peek()[0] == 'RPAREN': self.consume()
            return expr
        return None


def parse_formula(text: str) -> Formula:
    tokens = tokenize(text)
    if not tokens: return None
    parser = Parser(tokens)
    result = parser.parse()
    if parser.pos != len(tokens): return None
    return result


# ================================================================
# 4. TRUTH-TABLE ENGINE (Section 3.3: Equivalence and Validity)
# ================================================================

def eval_formula(node: Formula, env: dict) -> bool:
    if isinstance(node, Var): return env.get(node.name, False)
    if isinstance(node, Not): return not eval_formula(node.child, env)
    if isinstance(node, And): return eval_formula(node.left, env) and eval_formula(node.right, env)
    if isinstance(node, Or):  return eval_formula(node.left, env) or eval_formula(node.right, env)
    if isinstance(node, Implies): return (not eval_formula(node.left, env)) or eval_formula(node.right, env)
    if isinstance(node, Iff): return eval_formula(node.left, env) == eval_formula(node.right, env)
    if isinstance(node, Xor): return eval_formula(node.left, env) != eval_formula(node.right, env)
    return False


def get_vars(node: Formula) -> set:
    result = set()
    def collect(n):
        if isinstance(n, Var): result.add(n.name)
        elif isinstance(n, Not): collect(n.child)
        elif hasattr(n, 'left'): collect(n.left); collect(n.right)
    collect(node)
    return result


def all_assignments(vars_list: list):
    for bits in product([False, True], repeat=len(vars_list)):
        yield dict(zip(vars_list, bits))


def formulas_equal(a: Formula, b: Formula) -> bool:
    if type(a) != type(b): return False
    if isinstance(a, Var): return a.name == b.name
    if isinstance(a, Not): return formulas_equal(a.child, b.child)
    return formulas_equal(a.left, b.left) and formulas_equal(a.right, b.right)


# ================================================================
# 5. HELPERS
# ================================================================

def extract_formula(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"^(assume|suppose|let|then|so|thus|therefore|hence)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[.∎]\s*$", "", text)
    return text.strip()


# ================================================================
# 6. QUALITY CHECKS (Section 1.9 — reused)
# ================================================================

def check_quality(steps: list[dict]) -> list[dict]:
    issues = []
    if not steps: return issues
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
# 7. TECHNIQUE CLASSIFIER
# ================================================================

def classify_technique(steps: list[dict]) -> str:
    full_text = " ".join(step["text"].lower() for step in steps)

    wop_signals = [r"well ordering", r"\bwop\b", r"smallest counterexample",
                   r"smallest element", r"minimum element", r"least element"]
    if any(re.search(p, full_text) for p in wop_signals):
        return "well_ordering"

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
# 8. FALLACY DETECTOR (Section 3.3.1)
# ================================================================

def detect_fallacy(premises: list, conclusion: Formula) -> str:
    # Affirming the consequent: P→Q, Q ⊢ P
    for p1 in premises:
        for p2 in premises:
            if isinstance(p1, Implies) and formulas_equal(p1.right, p2) and formulas_equal(p1.left, conclusion):
                return "Fallacy: affirming the consequent (P→Q, Q ∴ P)"

    # Denying the antecedent: P→Q, ¬P ⊢ ¬Q
    for p1 in premises:
        for p2 in premises:
            if isinstance(p1, Implies) and isinstance(p2, Not) and formulas_equal(p1.left, p2.child):
                if isinstance(conclusion, Not) and formulas_equal(p1.right, conclusion.child):
                    return "Fallacy: denying the antecedent (P→Q, ¬P ∴ ¬Q)"

    # Invalid transitivity: P→Q, Q→R but conclusion is not P→R
    implications = [p for p in premises if isinstance(p, Implies)]
    if len(implications) >= 2:
        for imp1 in implications:
            for imp2 in implications:
                if imp1 is not imp2 and formulas_equal(imp1.right, imp2.left):
                    valid_chain = Implies(imp1.left, imp2.right)
                    if not formulas_equal(conclusion, valid_chain):
                        return "Fallacy: invalid transitivity (broken implication chain)"

    return None


# ================================================================
# 9. ARGUMENT VALIDATOR
# ================================================================

def validate_argument(steps: list[dict]) -> list[dict]:
    issues = []
    premises = []
    conclusion = None
    conclusion_index = -1

    for i, step in enumerate(steps):
        text = step["text"].strip()
        text_lower = text.lower()

        if re.search(r"\b(theorem|claim|proof|lemma)\b", text_lower):
            continue

        if re.search(r"\b(therefore|thus|hence|so)\b", text_lower):
            conclusion_index = i
            match = re.search(r"(therefore|thus|hence|so)\s+(.+)", text, re.IGNORECASE)
            if match:
                formula_text = extract_formula(match.group(2))
                conclusion = parse_formula(formula_text)
                if conclusion is None:
                    issues.append({"step_index": i, "message": "Section 3.3: Could not parse conclusion formula"})
            continue

        formula_text = extract_formula(text)
        if formula_text:
            f = parse_formula(formula_text)
            if f: premises.append(f)

    if conclusion is None:
        issues.append({"step_index": len(steps) - 1, "message": "Section 3.3: Mark conclusion with 'Therefore ...'"})
        return issues
    if not premises:
        issues.append({"step_index": 0, "message": "Section 3.3: Provide at least one premise"})
        return issues

    all_vars = set()
    for p in premises: all_vars |= get_vars(p)
    all_vars |= get_vars(conclusion)
    all_vars = sorted(all_vars)

    if len(all_vars) > 8:
        issues.append({"step_index": 0, "message": "Section 3.3: Too many variables for truth table (max 8)"})
        return issues

    counterexamples = []
    for env in all_assignments(all_vars):
        premises_true = all(eval_formula(p, env) for p in premises)
        conclusion_true = eval_formula(conclusion, env)
        if premises_true and not conclusion_true:
            counterexamples.append(env)

    if counterexamples:
        fallacy = detect_fallacy(premises, conclusion)
        if fallacy:
            issues.append({"step_index": conclusion_index, "message": f"Section 3.3: {fallacy}"})
        else:
            ce = counterexamples[0]
            ce_str = ", ".join(f"{k}={'T' if v else 'F'}" for k, v in ce.items())
            issues.append({"step_index": conclusion_index, "message": f"Section 3.3: Invalid argument. Counterexample: {ce_str}"})

    return issues


# ================================================================
# 10. EQUIVALENCE VALIDATOR
# ================================================================

def validate_equivalence(steps: list[dict]) -> list[dict]:
    issues = []
    formulas = []
    formula_indices = []

    for i, step in enumerate(steps):
        text = step["text"].strip()
        text = re.sub(r"^\d+\.\s*", "", text)
        if re.search(r"\b(theorem|claim|proof|lemma)\b", text.lower()):
            continue
        f = parse_formula(extract_formula(text))
        if f:
            formulas.append(f)
            formula_indices.append(i)

    if len(formulas) < 2:
        for i, step in enumerate(steps):
            text = step["text"].strip()
            text = re.sub(r"^\d+\.\s*", "", text)
            for splitter in [r"\bequivalent\s+to\b", r"\biff\b", r"↔", r"<->"]:
                parts = re.split(splitter, text, flags=re.IGNORECASE)
                if len(parts) == 2:
                    f1 = parse_formula(extract_formula(parts[0]))
                    f2 = parse_formula(extract_formula(parts[1]))
                    if f1 and f2:
                        formulas = [f1, f2]
                        formula_indices = [i, i]
                        break
            if len(formulas) >= 2:
                break

    if len(formulas) < 2:
        issues.append({"step_index": 0, "message": "Section 3.3: Provide two formulas to compare for equivalence"})
        return issues

    f1, f2 = formulas[0], formulas[1]
    all_vars = sorted(set(get_vars(f1)) | set(get_vars(f2)))

    if len(all_vars) > 8:
        issues.append({"step_index": 0, "message": "Section 3.3: Too many variables for truth table (max 8)"})
        return issues

    equivalent = True
    counterexample = None
    for env in all_assignments(all_vars):
        if eval_formula(f1, env) != eval_formula(f2, env):
            equivalent = False
            counterexample = env
            break

    if not equivalent:
        ce_str = ", ".join(f"{k}={'T' if v else 'F'}" for k, v in counterexample.items())
        issues.append({"step_index": formula_indices[1] if formula_indices else len(steps) - 1,
                       "message": f"Section 3.3: Formulas are not equivalent. Counterexample: {ce_str}"})

    return issues


# ================================================================
# 11. MAIN ENTRY POINT
# ================================================================

def validate(steps: list[dict]) -> dict:
    if not steps:
        return {"valid": False, "step_results": [], "overall_reason": "No steps provided", "technique": "unknown"}

    technique = classify_technique(steps)
    quality_issues = check_quality(steps)
    structural_issues = []

    if technique == "logical_argument":
        structural_issues = validate_argument(steps)
    elif technique == "equivalence_check":
        structural_issues = validate_equivalence(steps)
    elif technique == "validity_check":
        structural_issues = validate_argument(steps)

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
