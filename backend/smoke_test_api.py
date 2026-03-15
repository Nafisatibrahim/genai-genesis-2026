"""
Smoke test for FlexCare API. Run with API up: uvicorn backend.api:app --port 8000
Usage: python -m backend.smoke_test_api [--base http://localhost:8000]
"""
import argparse
import json
import sys
import urllib.request

def req(method, url, body=None):
    kwargs = {"method": method}
    if body is not None:
        kwargs["data"] = json.dumps(body).encode("utf-8")
        kwargs["headers"] = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, **kwargs)
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.getcode(), json.loads(res.read().decode())

def get(base, path):
    return req("GET", base.rstrip("/") + path)

def post(base, path, body):
    return req("POST", base.rstrip("/") + path, body)

def put(base, path, body):
    return req("PUT", base.rstrip("/") + path, body)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:8000", help="API base URL")
    args = p.parse_args()
    base = args.base
    ok = True

    # 1. Health (and connection check)
    try:
        code, data = get(base, "/health")
        assert code == 200 and data.get("status") == "ok"
        print("[OK] GET /health")
    except OSError as e:
        if "refused" in str(e).lower() or "10061" in str(e):
            print(f"[SKIP] API not running at {base}. Start it with:")
            print("       uvicorn backend.api:app --host 127.0.0.1 --port 8000")
        else:
            print(f"[FAIL] GET /health: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] GET /health: {e}")
        ok = False

    # 2. Profile PUT + GET (with insurer_slug, plan_slug)
    try:
        code, _ = put(base, "/profile", {
            "session_id": "smoke-session",
            "insurer_slug": "sunlife",
            "plan_slug": "sunlife_basic",
        })
        assert code == 200
        code, data = get(base, "/profile?session_id=smoke-session")
        assert code == 200
        prof = data.get("profile")
        assert prof is not None
        assert prof.get("insurer_slug") == "sunlife" and prof.get("plan_slug") == "sunlife_basic"
        print("[OK] PUT/GET /profile (insurer_slug, plan_slug)")
    except Exception as e:
        print(f"[FAIL] Profile: {e}")
        ok = False

    # 3. Exercises
    try:
        code, data = get(base, "/exercises")
        assert code == 200
        ex = data.get("exercises") or []
        ids = [e.get("id") for e in ex]
        assert "bodyweight_squat" in ids and "cat_cow" in ids and "chin_tucks" in ids
        for e in ex:
            assert "id" in e and "name" in e and "instructions" in e
        print("[OK] GET /exercises (squat, cat_cow, chin_tucks)")
    except Exception as e:
        print(f"[FAIL] GET /exercises: {e}")
        ok = False

    # 4. Cost estimate
    try:
        code, data = get(base, "/referral/cost-estimate?plan_slug=sunlife_basic&provider_type=physio")
        assert code == 200
        assert isinstance(data, dict)
        if data:
            assert "coverage_percent" in data or "you_pay" in data or "cost_per_visit" in data
        print("[OK] GET /referral/cost-estimate")
    except Exception as e:
        print(f"[FAIL] GET /referral/cost-estimate: {e}")
        ok = False

    # 5. Referral data: insurers, plans, providers
    try:
        code, data = get(base, "/referral/insurers")
        assert code == 200 and isinstance(data.get("insurers"), list)
        code, data = get(base, "/referral/plans?insurer_slug=sunlife")
        assert code == 200 and isinstance(data.get("plans"), list)
        code, data = get(base, "/referral/providers?provider_type=physio")
        assert code == 200
        providers = data.get("providers") or []
        if providers:
            assert "id" in providers[0]
        print("[OK] GET /referral/insurers, /plans, /providers (with id)")
    except Exception as e:
        print(f"[FAIL] Referral data: {e}")
        ok = False

    # 6. Explain without provider_id (plan-level)
    try:
        code, data = post(base, "/referral/explain", {
            "provider_type": "physio",
            "plan_slug": "sunlife_basic",
            "question": "why",
        })
        assert code == 200 and "explanation" in data and len(data["explanation"]) > 0
        print("[OK] POST /referral/explain (no provider_id)")
    except Exception as e:
        print(f"[FAIL] POST /referral/explain (no provider_id): {e}")
        ok = False

    # 7. Explain with provider_id (per-provider)
    try:
        code, data = post(base, "/referral/explain", {
            "provider_type": "physio",
            "plan_slug": "sunlife_basic",
            "question": "why",
            "provider_id": "p1",
        })
        assert code == 200 and "explanation" in data and len(data["explanation"]) > 0
        print("[OK] POST /referral/explain (provider_id=p1)")
    except Exception as e:
        print(f"[FAIL] POST /referral/explain (provider_id): {e}")
        ok = False

    if not ok:
        sys.exit(1)
    print("\nAll smoke tests passed.")

if __name__ == "__main__":
    main()
