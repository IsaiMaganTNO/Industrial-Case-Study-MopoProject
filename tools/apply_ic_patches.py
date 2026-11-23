"""Apply the industrial-case model patches to a SpineOpt input database, in a fixed order.

Usage:
  python tools/apply_ic_patches.py SRC.sqlite DST.sqlite [--config config/ic_patches.yaml]
                                   [--from STEP] [--to STEP] [--keep-work]

Each step runs an existing tools/*.py patch script on a fresh copy, so every intermediate
database is kept in a work folder next to DST (deleted at the end unless --keep-work).
SRC is never modified. Stops at the first failing step. A log is written to DST + ".log".
"""
import argparse, os, shutil, subprocess, sys, time
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--config", default=os.path.join(ROOT, "config", "ic_patches.yaml"))
    ap.add_argument("--from", dest="start"); ap.add_argument("--to", dest="stop")
    ap.add_argument("--keep-work", action="store_true")
    a = ap.parse_args()
    src, dst = os.path.abspath(a.src), os.path.abspath(a.dst)
    if not os.path.exists(src): sys.exit(f"SRC not found: {src}")
    if os.path.exists(dst): sys.exit(f"DST exists: {dst}")
    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    steps = [s for s in cfg["steps"] if s.get("enabled", True)]
    ids = [s["id"] for s in steps]
    i0 = ids.index(a.start) if a.start else 0
    i1 = ids.index(a.stop) + 1 if a.stop else len(steps)
    steps = steps[i0:i1]
    work = dst + ".work"; os.makedirs(work, exist_ok=True)
    log = open(dst + ".log", "w", encoding="utf-8")
    def say(msg):
        print(msg); log.write(msg + "\n"); log.flush()
    say(f"case {cfg.get('case')} | {len(steps)} steps: {', '.join(s['id'] for s in steps)}")
    say(f"SRC {src}")
    cur = src
    for n, s in enumerate(steps, 1):
        out = os.path.join(work, f"{n:02d}_{s['id']}.sqlite")
        if s.get("output") == "none":
            out = cur
        elif s.get("inplace"):
            shutil.copyfile(cur, out)
        sub = {"src": cur, "dst": out, "work": work, "root": ROOT}
        args = [str(x).format(**sub) for x in s.get("args", [])]
        cmd = [sys.executable, os.path.join(ROOT, s["script"])] + args
        say(f"\n=== [{n}/{len(steps)}] {s['id']}: {' '.join(cmd[1:])}")
        t = time.time()
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        log.write(p.stdout); log.write(p.stderr); log.flush()
        tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
        for line in tail: print("    " + line)
        if p.returncode != 0 or not os.path.exists(out):
            say(f"FAILED at step {s['id']} (exit {p.returncode}); intermediates kept in {work}")
            sys.exit(1)
        say(f"    ok ({time.time() - t:.0f} s)")
        cur = out
    shutil.copyfile(cur, dst)
    say(f"\nWROTE {dst}")
    if not a.keep_work: shutil.rmtree(work)
    log.close()

if __name__ == "__main__":
    main()
