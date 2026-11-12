"""Web interface for the Self-Aware Game.

- app.py         FastAPI app: front end in static/, JSON API under /api (STATIC_ENDPOINTS exported for GitHub Pages)
- sim_record.py  runs the real desktop game headlessly (seeded) and records its state; also the text libraries
- static/        ES-module front end; sim_*.js is the JavaScript port of the game, node-tested against sim_record runs
"""
