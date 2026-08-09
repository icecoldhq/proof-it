# Proof It — M1 Validator Skeleton

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:4321

## What You Edit

- `public/engine.py` — The Python validator. **This is your file.**
- `src/styles/global.css` — Colors and layout (if you want to tweak visuals).

## How It Works

1. Type proof steps in the text box.
2. Click **Check Proof**.
3. Pyodide (Python in the browser) loads `engine.py` and runs your `parse_input` and `validate` functions.
4. Results appear in the panel below.

## Deploy to Cloudflare Pages

```bash
npm run build
```

Upload the `dist/` folder to Cloudflare Pages.

## M1 Rules (in engine.py)

- Steps must not be empty.
- Step numbers must be sequential (1, 2, 3...).

## Next: M2

When M1 works, you will add a new Python module for propositional logic. Kimi will show you exactly where to plug it in.
