#!/usr/bin/env python3
"""Build data/party.js: tempo, key and energy for the Israeli / international wedding songs.

Runs in GitHub Actions (never locally). For every song it finds the official iTunes 30-second preview,
analyses it in memory and keeps only the numbers. iTunes allows ~20 searches a minute, so it goes slowly.

usage: build_party_catalog.py data/party_list.txt data/party.js
"""
import json, re, sys, tempfile, time, unicodedata, urllib.parse, urllib.request

import numpy as np

sys.path.insert(0, "mixer")
from analyze_previews import UA, load, usable_window, beat_grid, key_of, SR  # noqa: E402
import librosa  # noqa: E402

GAP = 3.4
JUNK = re.compile(r"cover|karaoke|kidz bop|rockabye|lullaby|instrumental|tribute|\blive\b|לייב|הופעה חיה|the voice|רמיקס|remix|sped up|slowed|8d", re.I)


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)
    s = re.sub(r"[^\w֐-׿]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def first_artist(a):
    return re.split(r",|&| feat\.? | x | ו(?=[֐-׿])| עם ", a)[0].strip()


last = [0.0]


def search(term, country):
    wait = GAP - (time.time() - last[0])
    if wait > 0:
        time.sleep(wait)
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(
        {"term": term, "media": "music", "entity": "song", "limit": 8, "country": country})
    for attempt in range(4):
        last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r).get("results", [])
        except Exception as e:  # 403/429 when rate limited
            print(f"   retry ({e})", file=sys.stderr, flush=True)
            time.sleep(20 * (attempt + 1))
    return []


def lookup_id(track_id):
    wait = GAP - (time.time() - last[0])
    if wait > 0:
        time.sleep(wait)
    last[0] = time.time()
    for country in ("il", "us"):
        url = f"https://itunes.apple.com/lookup?id={track_id}&country={country}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            res = json.load(r).get("results", [])
        if res and res[0].get("previewUrl"):
            return res[0]
    return None


def best_hit(title, artist, he):
    t, a = norm(title), norm(first_artist(artist))
    for country in (("il", "us") if he else ("us", "il")):
        for term in (f"{title} {first_artist(artist)}", title):
            res = [r for r in search(term, country) if r.get("previewUrl")]
            scored = []
            for r in res:
                rt, ra = norm(r.get("trackName", "")), norm(r.get("artistName", ""))
                raw = r.get("trackName", "") + " " + r.get("artistName", "") + " " + r.get("collectionName", "")
                if JUNK.search(raw) and not JUNK.search(title + " " + artist):
                    continue                      # covers, kids versions, karaoke, live takes, foreign remixes
                artist_ok = bool(a and (a in ra or ra in a))
                if not he and not artist_ok:
                    continue                      # English titles are too generic without the right artist
                s = (3 if rt == t else 2 if (t in rt or rt in t) else 0) + (2 if artist_ok else 0)
                scored.append((s, r))
            scored.sort(key=lambda x: -x[0])
            if scored and scored[0][0] >= 3:
                return scored[0][1], scored[0][0]
    return None, 0


def parse(path):
    cat, out = None, []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        m = re.match(r"#\s*cat:\s*(\w+)\s*\|\s*(.+)", line)
        if m:
            cat = (m.group(1), m.group(2).strip())
            continue
        if not line or line.startswith("#"):
            continue
        line, _, pin = line.partition(" | itunes:")
        title, _, artist = line.partition(" - ")
        out.append({"title": title.strip(), "artist": artist.strip(), "cat": cat[0], "cat_he": cat[1], "pin": pin.strip() or None})
    return out


def main(src, dst):
    songs = parse(src)
    out = []
    for i, s in enumerate(songs):
        he = bool(re.search(r"[֐-׿]", s["title"] + s["artist"]))
        rec = {"id": f"party-{i + 1}", "n": i + 1, **s, "lang": "he" if he else "en"}
        pin = rec.pop("pin", None)
        if pin == "none":
            hit, score = None, 0
        elif pin:
            res = lookup_id(pin)
            hit, score = (res, 9) if res else (None, 0)
        else:
            hit, score = best_hit(s["title"], s["artist"], he)
        if hit:
            rec.update({"itunes": hit["trackId"], "itunes_title": hit["trackName"], "itunes_artist": hit["artistName"],
                        "duration_sec": round(hit.get("trackTimeMillis", 0) / 1000), "link": hit.get("trackViewUrl"),
                        "match": score})
            try:
                with tempfile.TemporaryDirectory() as work:
                    y = load(hit["previewUrl"], work)
                start, end = usable_window(y)
                start, end = max(start, 1.0), min(end, len(y) / SR - 2.5)
                tempo, _, _ = beat_grid(y, start, end)
                seg = y[int(start * SR):int(end * SR)]
                key, camelot = key_of(seg)
                rms = float(np.sqrt(np.mean(seg ** 2)))
                onset = float(np.mean(librosa.onset.onset_strength(y=seg, sr=SR)))
                rec.update({"bpm": round(tempo, 1), "key": key, "camelot": camelot, "rms": round(rms, 4), "onset": round(onset, 3)})
            except Exception as e:
                rec["error"] = str(e)[:80]
        print(f'{i + 1:3d} {s["title"][:28]:28s} -> {rec.get("itunes_title", "NOT FOUND")[:28]:28s} '
              f'{rec.get("bpm", "")} {rec.get("camelot", "")}', file=sys.stderr, flush=True)
        out.append(rec)
    # energy 0..1 relative to this catalog: loudness + rhythmic density + tempo
    have = [r for r in out if "rms" in r]
    if have:
        def z(vals):
            v = np.array(vals, dtype=float)
            return (v - v.mean()) / (v.std() or 1)
        tempos = [min(max(r["bpm"], 85), 140) for r in have]
        e = z([r["rms"] for r in have]) * 0.35 + z([r["onset"] for r in have]) * 0.45 + z(tempos) * 0.2
        e = (e - e.min()) / ((e.max() - e.min()) or 1)
        for r, v in zip(have, e):
            r["energy"] = round(float(v), 3)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("// Generated by mixer/build_party_catalog.py in GitHub Actions. Do not edit by hand.\n")
        f.write("window.PARTY = " + json.dumps({"generated": time.strftime("%Y-%m-%d"), "songs": out}, ensure_ascii=False, indent=0) + ";\n")
    found = sum(1 for r in out if "bpm" in r)
    print(f"done: {found}/{len(out)} analysed", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
