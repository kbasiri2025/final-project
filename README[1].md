
# Fuzzy Bayesian Network – Final (Undergrad)

Hi, I'm **Khujasta Basiri**. This is my undergrad final where I upgraded my midterm BN into a **Fuzzy BN**. 
You can run it two ways:
- **Shell mode (required for undergrad spec)**
- **Flask service (so you can see metrics propagate like the midterm)**

## Quick start (shell)

```bash
# example report with linguistic inputs
python fuzzy_bn_cli.py --bn attack_flow.xdsl --report '{"T1059":"likely","Ransomware":"high"}'
```

This prints belief values for each node (True/False). I convert words like `low/moderate/high/likely` into 
numbers in [0..1] and then apply them on the BN.

## Quick start (web)

```bash
python bn_ws.py
# POST a report:
curl -X POST -H "Content-Type: application/json" localhost:5000/report   -d '{"T1059":"likely","Ransomware":0.9,"Process Delay":"moderate"}'
# Pull beliefs:
curl localhost:5000/inference
# Prometheus metrics (True-beliefs):
curl localhost:5000/metrics
```

Prometheus runs on port **8000**. Flask is on **5000**. You don't need to show install in the demo,
just show **how to use, submit evidence, and what the output looks like**.

## What changed from my midterm

- Added **linguistic inputs** (`/report` POST) → turn them into numeric confidence.
- Kept the same **BN file** (`attack_flow.xdsl`) so you can compare behavior quickly.
- Pushed **beliefs to Prometheus** so Grafana panels can show *fuzzy* status (e.g., high/low risk).

## Files

- `attack_flow.xdsl` – the BN
- `bn_ws.py` – Flask + Prometheus, now with `/report` and `/inference`
- `fuzzy_bn.py` – my FBN builder (kept simple and readable)
- `fuzzy_bn_cli.py` – shell interface for grading undergrad spec
- `stix_to_bn.py` – utility from my midterm for STIX → BN (still useful)
- `README.md`, `HOWTO.md` – how I run and test things

If you have any trouble, please check the HOWTO below. Thanks!
