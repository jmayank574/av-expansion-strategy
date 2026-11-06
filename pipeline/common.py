import pathlib, yaml, pandas as pd, os
ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, INTERIM, PROFILES = ROOT/"data/raw", ROOT/"data/interim", ROOT/"data/profiles"
for p in (RAW, INTERIM, PROFILES): p.mkdir(parents=True, exist_ok=True)

def load_metros():
    return pd.DataFrame(yaml.safe_load(open(ROOT/"config/metros.yaml"))["metros"])

def env(key):
    f = ROOT/".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if line.startswith(key+"="): return line.split("=",1)[1].strip()
    return os.environ.get(key)

def write_profile(name, df, checks, extra=""):
    """checks: list of (description, bool). Writes data/profiles/<name>.md and returns True if all pass."""
    L = [f"# Profile: {name}", f"rows: {len(df)}", "", "## Columns", "| column | dtype | nulls |", "|---|---|---|"]
    for c in df.columns: L.append(f"| {c} | {df[c].dtype} | {int(df[c].isna().sum())} |")
    num = df.select_dtypes("number")
    if not num.empty:
        L += ["", "## Numeric summary", "| column | min | median | max |", "|---|---|---|---|"]
        for c in num.columns: L.append(f"| {c} | {num[c].min():,.4g} | {num[c].median():,.4g} | {num[c].max():,.4g} |")
    L += ["", "## Sample rows", df.head(5).to_markdown(index=False), "", "## Sanity checks"]
    for d, ok in checks: L.append(f"- [{'PASS' if ok else 'FAIL'}] {d}")
    if extra: L += ["", extra]
    (PROFILES/f"{name}.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:2]), "\n" + "\n".join(f"{'PASS' if ok else 'FAIL'}: {d}" for d, ok in checks))
    return all(ok for _, ok in checks)
