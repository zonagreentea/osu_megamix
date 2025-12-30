import os, pathlib, socket, time, subprocess

# 4.4.4 four — no ego checking
# - no prints
# - returns structured result only
# - each gate max ~4 seconds

def _now(): return time.time()

def gate_egress(timeout=4):
    # silent: try to open a TCP connection (no curl dependency)
    # example.com:443 is stable enough for an egress gate
    try:
        s = socket.create_connection(("example.com", 443), timeout=timeout)
        s.close()
        return True, None
    except Exception as e:
        return False, "egress"

def gate_env(timeout=4):
    # minimal: python present, writable home
    try:
        home = pathlib.Path.home()
        test = home / ".imagination_four_tmp"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True, None
    except Exception:
        return False, "env"

def gate_assets(timeout=4):
    # minimal: beatmaps folder exists (or can exist)
    try:
        base = pathlib.Path(os.environ.get("OSU_MEGAMIX_HOME", str(pathlib.Path.home()/"osu_megamix_home")))
        (base/"beatmaps").mkdir(parents=True, exist_ok=True)
        (base/"skins").mkdir(parents=True, exist_ok=True)
        return True, None
    except Exception:
        return False, "assets"

def gate_entry(timeout=4):
    # minimal: game entry script exists in cwd
    try:
        return (pathlib.Path("osu_megamix.py").exists()), (None if pathlib.Path("osu_megamix.py").exists() else "entry")
    except Exception:
        return False, "entry"

def run_444(timeout_each=4):
    gates = [gate_egress, gate_env, gate_assets, gate_entry]
    failed = []
    for g in gates:
        ok, tag = g(timeout_each)
        if not ok:
            failed.append(tag or "unknown")

    # Outcomes:
    # pass: none failed
    # soft_fail: only egress failed (can still run offline)
    # defer: env/assets/entry failed but fixable
    # abort: multiple hard failures
    if not failed:
        return {"code":"pass","failed":[]}
    if failed == ["egress"]:
        return {"code":"soft_fail","failed":failed}
    if len(failed) <= 2:
        return {"code":"defer","failed":failed}
    return {"code":"abort","failed":failed}
