# m7_ch6_state_machines.py — Proof It State Machine Validator (M7)
# Checks preserved invariants and derived-variable termination.
# Finds the specific transition that breaks the claim.

import re
import itertools


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


def _safe_eval(expr: str, env: dict):
    """Evaluate a math expression in a restricted environment."""
    allowed = {"__builtins__": {}}
    allowed.update(env)
    return eval(expr, allowed)


def _strip_punct(s: str) -> str:
    """Strip trailing sentence punctuation."""
    return s.rstrip('.;:,').strip()


def _classify_step(text: str) -> str:
    """Classify a step into a state-machine component."""
    t = text.lower()

    # --- Check commands (must be checked BEFORE generic patterns) ---
    if re.search(r'\bcheck\b.*\b(preserved|preservation)\b', t):
        return "CHECK_PRESERVED"
    if re.search(r'\bcheck\b.*\b(decreasing|termination|terminate)\b', t):
        return "CHECK_TERMINATION"

    # --- Explicit structural labels ---
    if re.search(r'\bbase\s+(case|step|basis)\b', t):
        return "BASE_CASE"
    if re.search(r'\bconclusion\b', t):
        return "CONCLUSION"
    if re.search(r'\bstart\b', t):
        return "START"
    if re.search(r'\btransition', t):
        return "TRANSITION"
    if re.search(r'\bderived\s+variable\b', t):
        return "DERIVED_VAR"
    if re.search(r'\binvariant\b', t):
        return "INVARIANT"
    if re.search(r'\bstates?\b', t) and not re.search(r'\b(check|verify|prove)\b', t):
        return "STATES"

    # --- Conclusion by content ---
    if re.search(r'\btherefore\b|\bterminates\b|\bstable\b|\bqed\b|∎', t):
        return "CONCLUSION"

    return "OTHER"


def _parse_states(text: str) -> dict:
    """Extract state variables and constraints."""
    vars = []
    constraints = {}

    # Tuple: (x, y) where ...
    m = re.search(r'\(\s*([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*)\s*\)', text)
    if m:
        vars = [v.strip() for v in m.group(1).split(',')]
    else:
        # Single: n in N
        m = re.search(r'\b([a-zA-Z_]\w*)\s+(?:in|is|are)\b', text.lower())
        if m:
            vars = [m.group(1)]

    t = text.lower()
    for v in vars:
        if 'nonnegative' in t or 'natural' in t or 'naturals' in t or ' in n' in t:
            constraints[v] = ('>=', 0)
        elif 'positive' in t:
            constraints[v] = ('>', 0)

    return {'vars': vars, 'constraints': constraints}


def _parse_transition(text: str) -> dict | None:
    """Parse a transition rule into src vars, tgt expressions, and guard."""
    # Remove common label prefixes
    t = re.sub(r'^.*?transition\s*[:\-]?\s*', '', text, flags=re.I).strip()

    # Tuple format: (x,y) -> (x-1,y) if x > 0
    m = re.search(r'\(\s*([^)]+)\s*\)\s*->\s*\(\s*([^)]+)\s*\)(?:\s+(?:if|for)\b\s*(.+))?', t)
    if m:
        src = [v.strip() for v in m.group(1).split(',')]
        tgt = [e.strip() for e in m.group(2).split(',')]
        guard = _strip_punct(m.group(3)) if m.group(3) else "True"
        # Normalize multiple conditions into 'and'
        guard = re.sub(r'\s+(?:if|for)\b\s+', ' and ', guard)
        return {'src': src, 'tgt': tgt, 'guard': guard}

    # Single format: n -> n-1 if n > 0
    m = re.search(r'\b([a-zA-Z_]\w*)\s*->\s*(.+?)(?:\s+(?:if|for)\b\s*(.*))?$', t)
    if m:
        src = [m.group(1).strip()]
        tgt = [_strip_punct(m.group(2))]
        guard = _strip_punct(m.group(3)) if m.group(3) else "True"
        guard = re.sub(r'\s+(?:if|for)\b\s+', ' and ', guard)
        return {'src': src, 'tgt': tgt, 'guard': guard}

    return None


