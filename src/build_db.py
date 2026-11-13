"""Build the SQLite database used by sql/queries.sql and check its answers.

Creates energy.db with one table `energy` from data/analysis_subset.csv,
runs every query in sql/queries.sql, and writes the results to
outputs/sql_results.md so the README and paper can cite SQL output that
was actually produced by the queries.
"""
import sqlite3
import pandas as pd

sub = pd.read_csv("data/analysis_subset.csv")
con = sqlite3.connect("energy.db")
sub.to_sql("energy", con, if_exists="replace", index=False)

with open("sql/queries.sql") as f:
    script = f.read()

# split into individual queries on the Qn. markers
blocks, current = [], []
for line in script.splitlines():
    if line.startswith("-- Q") and current:
        blocks.append("\n".join(current))
        current = [line]
    else:
        current.append(line)
if current:
    blocks.append("\n".join(current))

out = ["# SQL query results\n",
       "Produced by `src/build_db.py` running `sql/queries.sql` against "
       "`energy.db`.\n"]
for block in blocks:
    lines = [l for l in block.splitlines() if not l.strip().startswith("-- ====")]
    title = next((l[3:].strip() for l in lines if l.startswith("-- Q")), "Query")
    sql = "\n".join(l for l in lines if not l.startswith("--")).strip()
    if not sql:
        continue
    df = pd.read_sql_query(sql, con)
    out.append(f"## {title}\n")
    out.append("```sql\n" + sql + "\n```\n")
    out.append(df.to_markdown(index=False) + "\n")

with open("outputs/sql_results.md", "w") as f:
    f.write("\n".join(out))
con.close()
print("energy.db built; outputs/sql_results.md written")
