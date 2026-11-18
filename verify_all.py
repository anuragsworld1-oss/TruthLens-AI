"""
TruthLens AI - Master Verification Script
Runs all API endpoints end-to-end and prints a full status report.
"""
import sys, os, json

# Force UTF-8 stdout so Unicode/ANSI never crashes on a Windows cp1252 console.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_pipeline'))

from backend.app import create_app

app = create_app()
app.config["TESTING"] = True

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
HDR  = "\033[96m"
RST  = "\033[0m"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    results.append(condition)
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))

print(f"\n{HDR}===========================================================")
print(f"  TRUTHLENS AI - MASTER INTEGRATION VERIFICATION SUITE")
print(f"==========================================================={RST}\n")

with app.test_client() as c:

    print(f"{HDR}[01] SPA PAGE ROUTING{RST}")
    for route in ['/', '/dashboard', '/studio', '/history', '/models', '/about']:
        resp = c.get(route)
        check(f"GET {route}", resp.status_code == 200 and b'TRUTHLENS AI' in resp.data, f"status={resp.status_code}")

    print(f"\n{HDR}[02] REST API HEALTH & STATS{RST}")
    h = c.get('/api/health')
    hd = json.loads(h.data)
    check("GET /api/health", h.status_code == 200 and hd.get("status") == "operational", hd.get("status"))

    ds = c.get('/api/dashboard/stats')
    dsd = json.loads(ds.data)
    check("GET /api/dashboard/stats", ds.status_code == 200 and "total_articles_analyzed" in dsd,
          f"total={dsd.get('total_articles_analyzed')}")

    mp = c.get('/api/models/performance')
    mpd = json.loads(mp.data)
    check("GET /api/models/performance", mp.status_code == 200 and len(mpd.get("models", {})) >= 4,
          f"models={list(mpd.get('models', {}).keys())}")

    hi = c.get('/api/analysis/history')
    check("GET /api/analysis/history", hi.status_code == 200)

    print(f"\n{HDR}[03] TEXT ANALYSIS PIPELINE{RST}")
    r = c.post('/api/analyze/text', json={
        "title": "NASA James Webb Telescope Confirms Black Hole in CEERS 1019",
        "text": "Astronomers published peer-reviewed findings in The Astrophysical Journal confirming black hole accretion with NIRSpec spectroscopic data."
    })
    rd = json.loads(r.data)
    check("POST /api/analyze/text [science]", r.status_code == 200,
          f"score={rd.get('credibility_score')} class={rd.get('predicted_class')}")
    check("  model_predictions present", "model_predictions" in rd,
          f"models={list((rd.get('model_predictions') or {}).keys())}")
    check("  claims array present", "claims" in rd, f"count={len(rd.get('claims', []))}")
    check("  explanation/XAI present", "explanation" in rd,
          f"tokens={len((rd.get('explanation') or {}).get('token_highlights', []))}")
    check("  linguistic_analysis present", "linguistic_analysis" in rd,
          f"risk={rd.get('linguistic_analysis', {}).get('linguistic_risk_score')}")

    r2 = c.post('/api/analyze/text', json={
        "title": "SHOCKING: 5G Towers Alter DNA",
        "text": "BOMBSHELL REVELATION!! Whistleblowers PROVE 5G cell towers vibrate at quantum bio-resonance frequencies! SHARE BEFORE THEY DELETE THIS!"
    })
    rd2 = json.loads(r2.data)
    check("POST /api/analyze/text [disinfo]", r2.status_code == 200,
          f"score={rd2.get('credibility_score')} class={rd2.get('predicted_class')}")
    check("  disinfo score < 50", (rd2.get("credibility_score") or 100) < 50,
          f"score={rd2.get('credibility_score')}")

    print(f"\n{HDR}[04] SSRF SECURITY GUARD{RST}")
    for bad_url in ["http://127.0.0.1/admin", "http://localhost:9200", "http://169.254.169.254/meta-data"]:
        ru = c.post('/api/analyze/url', json={"url": bad_url})
        check(f"SSRF blocks {bad_url}", ru.status_code in [400, 500])

    print(f"\n{HDR}[05] EDITORIAL REVIEW WORKFLOW{RST}")
    # Use the analysis_id from the science article
    aid = rd.get("analysis_id") or rd.get("id")
    if aid:
        rv = c.post('/api/review', json={"analysis_id": aid, "status": "Verified Authentic", "notes": "Corroborated with Astrophysical Journal"})
        rvd = json.loads(rv.data)
        check("POST /api/review", rv.status_code == 201, rvd.get("message"))

        detail = c.get(f'/api/analysis/{aid}')
        check(f"GET /api/analysis/{aid}", detail.status_code == 200)
    else:
        check("Review workflow (no aid)", False, "analysis_id missing from response")

passed = sum(results)
total = len(results)
print(f"\n{HDR}==========================================================={RST}")
print(f"  RESULT: {passed}/{total} checks passed", PASS if passed == total else FAIL)
print(f"{HDR}==========================================================={RST}\n")
