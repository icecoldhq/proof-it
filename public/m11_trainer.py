# m11_trainer.py — Proof It Trainer (M11)
# Generates flawed or valid arguments for the user to spot.
# Uses whichever modules are loaded.

import random
import json


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


# --- Proof templates by chapter ---
TRAINING_BANK = {
    "induction": [
        {
            "name": "Ordinary induction — valid",
            "steps": [
                "Base case: P(0) is true.",
                "Inductive hypothesis: Assume P(n).",
                "Inductive step: Prove P(n+1).",
                "Therefore P(n) for all n by induction."
            ],
            "flawed": False,
            "explanation": "Canonical ordinary induction structure."
        },
        {
            "name": "Strong induction with ordinary IH — flawed",
            "steps": [
                "Base case: P(0).",
                "Assume P(n).",
                "Prove P(n+1) by strong induction.",
                "QED."
            ],
            "flawed": True,
            "explanation": "Claims strong induction but only assumes P(n), not P(k) for all k ≤ n."
        },
        {
            "name": "Missing base case — flawed",
            "steps": [
                "Assume P(n).",
                "Prove P(n+1).",
                "Therefore P(n) for all n."
            ],
            "flawed": True,
            "explanation": "Missing base case. Induction requires P(0) verified."
        }
    ],
    "state_machines": [
        {
            "name": "Invariant preserved — valid",
            "steps": [
                "States: (x,y) where x,y are nonnegative integers.",
                "Transitions: (x,y) -> (x-1,y) if x > 0.",
                "Invariant: x + y >= 0.",
                "Check invariant preserved."
            ],
            "flawed": False,
            "explanation": "Invariant holds under all transitions."
        },
        {
            "name": "Invariant broken — flawed",
            "steps": [
                "States: (x,y) where x,y are nonnegative integers.",
                "Transitions: (x,y) -> (x-1,y) if x > 0.",
                "Transitions: (x,y) -> (x,y-1) if y > 0.",
                "Invariant: x + y > 0.",
                "Check invariant preserved."
            ],
            "flawed": True,
            "explanation": "Transition from (1,0) to (0,0) or (0,1) to (0,0) breaks x + y > 0."
        }
    ],
    "infinite_sets": [
        {
            "name": "Diagonalization — valid",
            "steps": [
                "Assume the reals in [0,1] can be enumerated.",
                "List them as r1, r2, r3, ...",
                "Construct d where the nth digit of d differs from the nth digit of rn.",
                "Then d is not in the list, a contradiction.",
                "Therefore the reals are uncountable."
            ],
            "flawed": False,
            "explanation": "Canonical Cantor diagonalization."
        },
        {
            "name": "Missing construction — flawed",
            "steps": [
                "Assume the reals can be enumerated.",
                "Contradiction.",
                "Therefore the reals are uncountable."
            ],
            "flawed": True,
            "explanation": "Missing the construction of the diagonal element d."
        }
    ],
    "reasoning": [
        {
            "name": "Valid syllogism",
            "steps": [
                "All humans are mortal.",
                "Socrates is human.",
                "Therefore Socrates is mortal."
            ],
            "flawed": False,
            "explanation": "Valid modus ponens structure."
        },
        {
            "name": "Affirming the consequent",
            "steps": [
                "If it rained, the ground is wet.",
                "The ground is wet.",
                "Therefore it rained."
            ],
            "flawed": True,
            "explanation": "Affirming the consequent. The ground could be wet from a sprinkler."
        },
        {
            "name": "Slippery slope",
            "steps": [
                "If we allow one retake, students will demand infinite retakes.",
                "Therefore we must ban all retakes."
            ],
            "flawed": True,
            "explanation": "Slippery slope. No evidence that one retake causes infinite demands."
        }
    ]
}


def generate_proof(category: str | None = None, difficulty: str = "mixed") -> dict:
    """Generate a random proof from the training bank."""
    if category is None or category not in TRAINING_BANK:
        category = random.choice(list(TRAINING_BANK.keys()))
    
    bank = TRAINING_BANK[category]
    
    if difficulty == "flawed":
        candidates = [p for p in bank if p["flawed"]]
    elif difficulty == "valid":
        candidates = [p for p in bank if not p["flawed"]]
    else:
        candidates = bank
    
    proof = random.choice(candidates)
    return {
        "category": category,
        "name": proof["name"],
        "steps": [{"number": i+1, "text": s} for i, s in enumerate(proof["steps"])],
        "flawed": proof["flawed"],
        "explanation": proof["explanation"]
    }


def validate(steps: list[dict]) -> dict:
    """
    Trainer mode: expects user input to be either:
    - "generate [category] [difficulty]" to get a new proof
    - "check [answer]" to validate the user's analysis
    - Or just proof steps to be validated
    """
    if not steps:
        return {
            "valid": False,
            "step_results": [],
            "overall_reason": "Trainer: type 'generate' to get a proof, or paste proof steps to analyze.",
            "technique": "trainer"
        }
    
    first_text = steps[0]["text"].lower()
    
    # Generate command
    if first_text.startswith("generate"):
        parts = first_text.split()
        category = parts[1] if len(parts) > 1 else None
        difficulty = parts[2] if len(parts) > 2 else "mixed"
        
        if category and category not in TRAINING_BANK:
            available = ", ".join(TRAINING_BANK.keys())
            return {
                "valid": False,
                "step_results": [],
                "overall_reason": f"Unknown category '{category}'. Available: {available}.",
                "technique": "trainer"
            }
        
        proof = generate_proof(category, difficulty)
        step_results = [{"number": s["number"], "ok": True, "reason": "OK"} for s in proof["steps"]]
        
        return {
            "valid": True,
            "step_results": step_results,
            "overall_reason": (
                f"**{proof['name']}** ({proof['category']})\\n"
                f"Flawed: {proof['flawed']}\\n"
                f"Analyze this proof. What is wrong with it (if anything)?\\n"
                f"Type your analysis, then click Check to reveal the answer."
            ),
            "technique": "trainer",
            "trainer_data": json.dumps({
                "flawed": proof["flawed"],
                "explanation": proof["explanation"],
                "name": proof["name"]
            })
        }
    
    # Check/reveal command
    if first_text.startswith("check") or first_text.startswith("reveal"):
        # Look for trainer_data in the input (not ideal, but PyScript bridge can pass it)
        # For now, just tell the user to look at the previous result
        return {
            "valid": True,
            "step_results": [],
            "overall_reason": "To reveal the answer, the trainer stores the explanation in the result. In the full implementation, this would display the explanation.",
            "technique": "trainer"
        }
    
    # Default: validate as normal proof steps
    # In trainer mode, we just echo back for analysis
    step_results = [{"number": s["number"], "ok": True, "reason": "OK"} for s in steps]
    
    return {
        "valid": True,
        "step_results": step_results,
        "overall_reason": "Trainer received proof steps. Type 'generate' to get a training proof, or analyze these steps yourself.",
        "technique": "trainer"
    }
