# Excel round-trip corruption in the staged VRE timeseries
Days 1-12 of each month : "DD-MM-YYYY"      -- HOUR LOST (24 identical stamps)
Days 13-31              : "M/D/YYYY H:MM"   -- hour present, MONTH-first
Some files (solar-PV-no-tracking) : "DD-MM-YYYY HH:MM:SS" throughout, uniform.

Classic Excel locale damage: ambiguous day<=12 dates were re-interpreted and
reformatted; unambiguous day>=13 dates were left in US style.

Consequences
- A single dayfirst=True parse yields NaT on every day>=13 row (223,032 of them).
- A single dayfirst=False parse would SILENTLY TRANSPOSE day and month on the
  days 1-12 rows -- far worse, because it fails quietly.
- The hour genuinely is unrecoverable from the string for days 1-12; it must be
  reconstructed from row order, which is safe because rows are chronological.