def _parse_invariant(text: str) -> str:
    """Strip label and return the invariant expression."""
    t = re.sub(r'^.*?invariant\s*([A-Z]\s*\([^)]*\)\s*=\s*)?', '', text, flags=re.I)
    return _strip_punct(t)


def _parse_derived(text: str) -> str:
    """Strip label and return the derived-variable expression."""
    # name(...) = expr
    t = re.sub(r'^.*?derived\s+variable\s*[a-zA-Z_]\w*\s*\([^)]*\)\s*=\s*', '', text, flags=re.I)
    # name = expr
    t = re.sub(r'^.*?derived\s+variable\s*[a-zA-Z_]\w*\s*=\s*', '', t, flags=re.I)
    # plain: Derived variable: expr
    t = re.sub(r'^.*?derived\s+variable\s*[:\-]?\s*', '', t, flags=re.I)
    return _strip_punct(t)


def _trans_vars(trans: dict, states_info: dict) -> list[str]:
    """All variables mentioned in this transition."""
    all_vars = set(states_info['vars'])
    all_vars.update(re.findall(r'\b[a-zA-Z_]\w*\b', trans['guard']))
    for expr in trans['tgt']:
        all_vars.update(re.findall(r'\b[a-zA-Z_]\w*\b', expr))
    return list(all_vars)


def _samples(vars_list: list[str], constraints: dict, max_val: int = 4):
    """Generate small sample assignments for the given variables."""
    ranges = []
    for v in vars_list:
        if v in constraints:
            op, val = constraints[v]
            if op == '>=':
                ranges.append(range(val, val + max_val + 1))
            elif op == '>':
                ranges.append(range(val + 1, val + max_val + 2))
            else:
                ranges.append(range(0, max_val + 1))
        else:
            ranges.append(range(0, max_val + 1))

    for vals in itertools.product(*ranges):
        env = dict(zip(vars_list, vals))
        ok = True
        for v, (op, val) in constraints.items():
            if v not in env:
                continue
            if op == '>=' and env[v] < val:
                ok = False
            elif op == '>' and env[v] <= val:
                ok = False
        if ok:
            yield env


def _check_preservation(states_info: dict, transitions: list, invariant: str):
    """Return (ok, reason, fail_transition_index, counterexample)."""
    for ti, trans in enumerate(transitions):
        tvars = _trans_vars(trans, states_info)
        for env in _samples(tvars, states_info['constraints']):
            try:
                guard_val = _safe_eval(trans['guard'], env)
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: guard syntax error ({e}). "
                    f"Guard was: '{trans['guard']}'"
                ), ti, None

            if not guard_val:
                continue

            try:
                if not _safe_eval(invariant, env):
                    continue
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: invariant syntax error in pre-state ({e}). "
                    f"Invariant was: '{invariant}'"
                ), ti, None

            # Compute post-state
            post = dict(env)
            for i, expr in enumerate(trans['tgt']):
                if i < len(trans['src']):
                    var = trans['src'][i]
                    try:
                        post[var] = _safe_eval(expr, env)
                    except Exception as e:
                        return False, (
                            f"Transition {ti+1}: target expression syntax error ({e}). "
                            f"Expression was: '{expr}'"
                        ), ti, None

            try:
                if not _safe_eval(invariant, post):
                    return False, (
                        f"Transition {ti+1} breaks the invariant. "
                        f"Counterexample: pre-state {env} -> post-state {post}"
                    ), ti, (env, post)
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: invariant syntax error in post-state ({e}). "
                    f"Invariant was: '{invariant}'"
                ), ti, (env, post)

    return True, "Invariant is preserved under every transition.", None, None


