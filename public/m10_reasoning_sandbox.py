# m10_reasoning_sandbox.py — Proof It Reasoning Sandbox (M10)
# General validity checker for informal arguments.
# Catches fallacies, thinking traps, and suggests mental models.

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


# --- Cross-argument fallacy detection (looks at full text) ---
def _detect_cross_fallacies(full_text: str, steps: list[dict]) -> list[dict]:
    """Detect fallacies that require looking across multiple steps."""
    found = []
    t = full_text.lower()

    # Affirming the Consequent: If P then Q. Q. Therefore P.
    # Heuristic: "if" appears, "therefore" appears, and there are 3+ steps.
    # This is loose but catches the canonical form.
    has_if = 'if' in t
    has_therefore = 'therefore' in t
    has_so = re.search(r'\bso\s+\w+', t) is not None
    
    if has_if and (has_therefore or has_so) and len(steps) >= 3:
        # Check if the structure looks like: conditional + fact + conclusion
        # Look for patterns like "if [X], [Y]" then later "[Y]" then "therefore [X]"
        found.append({
            "name": "Affirming the Consequent",
            "description": "If P then Q. Q. Therefore P. — Invalid. The consequent does not imply the antecedent.",
            "example": "If it rained, the ground is wet. The ground is wet. Therefore it rained.",
            "mental_model": "Inversion Principle — what else could cause Q?"
        })

    # False Dichotomy
    if re.search(r'\b(either\s+\w+.*?\bor\s+\w+)', t):
        found.append({
            "name": "False Dichotomy",
            "description": "Presenting only two options when more may exist.",
            "example": "Either we cut taxes or the economy collapses.",
            "mental_model": "Multi-Dimensional Thinking — what other options exist?"
        })

    # Slippery Slope: if X, then Y (escalation)
    if (re.search(r'\bif\b', t) and 
        re.search(r'\b(will|would|demand|force|require|lead|inevitably|cascade|snowball)\b', t)):
        found.append({
            "name": "Slippery Slope",
            "description": "Assuming one step leads inevitably to extreme consequences without evidence.",
            "example": "If we allow one retake, students will demand infinite retakes.",
            "mental_model": "Second-Order Thinking — at what point does the chain actually break?"
        })

    # Circular Reasoning
    if re.search(r'\b(because|since)\b.*?\b(true|correct|valid|obvious|proven)\b.*?\b(because|since)\b', t):
        found.append({
            "name": "Circular Reasoning",
            "description": "The conclusion is assumed in the premise.",
            "example": "The Bible is true because God wrote it. We know God wrote it because the Bible says so.",
            "mental_model": "First Principles — what is the independent foundation?"
        })

    return found


# --- Per-step fallacy detection ---
def _detect_step_fallacies(text: str) -> list[dict]:
    """Detect fallacies visible within a single step."""
    found = []
    t = text.lower()

    # Ad Hominem
    if re.search(r'\b(you\'?re?|he\'?s?|she\'?s?|they\'?re?)\b.*?\b(stupid|lazy|biased|corrupt|liar|hypocrite|incompetent|evil|dumb|idiot|moron)', t):
        found.append({
            "name": "Ad Hominem",
            "description": "Attacking the person instead of the argument.",
            "example": "You can't trust his data because he drives a gas car.",
            "mental_model": "Author-Blind Merit — evaluate the claim, not the source."
        })

    # Appeal to Authority
    if re.search(r'\b(expert|scientist|doctor|study|research|paper|report|professor|official)\b.*?\b(says?|said|shows?|proves?|confirms?|claims?)\b', t):
        found.append({
            "name": "Appeal to Authority",
            "description": "Accepting a claim solely because an authority stated it.",
            "example": "This diet works because a celebrity endorses it.",
            "mental_model": "Hypothesis Thinking — what is the actual evidence?"
        })

    # Hasty Generalization
    if re.search(r'\b(all|every|always|never|none|no\s+one)\b', t) and re.search(r'\b(only|just|few|couple|some|my|I\s+saw|I\s+know|one\s+time)\b', t):
        found.append({
            "name": "Hasty Generalization",
            "description": "Drawing a broad conclusion from insufficient evidence.",
            "example": "My two friends failed, so the professor is unfair to everyone.",
            "mental_model": "Normal Distribution — is this a trend or an outlier?"
        })

    # Post Hoc
    if re.search(r'\b(after|since|ever\s+since)\b.*?\b(happened|occurred|started|began|came|went)\b.*?\b(therefore|so|caused|must\s+have|proves?)\b', t):
        found.append({
            "name": "Post Hoc Ergo Propter Hoc",
            "description": "Assuming that because B followed A, A caused B.",
            "example": "I wore lucky socks and we won. The socks caused the win.",
            "mental_model": "First Principles — what is the actual causal mechanism?"
        })

    # Strawman
    if re.search(r'\b(so\s+you\'?re?\s+saying|so\s+you\s+think|basically\s+you|what\s+you\'?re?\s+really\s+saying|you\s+really\s+mean)\b', t):
        found.append({
            "name": "Strawman Fallacy",
            "description": "Misrepresenting someone's argument to make it easier to attack.",
            "example": "So you think we should just let criminals roam free?",
            "mental_model": "Articulation — restate their argument in their own terms."
        })

    # Confirmation Bias
    if re.search(r'\b(of\s+course|obviously|as\s+expected|just\s+like\s+I\s+thought|this\s+proves\s+what\s+I\s+already|confirms\s+my)\b', t):
        found.append({
            "name": "Confirmation Bias",
            "description": "Seeking only evidence that confirms pre-existing beliefs.",
            "example": "I knew he was guilty, and this ambiguous email proves it.",
            "mental_model": "Inversion Principle — what evidence would prove me wrong?"
        })

    # Sunk Cost
    if re.search(r'\b(already|we\'?ve?|I\'?ve?|so\s+much|too\s+much|can\'?t\s+quit|can\'?t\s+stop|invested|spent|put\s+in)\b.*?\b(therefore|so|must|have\s+to|should|need\s+to)\b', t):
        found.append({
            "name": "Sunk Cost Fallacy",
            "description": "Continuing because of past investment, not future value.",
            "example": "We've already spent $1M on this project, so we can't cancel it.",
            "mental_model": "Opportunity Cost — what is the best alternative use of resources now?"
        })

    # Appeal to Emotion
    if re.search(r'\b(think\s+of\s+the|how\s+could\s+you|heartless|cruel|unfair|disgusting|outrageous|shameful|devastating|tragic|horrific)\b', t):
        found.append({
            "name": "Appeal to Emotion",
            "description": "Manipulating emotions instead of presenting evidence.",
            "example": "Think of the children! We must ban this immediately.",
            "mental_model": "Author-Blind Merit — strip the emotional framing, what is the claim?"
        })

    # The Frozen Premise
    if re.search(r'\b(always|never|everyone|no\s+one|impossible|certainly|definitely|absolutely)\b.*?\b(because|since|it\s+follows|we\s+know)\b', t):
        found.append({
            "name": "The Frozen Premise",
            "description": "Treating a variable property as fixed while your reasoning changes it.",
            "example": "I proved there is no surprise quiz, so I stopped expecting it. Then the quiz surprised me.",
            "mental_model": "Second-Order Thinking — if I believe this, how does that belief change the situation?"
        })

    return found


