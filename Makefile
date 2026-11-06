PY ?= .venv/Scripts/python
.PHONY: data score app memo deck all test publish-json
data:
	$(PY) pipeline/ingest_acs.py && $(PY) pipeline/ingest_gazetteer.py && $(PY) pipeline/ingest_faa.py && \
	$(PY) pipeline/ingest_weather.py && $(PY) pipeline/ingest_nhtsa.py && $(PY) pipeline/ingest_eia.py && $(PY) pipeline/ingest_seed.py
score:
	$(PY) pipeline/build_features.py && $(PY) pipeline/score.py && $(MAKE) publish-json
publish-json:
	cp data/output/metros_scored.json app/public/metros_scored.json && cp docs/methodology.md app/public/methodology.md
test:
	$(PY) -m pytest -q && cd app && npx vitest run
app:
	cd app && npm install && npm run dev
memo:
	$(PY) reports/make_memo.py
deck:
	$(PY) reports/make_deck.py
all: data score test memo deck
