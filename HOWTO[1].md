
# HOWTO – What to run and what to look for

**Voice: Khujasta Basiri**

## 1) Shell (undergrad requirement)

I made this super direct. One line to run:

```bash
python fuzzy_bn_cli.py --bn attack_flow.xdsl --report '{"T1059":"likely","Ransomware":"high"}'
```

You’ll see lines like:
```
T1059: True=0.8123 False=0.1877
Ransomware: True=0.9000 False=0.1000
...
```

That’s the belief after I map words → numbers and push them into the BN.

## 2) Web (for parity with my midterm)

Start it:
```bash
python bn_ws.py
```

Send a report:
```bash
curl -X POST -H "Content-Type: application/json" localhost:5000/report   -d '{"T1059":"likely","Ransomware":0.9,"Process Delay":"moderate"}'
```

Check beliefs:
```bash
curl localhost:5000/inference
```

Prometheus metrics (for Grafana panels):
```bash
curl localhost:5000/metrics
```

## Notes I kept in mind

- I didn’t include install steps in the video (per the instructions). I just show usage, dynamics,
  evidence submit, and the output.
- If you want me to tune the word→number mapping (e.g., make “moderate” = 0.6 instead of 0.5),
  that’s easy—see the `LINGUISTIC_MAP` in `bn_ws.py` and `fuzzy_bn_cli.py`.

— Khujasta
