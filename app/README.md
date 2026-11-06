# App

Interactive view of the AV market-expansion scoring: a ranking table with live weight sliders, an Opportunity vs. Ease of Entry 2x2, and a metro drill-down (pillar breakdown, raw metrics, competitors, regulation with sources, unit economics with assumption sliders). Built with Vite, React, TypeScript, Recharts and Tailwind.

The app reads `public/metros_scored.json`, which the pipeline writes (`python tasks.py score`, or `make score`, copies it from `data/output/`). Scores recompute in the browser from the normalized sub-scores, and a Vitest test checks that the browser's balanced-scenario scores match Python's to 2 decimals. Launch-plan waves in the 2x2 come from the balanced scenario and do not change when weights are moved.

```bash
npm install
npm run dev        # http://localhost:5173
npm run build && npm run preview     # production build
npx vitest run     # browser-vs-Python parity tests
npm run lint
node scripts/screenshots.mjs         # re-capture docs/screenshots (Playwright, uses the installed Edge or Chrome)
```

See the repository README for the recommendation and `docs/methodology.md` for the method.
