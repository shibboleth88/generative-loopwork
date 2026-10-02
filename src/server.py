"""Static files + a generate endpoint for the loopwork engine (RULES.md v3).

There is one implementation of the rules (loopwork.py). The browser draws what
it returns and contains no generator, so the picture cannot drift from them.
"""
import gzip, json, os, sys, time, functools, http.server, socketserver, urllib.parse
from dataclasses import asdict

PORT = 8778
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
import loopwork as LW

def r3(a):
    return [[round(float(x), 4) for x in p] for p in a]

def generate(params):
    base = asdict(LW.Ruleset())
    kw = {}
    for k, v in base.items():
        if k in params:
            raw = params[k][0]
            kw[k] = (raw if isinstance(v, str) else
                     raw.lower() == "true" if isinstance(v, bool) else type(v)(raw))
    R = LW.Ruleset(**kw)
    t = time.time()
    w = LW.build(R)
    s = LW.stats(R, w)
    s["build_seconds"] = round(time.time() - t, 3)

    P, n = w["P"], len(w["P"])
    sh = LW.occlusion(R, w)        # how buried each stitch is -- a measurement
    stitches = []
    for i in range(n):
        col = w["colour"][i]
        stitches.append({
            "at": i, "colour": col, "shade": round(float(sh[i]), 3),
            # the loop this bight was pulled THROUGH: the act itself
            "t": int(w["target"][i]),
            "radius": R.cord_radius * (R.heavy_scale if col == LW.HEAVY else 1.0),
            "pts": r3(LW.bight(R, P, i, n, seg=12)),
        })
    rings = []
    for si in w["rings"]:
        c, axis = LW.ring_frame(R, w, si)
        rings.append({"at": int(si), "c": [float(x) for x in c],
                      "axis": [float(x) for x in axis],
                      "r": R.ring_radius, "tube": R.ring_tube})
    carries = []
    for a, b, *_ in w["carries"]:
        col = w["colour"][b]
        carries.append({"at": int(b), "colour": col, "shade": round(float(sh[b]), 3),
                        "radius": R.cord_radius * (R.heavy_scale if col == LW.HEAVY else 1.0),
                        "pts": r3(LW.carry_path(P, a, b))})
    tails = []
    for (path, col), si in zip(LW.tail_paths(R, w),
                               [s2 for s2 in w["tails"] for _ in (0, 1)]):
        tails.append({"at": int(si), "colour": col,
                      "shade": round(float(sh[min(si, n-1)]), 3),
                      "radius": R.cord_radius * (R.heavy_scale if col == LW.HEAVY else 1.0),
                      "pts": r3(path)})
    # Everything needed to HANDLE the finished piece: who is linked to whom,
    # and the solver's own constants. Handling is not generating -- the object
    # is already made, and these let the browser move it the way the generator
    # would, rather than inventing a second physics.
    joined = w["joined"]
    handling = {
        "target": [int(x) for x in w["target"]],
        "joined": [1 if x else 0 for x in joined],
        "carries": [[int(a), int(b)] for a, b, *_ in w["carries"]],
        "rings": [int(x) for x in w["rings"]],
        "pitch": R.loop_a * 1.15,
        "link_rest": R.loop_a * 0.95,
        "cutoff": R.loop_a * 1.6,
        "stiff_chain": R.stiff_chain, "repel": R.repel,
        "gravity": R.gravity, "damping": R.damping,
        "max_step": R.max_step, "ring_weight": R.ring_weight,
    }

    return {"ruleset": asdict(R), "stats": s, "policies": LW.TARGETS,
            "handling": handling,
            "stitches": stitches, "rings": rings, "tails": tails,
            "carries": carries,
            "materials": {k: list(v) for k, v in LW.MATS.items()}}

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path != "/api/generate":
            return super().do_GET()
        try:
            body = json.dumps(generate(urllib.parse.parse_qs(u.query))).encode(); code = 200
        except SystemExit as e:
            body = json.dumps({"error": str(e)}).encode(); code = 400
        except Exception as e:
            body = json.dumps({"error": f"{type(e).__name__}: {e}"}).encode(); code = 500
        enc = None
        if "gzip" in self.headers.get("Accept-Encoding", ""):
            body = gzip.compress(body, 5); enc = "gzip"
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if enc:
            self.send_header("Content-Encoding", enc)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *a):
        print("%s - %s" % (self.address_string(), fmt % a))

class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == "__main__":
    print(f"loopwork server on http://localhost:{PORT}")
    S(("", PORT), functools.partial(H, directory=HERE)).serve_forever()
