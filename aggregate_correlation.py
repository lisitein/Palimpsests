#!/usr/bin/env python3
"""
aggregate_correlation.py

Aggregate the co-occurrence of CreativeStrategy vs NarrativeElement from the
operations CSV, ready for a stacked bar chart (one bar per CreativeStrategy,
segments = NarrativeElement counts).

Usage:
    python aggregate_correlation.py Operations_Audited.csv

Outputs (written next to the input):
    - correlation_matrix.csv   wide: rows=strategy, cols=narrative element, cells=count
                               (+ Total row and Total column)
    - correlation_long.csv     long/tidy: strategy, narrative_element, count
                               (easiest to feed most plotting libs)
    - correlation_row_pct.csv  wide, each row normalised to % (share within a strategy)
Also prints the matrix to the console.
"""

import csv
import sys
import os
from collections import Counter, defaultdict

STRATEGY_COL = "CreativeStrategy (Class)"
ELEMENT_COL  = "NarrativeElement (Class)"

# Fixed display order (nice for charts). Anything not listed is appended alphabetically.
STRATEGY_ORDER = ["Imitation", "Transformation", "Inheritance"]
ELEMENT_ORDER = [
    "CharacterIdentity", "CharacterArc", "CharacterFunction",
    "Chronotope", "WorldRules",
    "EventSequence", "Causality", "Outcome", "Focalization",
    "RelationType", "RelationTopology",
    "ContentDomain", "MediumType",
]

def ordered(seen, preferred):
    """Return preferred items that appear in `seen`, then any extras sorted."""
    out = [x for x in preferred if x in seen]
    out += sorted(x for x in seen if x not in preferred)
    return out

def main(in_path):
    with open(in_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    counts = defaultdict(Counter)         # strategy -> Counter(element -> n)
    strat_seen, elem_seen = set(), set()

    for r in rows:
        s = (r.get(STRATEGY_COL) or "").strip()
        e = (r.get(ELEMENT_COL) or "").strip()
        if not s or not e:
            continue
        counts[s][e] += 1
        strat_seen.add(s)
        elem_seen.add(e)

    strategies = ordered(strat_seen, STRATEGY_ORDER)
    elements   = ordered(elem_seen, ELEMENT_ORDER)

    outdir = os.path.dirname(os.path.abspath(in_path))

    # ---- wide matrix (counts) with totals ----
    matrix_path = os.path.join(outdir, "correlation_matrix.csv")
    with open(matrix_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["CreativeStrategy"] + elements + ["Total"])
        col_tot = Counter()
        for s in strategies:
            row = [counts[s].get(e, 0) for e in elements]
            w.writerow([s] + row + [sum(row)])
            for e in elements:
                col_tot[e] += counts[s].get(e, 0)
        w.writerow(["Total"] + [col_tot[e] for e in elements] + [sum(col_tot.values())])

    # ---- long / tidy (only non-zero cells) ----
    long_path = os.path.join(outdir, "correlation_long.csv")
    with open(long_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["strategy", "narrative_element", "count"])
        for s in strategies:
            for e in elements:
                n = counts[s].get(e, 0)
                if n:
                    w.writerow([s, e, n])

    # ---- row-percentage matrix (share of each element within a strategy) ----
    pct_path = os.path.join(outdir, "correlation_row_pct.csv")
    with open(pct_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["CreativeStrategy"] + elements)
        for s in strategies:
            tot = sum(counts[s].values()) or 1
            w.writerow([s] + [round(100 * counts[s].get(e, 0) / tot, 1) for e in elements])

    # ---- console preview ----
    colw = max(len(e) for e in elements + ["CreativeStrategy"]) + 1
    print("\nCreativeStrategy × NarrativeElement (counts)\n")
    header = "strategy".ljust(16) + "".join(e[:12].rjust(13) for e in elements) + "   Total"
    print(header)
    print("-" * len(header))
    for s in strategies:
        row = [counts[s].get(e, 0) for e in elements]
        print(s.ljust(16) + "".join(str(v).rjust(13) for v in row) + str(sum(row)).rjust(8))
    print()
    print("Wrote:")
    print(" ", matrix_path)
    print(" ", long_path)
    print(" ", pct_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python aggregate_correlation.py <input.csv>")
        sys.exit(1)
    main(sys.argv[1])
