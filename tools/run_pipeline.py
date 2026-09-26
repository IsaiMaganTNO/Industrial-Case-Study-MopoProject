"""Headless step-by-step runner for the IC1 Spine Toolbox pipeline.

Why this exists instead of the Spine Toolbox GUI:
  * The remote machine cannot be power-cycled by the operator. Running from the
    command line means a dropped RDP session does not kill the job.
  * Every step is logged to run_logs/NN_<tool>.log for post-mortem inspection.
  * Resource use is sampled around every step, so if something is about to
    exhaust RAM or disk we see it in the log rather than by losing the machine.
  * Stopping between steps lets us inspect the databases as they are built,
    which is how both previous silent keying bugs would have been caught early.

Deliberately excluded: Run_Model_Planning, fix_investments, Run_Dispatch,
visualization. The stage 1 solve is launched separately and explicitly.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / ".spinetoolbox" / "project.json"
LOGDIR = ROOT / "run_logs"
VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"
JULIA = Path(os.environ.get(
    "JULIA_EXE",
    r"C:\Users\maganih\.julia\juliaup\julia-1.12.6+0.x64.w64.mingw32\bin\julia.exe"))
JENV = ROOT / "jenv"

EXCLUDED = {"Run_Model_Planning", "Run_Dispatch", "fix_investments", "visualization"}

MIN_FREE_DISK_GB = 20.0
MAX_RAM_FRACTION = 0.85


def load_project():
    with open(PROJECT, encoding="utf-8") as fh:
        return json.load(fh)


def tool_order(proj):
    items = proj["items"]
    succ = defaultdict(list)
    indeg = defaultdict(int)
    nodes = set(items)
    for c in proj["project"]["connections"]:
        f, t = c["from"][0], c["to"][0]
        succ[f].append(t)
        indeg[t] += 1
    q = deque(sorted(n for n in nodes if indeg[n] == 0))
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for m in sorted(succ[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    return [n for n in order if items.get(n, {}).get("type") == "Tool"]


def spec_for(proj, tool_name):
    spec_name = proj["items"][tool_name].get("specification")
    for entry in proj["project"]["specifications"]["Tool"]:
        p = ROOT / entry["path"]
        with open(p, encoding="utf-8") as fh:
            spec = json.load(fh)
        if spec.get("name") == spec_name:
            return spec, p
    return None, None


def db_path(proj, ds_name):
    rel = proj["items"][ds_name]["url"]["database"]
    rel = rel if isinstance(rel, str) else rel["path"]
    return ROOT / rel


def resolve_args(proj, tool_name):
    out = []
    for a in proj["items"][tool_name].get("cmd_line_args", []):
        arg = a if isinstance(a, str) else a.get("arg", "")
        if isinstance(a, dict) and a.get("type") == "resource" and str(arg).startswith("db_url@"):
            ds = str(arg).split("@", 1)[1]
            out.append("sqlite:///" + str(db_path(proj, ds)))
            continue
        out.append(str(arg).replace("<project>/", str(ROOT) + os.sep))
    return out


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def resources():
    total = free = 0.0
    try:
        m = MEMORYSTATUSEX()
        m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        total = m.ullTotalPhys / 2 ** 30
        free = m.ullAvailPhys / 2 ** 30
    except Exception:
        pass
    disk = shutil.disk_usage(str(ROOT)).free / 2 ** 30
    return total, free, disk


def guard(log):
    total, free, disk = resources()
    if disk < MIN_FREE_DISK_GB:
        log("ABORT: only %.1f GB free disk (limit %.1f)." % (disk, MIN_FREE_DISK_GB))
        return False
    if total:
        used = (total - free) / total
        if used > MAX_RAM_FRACTION:
            log("ABORT: RAM at %.0f%% (limit %.0f%%)." % (used * 100, MAX_RAM_FRACTION * 100))
            return False
    return True


def db_stats():
    from spinedb_api import DatabaseMapping
    proj = load_project()
    out = {}
    for name, item in proj["items"].items():
        if item["type"] != "Data Store":
            continue
        p = db_path(proj, name)
        if not p.exists():
            out[name] = None
            continue
        try:
            with DatabaseMapping("sqlite:///" + str(p)) as db:
                out[name] = (len(db.get_entity_items()), len(db.get_parameter_value_items()))
        except Exception:
            out[name] = "error"
    return out


def run_tool(proj, name, index):
    spec, spec_path = spec_for(proj, name)
    if spec is None:
        print("  !! no specification for " + name)
        return False
    main = spec["includes"][0]
    main_dir = (spec_path.parent / spec.get("includes_main_path", ".")).resolve()
    script = main_dir / main
    args = resolve_args(proj, name)
    tooltype = spec.get("tooltype", "python").lower()
    if tooltype == "python":
        cmd = [str(VENV_PY), str(script)] + args
    elif tooltype == "julia":
        cmd = [str(JULIA), "--project=" + str(JENV), str(script)] + args
    else:
        print("  !! unsupported tooltype %s for %s" % (tooltype, name))
        return False

    LOGDIR.mkdir(exist_ok=True)
    logfile = LOGDIR / ("%02d_%s.log" % (index, name))

    def log(msg):
        print(msg)
        with open(logfile, "a", encoding="utf-8") as fh:
            fh.write(msg + "\n")

    with open(logfile, "w", encoding="utf-8") as fh:
        fh.write("# %s\n# %s\n# cwd=%s\n" % (name, datetime.now().isoformat(), main_dir))
        fh.write("# " + " ".join(cmd) + "\n\n")

    if not guard(log):
        return False
    total, free, disk = resources()
    log("  RAM %.1f/%.1f GB used | disk %.1f GB free" % (total - free, total, disk))

    t0 = time.time()
    with open(logfile, "a", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=str(main_dir), stdout=fh,
                              stderr=subprocess.STDOUT, text=True)
    dt = time.time() - t0
    total, free, disk = resources()
    log("  exit=%d in %.1f min | RAM %.1f/%.1f GB | disk %.1f GB free"
        % (proc.returncode, dt / 60, total - free, total, disk))
    if proc.returncode != 0:
        log("  FAILED - see " + str(logfile))
        with open(logfile, encoding="utf-8", errors="replace") as fh:
            tail = fh.read().splitlines()[-25:]
        for line in tail:
            print("    | " + line)
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--from", dest="start")
    ap.add_argument("--until")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    proj = load_project()
    order = [t for t in tool_order(proj) if t not in EXCLUDED]

    if a.stats:
        for k, v in db_stats().items():
            print("  %-24s %s" % (k, v))
        return 0
    if a.list:
        for i, t in enumerate(order, 1):
            print("  %2d. %s" % (i, t))
        return 0

    todo = [a.only] if a.only else list(order)
    if not a.only:
        if a.start:
            todo = todo[todo.index(a.start):]
        if a.until:
            todo = todo[: todo.index(a.until) + 1]

    print("Running %d tool(s): %s\n" % (len(todo), ", ".join(todo)))
    before = db_stats()
    t_all = time.time()
    for i, name in enumerate(todo, 1):
        idx = order.index(name) + 1 if name in order else i
        print("[%d/%d] %s" % (i, len(todo), name))
        if not run_tool(proj, name, idx):
            print("\nSTOPPED at %s. Databases left as-is for inspection." % name)
            return 1
        print()
    after = db_stats()
    print("--- all steps done in %.1f min ---" % ((time.time() - t_all) / 60))
    for k in after:
        if before.get(k) != after.get(k):
            print("%-24s %18s -> %-18s" % (k, before.get(k), after.get(k)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
