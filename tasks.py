"""Cross-platform task runner: the same steps as the Makefile, for machines without `make`.

Usage: python tasks.py <task> [<task> ...]     e.g. python tasks.py all     python tasks.py data score
Tasks: data, score, analyze, publish-json, dbt, test, memo, deck, app, all
"""
import pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
PY = str(VENV / ("python.exe" if sys.platform == "win32" else "python")) if VENV.exists() else sys.executable
_dbt = VENV / ("dbt.exe" if sys.platform == "win32" else "dbt")
DBT = str(_dbt) if _dbt.exists() else (shutil.which("dbt") or "dbt")
SHELL_NPM = sys.platform == "win32"      # npm is npm.cmd on Windows


def run(*cmd, cwd=ROOT, shell=False):
    print("+", " ".join(map(str, cmd)), flush=True)
    r = subprocess.run([str(c) for c in cmd] if not shell else " ".join(map(str, cmd)), cwd=cwd, shell=shell)
    if r.returncode:
        sys.exit(f"FAILED (exit {r.returncode}): {' '.join(map(str, cmd))}")


def data():
    for s in ["acs", "gazetteer", "faa", "weather", "nhtsa", "eia", "seed"]:
        run(PY, f"pipeline/ingest_{s}.py")


def analyze():
    for s in ["demand", "unit_economics", "monte_carlo", "enrich"]:
        run(PY, f"analysis/{s}.py")


def publish_json():
    shutil.copy(ROOT / "data/output/metros_scored.json", ROOT / "app/public/metros_scored.json")
    shutil.copy(ROOT / "docs/methodology.md", ROOT / "app/public/methodology.md")
    print("published metros_scored.json and methodology.md to app/public", flush=True)


def score():
    run(PY, "pipeline/build_features.py")
    run(PY, "pipeline/score.py")
    analyze()
    publish_json()


def dbt():
    run(PY, "pipeline/export_dbt_inputs.py")
    run(DBT, "build", "--profiles-dir", ".", cwd=ROOT / "dbt")
    run(PY, "pipeline/parity_dbt.py")


def test():
    run(PY, "-m", "pytest", "-q")
    run("npx", "vitest", "run", cwd=ROOT / "app", shell=SHELL_NPM)


def memo():
    run(PY, "reports/make_memo.py")


def deck():
    run(PY, "reports/make_deck.py")


def app():
    run("npm", "install", cwd=ROOT / "app", shell=SHELL_NPM)
    run("npm", "run", "dev", cwd=ROOT / "app", shell=SHELL_NPM)


def all_():
    for t in (data, score, dbt, test, memo, deck):
        t()


TASKS = {"data": data, "score": score, "analyze": analyze, "publish-json": publish_json, "dbt": dbt,
         "test": test, "memo": memo, "deck": deck, "app": app, "all": all_}

if __name__ == "__main__":
    names = sys.argv[1:]
    if not names or any(n not in TASKS for n in names):
        sys.exit(__doc__)
    for n in names:
        TASKS[n]()
