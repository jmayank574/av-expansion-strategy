PY ?= .venv/Scripts/python
.PHONY: data score app memo deck all test
data:
	$(PY) pipeline/ingest_acs.py && $(PY) pipeline/ingest_gazetteer.py && $(PY) pipeline/ingest_faa.py && \
	$(PY) pipeline/ingest_weather.py && $(PY) pipeline/ingest_nhtsa.py && $(PY) pipeline/ingest_eia.py
score:
	$(PY) pipeline/build_features.py && $(PY) pipeline/score.py
app:
	cd app && npm install && npm run dev
memo:
	$(PY) reports/make_memo.py
deck:
	$(PY) reports/make_deck.py
test:
	$(PY) -m pytest
all: data score test memo deck