def _check_termination(states_info: dict, transitions: list, derived_expr: str, strict: bool = True):
    """Return (ok, reason, fail_transition_index, counterexample)."""
    for ti, trans in enumerate(transitions):
        tvars = _trans_vars(trans, states_info)
        for env in _samples(tvars, states_info['constraints']):
            try:
                guard_val = _safe_eval(trans['guard'], env)
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: guard syntax error ({e}). "
                    f"Guard was: '{trans['guard']}'"
                ), ti, None

            if not guard_val:
                continue

            try:
                pre_val = _safe_eval(derived_expr, env)
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: derived variable syntax error in pre-state ({e}). "
                    f"Expression was: '{derived_expr}'"
                ), ti, None

            post = dict(env)
            for i, expr in enumerate(trans['tgt']):
                if i < len(trans['src']):
                    var = trans['src'][i]
                    try:
                        post[var] = _safe_eval(expr, env)
                    except Exception as e:
                        return False, (
                            f"Transition {ti+1}: target expression syntax error ({e}). "
                            f"Expression was: '{expr}'"
                        ), ti, None

            try:
                post_val = _safe_eval(derived_expr, post)
            except Exception as e:
                return False, (
                    f"Transition {ti+1}: derived variable syntax error in post-state ({e}). "
                    f"Expression was: '{derived_expr}'"
                ), ti, None

            if strict:
                if not (post_val < pre_val):
                    return False, (
                        f"Transition {ti+1} does NOT strictly decrease the derived variable. "
                        f"Counterexample: pre-state {env} (value {pre_val}) -> post-state {post} (value {post_val})"
                    ), ti, (env, post)
            else:
                if not (post_val <= pre_val):
                    return False, (
                        f"Transition {ti+1} does NOT weakly decrease the derived variable. "
                        f"Counterexample: pre-state {env} (value {pre_val}) -> post-state {post} (value {post_val})"
                    ), ti, (env, post)

    kind = "strictly" if strict else "weakly"
    return True, f"Derived variable {kind} decreases under every transition.", None, None


def validate(steps: list[dict]) -> dict:
    """
    Validate state-machine structure, invariant preservation, and termination.
    """
    states_info = None
    transitions = []
    trans_step_indices = []
    invariant = None
    derived = None
    check_preserved = False
    check_termination = False
    strict = True

    for i, step in enumerate(steps):
        text = step['text']
        cls = _classify_step(text)

        if cls == "STATES":
            states_info = _parse_states(text)
        elif cls == "TRANSITION":
            t = _parse_transition(text)
            if t:
                transitions.append(t)
                trans_step_indices.append(i)
        elif cls == "INVARIANT":
            invariant = _parse_invariant(text)
        elif cls == "DERIVED_VAR":
            derived = _parse_derived(text)
        elif cls == "CHECK_PRESERVED":
            check_preserved = True
        elif cls == "CHECK_TERMINATION":
            check_termination = True
            if 'weakly' in text.lower():
                strict = False

    # Per-step results
    step_results = []
    for step in steps:
        step_results.append({"number": step["number"], "ok": True, "reason": "OK"})

    all_ok = True
    messages = []

    # Structural checks
    if not states_info:
        all_ok = False
        messages.append("Missing state definition.")
    if not transitions:
        all_ok = False
        messages.append("Missing transitions.")

    # Invariant preservation
    if check_preserved:
        if not invariant:
            all_ok = False
            messages.append("Preservation check requested but no invariant defined.")
        elif states_info and transitions:
            ok, reason, fail_ti, cx = _check_preservation(states_info, transitions, invariant)
            if not ok:
                all_ok = False
                messages.append(reason)
                if fail_ti is not None:
                    si = trans_step_indices[fail_ti]
                    step_results[si]["ok"] = False
                    if cx:
                        step_results[si]["reason"] = f"Breaks invariant: {cx[0]} -> {cx[1]}"
                    else:
                        step_results[si]["reason"] = reason
            else:
                messages.append(reason)

    # Termination via derived variable
    if check_termination:
        if not derived:
            all_ok = False
            messages.append("Termination check requested but no derived variable defined.")
        elif states_info and transitions:
            ok, reason, fail_ti, cx = _check_termination(states_info, transitions, derived, strict)
            if not ok:
                all_ok = False
                messages.append(reason)
                if fail_ti is not None:
                    si = trans_step_indices[fail_ti]
                    step_results[si]["ok"] = False
                    if cx:
                        step_results[si]["reason"] = f"Does not decrease: {cx[0]} -> {cx[1]}"
                    else:
                        step_results[si]["reason"] = reason
            else:
                messages.append(reason)

    overall = " ".join(messages) if messages else "State machine checks complete."

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": overall,
        "technique": "state_machine"
    }
