import json, os, sys

base = "/home/user/workspace/13511660557912876654/buddhist-ontology"
outdir = os.path.join(base, "_b79")
os.makedirs(outdir, exist_ok=True)

for sid in ["t0709", "t0556", "t0831"]:
    with open(os.path.join(base, "data/baihua-tasks", sid + ".json"), encoding="utf-8") as f:
        obj = json.load(f)
    with open(os.path.join(outdir, "src_" + sid + ".json"), encoding="utf-8") as f:
        tr = json.load(f)

    segs = obj["translations"]
    assert len(segs) == len(tr), (sid, len(segs), len(tr))

    # keep original_preview copy to verify untouched
    before = [s["original_preview"] for s in segs]

    for s, t in zip(segs, tr):
        sec = t["section"]
        mod = t["modern"]
        # section length check (chars, full-width counts as 1)
        assert 1 <= len(sec) <= 14, (sid, sec, len(sec))
        assert "【" not in sec and "】" not in sec and "《" not in sec
        # modern rules
        assert mod.startswith("【" + sec + "】"), (sid, sec, mod[:40])
        assert "【义解】" in mod, (sid, sec)
        assert not mod.endswith("】"), (sid, sec)
        assert '"' not in mod and "'" not in mod, (sid, sec)
        assert '```' not in mod
        s["section"] = sec
        s["modern"] = mod

    after = [s["original_preview"] for s in segs]
    assert before == after, ("original_preview changed!", sid)

    # verify key order and other fields preserved
    with open(os.path.join(outdir, "modern_" + sid + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print(sid, "segments:", len(segs), "-> ok")
