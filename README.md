> **AI Collaboration Notice:** This project was built using an augmented
> collaboration model. The human author owns all proof logic, mathematical
> reasoning, and rule modules. The AI assistant (Kimi by Moonshot AI)
> contributed the Astro scaffolding, PyScript integration, UI components,
> and deployment configuration. See `NOTICE` for the full disclosure.

---

# Proof It

A client-side proof validator for discrete mathematics. Built with Astro, PyScript/WASM, and Python. No backend required — everything runs in your browser.

Link (Cloudflare): https://proof-it.icecoldhq.workers.dev/

## What it does

Proof It checks the structural correctness of mathematical proofs across 8 chapters of discrete math, plus a general reasoning sandbox and a training mode.

| Mode | What it checks |
|---|---|
| M1 | Syntax and step numbering |
| M2 | Proof techniques (implication, iff, cases, contradiction) |
| M3 | Well-Ordering Principle structure |
| M4 | Logical formulas (AND/OR/NOT/implies/equivalence) |
| M5 | Mathematical data types (sets, functions, relations) |
| M6 | Induction (ordinary vs. strong, base case, IH, inductive step) |
| M7 | State machines (invariant preservation, termination via derived variables) |
| M8 | Recursive data types (structural induction) |
| M9 | Infinite sets (diagonalization, countability, cardinality fallacies) |
| M10 | Reasoning Sandbox — informal fallacies and thinking traps |
| M11 | Trainer — generate flawed or valid proofs to spot errors |

## How to use

1. Pick a mode from the dropdown.
2. Type your proof steps (one per line, numbered).
3. Click **Check Proof**.
4. The validator tells you what is missing, out of order, or structurally wrong.

### Trainer mode

1. Select **Mode 11: Trainer**.
2. Type `generate [category] [difficulty]` (e.g., `generate induction mixed`).
3. Analyze the proof yourself.
4. Type `reveal` to see the answer.

## Tech stack

- **Astro** — static site shell
- **PyScript / Pyodide (WASM)** — Python engine running client-side
- **KaTeX** — math rendering
- **localStorage** — theme persistence
- **Cloudflare Pages** — deployment target

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Deploy

```bash
npm run deploy
```

Or connect the GitHub repo to Cloudflare Pages for auto-deploy on push.

## License

MIT. See `LICENSE`.
