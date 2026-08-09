# engine.py — Proof It Validator Skeleton (M1)
# You write and edit this file. Kimi handles the rest.


def parse_input(raw_text: str) -> list[dict]:
    """
    Split raw text into steps.
    Return a list like: [{"number": 1, "text": "Assume P"}, ...]
    """
    steps = []
    for line in raw_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Try to pull a number off the front
        parts = line.split(".", 1)
        if len(parts) == 2 and parts[0].strip().isdigit():
            num = int(parts[0].strip())
            text = parts[1].strip()
        else:
            num = len(steps) + 1
            text = line
        steps.append({"number": num, "text": text})
    return steps


def validate(steps: list[dict]) -> dict:
    """
    M1: Skeleton rule.
    Returns: {
        "valid": bool,
        "step_results": [{"number": int, "ok": bool, "reason": str}, ...],
        "overall_reason": str
    }
    """
    step_results = []
    all_ok = True

    for i, step in enumerate(steps):
        ok = True
        reason = "OK"

        if not step["text"]:
            ok = False
            reason = "Step is empty"
            all_ok = False

        # M1 extra rule: numbers must be sequential starting from 1
        expected_num = i + 1
        if step["number"] != expected_num:
            ok = False
            reason = f"Expected step {expected_num}, got {step['number']}"
            all_ok = False

        step_results.append({
            "number": step["number"],
            "ok": ok,
            "reason": reason
        })

    return {
        "valid": all_ok,
        "step_results": step_results,
        "overall_reason": "All steps valid" if all_ok else "Some steps failed"
    }