def _map_to_thinking_traps(fallacies: list[dict]) -> list[str]:
    """Map detected fallacies to thinking trap names."""
    traps = []
    mapping = {
        "affirming the consequent": "End point trap (reverse implication)",
        "denying the antecedent": "End point trap (reverse implication)",
        "false dichotomy": "False Dichotomy",
        "slippery slope": "Slippery Slope",
        "ad hominem": "Ad Hominem",
        "appeal to authority": "Appeal to Authority",
        "hasty generalization": "Hasty Generalization",
        "post hoc": "Post Hoc Fallacy",
        "strawman": "Strawman Fallacy",
        "the frozen premise": "The Frozen Premise",
        "confirmation bias": "Confirmation Bias",
        "sunk cost": "Sunk Cost Fallacy",
        "circular reasoning": "End point trap (reverse implication)",
        "appeal to emotion": "Appeal to Authority",
    }
    for f in fallacies:
        name = f["name"].lower()
        for key, trap in mapping.items():
            if key in name and trap not in traps:
                traps.append(trap)
    return traps


def validate(steps: list[dict]) -> dict:
    """
    Validate informal arguments for fallacies and thinking traps.
    Suggests mental models.
    """
    if not steps:
        return {
            "valid": False,
            "step_results": [],
            "overall_reason": "No argument steps provided.",
            "technique": "reasoning_sandbox"
        }

    full_text = " ".join([s["text"] for s in steps])
    cross_fallacies = _detect_cross_fallacies(full_text, steps)

    step_results = []
    all_fallacies = list(cross_fallacies)
    all_traps = _map_to_thinking_traps(cross_fallacies)

    for step in steps:
        text = step["text"]
        step_fallacies = _detect_step_fallacies(text)
        step_traps = _map_to_thinking_traps(step_fallacies)
        suggestions = list(set([f["mental_model"] for f in step_fallacies]))

        all_fallacies.extend(step_fallacies)
        all_traps.extend(step_traps)

        ok = len(step_fallacies) == 0 and len(cross_fallacies) == 0
        reasons = []
        if step_fallacies:
            reasons.append("Fallacies: " + ", ".join([f["name"] for f in step_fallacies]))
        if step_traps:
            reasons.append("Traps: " + ", ".join(step_traps))
        if suggestions:
            reasons.append("Try: " + "; ".join(suggestions))

        step_results.append({
            "number": step["number"],
            "ok": ok,
            "reason": " | ".join(reasons) if reasons else "OK"
        })

    # Deduplicate
    all_fallacies = list({f["name"]: f for f in all_fallacies}.values())
    all_traps = list(set(all_traps))

    if all_fallacies:
        overall = (
            f"Detected {len(all_fallacies)} fallacy type(s): {', '.join([f['name'] for f in all_fallacies])}. "
            f"Thinking traps: {', '.join(all_traps) if all_traps else 'None'}. "
        )
        valid = False
    else:
        overall = "No common fallacies detected. Argument appears structurally sound."
        valid = True

    return {
        "valid": valid,
        "step_results": step_results,
        "overall_reason": overall,
        "technique": "reasoning_sandbox"
    }
