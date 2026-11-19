#!/usr/bin/env python3
"""Analyse the official 30-second iTunes previews of a set (runs in GitHub Actions, never locally).

Only numbers are written out (tempo, beat grid, key, loudness); the audio itself is not stored or
redistributed. The browser page (megamix.html) streams the previews from Apple and mixes them live.

usage: analyze_previews.py sets/megamix1.json sets/megamix1.analysis.json
"""
import json, os, subprocess, sys, tempfile, urllib.request

import numpy as np
import librosa

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJ_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
CAMELOT_MAJ = {0: "8B", 7: "9B", 2: "10B", 9: "11B", 4: "12B", 11: "1B", 6: "2B", 1: "3B", 8: "4B", 3: "5B", 10: "6B", 5: "7B"}
CAMELOT_MIN = {9: "8A", 4: "9A", 11: "10A", 6: "11A", 1: "12A", 8: "1A", 3: "2A", 10: "3A", 5: "4A", 0: "5A", 7: "6A", 2: "7A"}
SR = 22050
HOP = 128
UA = {"User-Agent": "muzic-analyzer/1.0"}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def lookup(track_id):
    url = f"https://itunes.apple.com/lookup?id={track_id}&entity=song"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        res = json.load(r)["results"]
    if not res or not res[0].get("previewUrl"):
        raise SystemExit(f"no preview for iTunes id {track_id}")
    return res[0]


def load(preview_url, work):
    src = os.path.join(work, "p.m4a")
    wav = os.path.join(work, "p.wav")
    with urllib.request.urlopen(urllib.request.Request(preview_url, headers=UA), timeout=60) as r, open(src, "wb") as f:
        f.write(r.read())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(SR), wav], check=True)
    y, _ = librosa.load(wav, sr=SR, mono=True)
    return y


def usable_window(y):
    """Previews fade in and out; keep the part that is at full level."""
    frame = 1024
    rms = librosa.feature.rms(y=y, frame_length=frame, hop_length=512)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=SR, hop_length=512)
    ref = np.percentile(rms, 70)
    ok = np.nonzero(rms >= 0.55 * ref)[0]
    if not len(ok):
        return 0.0, len(y) / SR
    return float(t[ok[0]]), float(t[ok[-1]])


def beat_grid(y, start, end):
    _, beat_frames = librosa.beat.beat_track(y=y, sr=SR, hop_length=HOP, tightness=120)
    raw = librosa.frames_to_time(beat_frames, sr=SR, hop_length=HOP)
    raw = raw[(raw >= start) & (raw <= end)]
    if len(raw) < 12:
        raise SystemExit("too few beats")
    k = np.arange(len(raw))
    T, t0 = np.polyfit(k, raw, 1)
    for _ in range(3):
        res = raw - (t0 + T * k)
        keep = np.abs(res) < 0.15 * T
        if keep.sum() > 10:
            T, t0 = np.polyfit(k[keep], raw[keep], 1)
    tempo = 60.0 / T
    while tempo < 85:
        tempo *= 2
        T /= 2
    while tempo > 170:
        tempo /= 2
        T *= 2
    first = t0 - np.floor((t0 - start) / T) * T  # first grid beat at/after start
    if first < start:
        first += T
    beats = np.arange(first, end, T)
    return float(tempo), float(T), beats


def downbeat_phase(y, beats):
    """In dance music the kick is strongest on beat 1 of the bar."""
    lows = librosa.onset.onset_strength(y=librosa.effects.preemphasis(y, coef=-0.97), sr=SR, hop_length=HOP)
    bf = librosa.time_to_frames(beats, sr=SR, hop_length=HOP)
    bf = bf[bf < len(lows)]
    if len(bf) < 8:
        return 0
    return int(np.argmax([lows[bf[p::4]].mean() for p in range(4)]))


def triplet_feel(y, beats, T):
    """>1 means the beat is split in three (Persian 6/8, bandari shuffle); <1 means straight 4/4 sixteenths."""
    env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)

    def at(times):
        f = librosa.time_to_frames(times, sr=SR, hop_length=HOP)
        f = f[(f >= 0) & (f < len(env))]
        return float(env[f].mean()) if len(f) else 0.0

    trip = (at(beats + T / 3) + at(beats + 2 * T / 3)) / 2
    straight = (at(beats + T / 2) + (at(beats + T / 4) + at(beats + 3 * T / 4)) / 2) / 2
    return trip / max(straight, 1e-6)


def key_of(y):
    chroma = librosa.feature.chroma_cqt(y=y, sr=SR).mean(axis=1)
    best = (-9, 0, "maj")
    for k in range(12):
        for prof, mode in ((MAJ_PROFILE, "maj"), (MIN_PROFILE, "min")):
            r = np.corrcoef(np.roll(prof, k), chroma)[0, 1]
            if r > best[0]:
                best = (r, k, mode)
    _, tonic, mode = best
    return f"{NOTES[tonic]} {'major' if mode == 'maj' else 'minor'}", (CAMELOT_MAJ if mode == "maj" else CAMELOT_MIN)[tonic]


def analyse(y, start, end):
    tempo, T, beats = beat_grid(y, start, end)
    phase = downbeat_phase(y, beats)
    downbeats = beats[phase::4]
    seg = y[int(start * SR):int(end * SR)]
    rms = float(np.sqrt(np.mean(seg ** 2)))
    bars = []
    for i in range(len(downbeats) - 1):
        s = y[int(downbeats[i] * SR):int(downbeats[i + 1] * SR)]
        bars.append(float(np.sqrt(np.mean(s ** 2))) if len(s) else 0.0)
    bars = np.array(bars) if bars else np.array([rms])
    onset_rate = float(np.mean(librosa.onset.onset_strength(y=seg, sr=SR)))
    key, camelot = key_of(seg)
    return {
        "bpm": round(tempo, 2), "beat": round(T, 5),
        "beats": [round(b, 4) for b in beats.tolist()],
        "downbeats": [round(b, 4) for b in downbeats.tolist()],
        "key": key, "camelot": camelot,
        "triplet": round(triplet_feel(y, beats, T), 3),
        "rms": round(rms, 5),
        "gain_db": round(float(np.clip(20 * np.log10(0.12 / max(rms, 1e-6)), -9, 9)), 2),
        "energy": round(float(np.percentile(bars, 75)) * 10 + onset_rate * 0.3, 3),
        "loudest_bar": int(np.argmax(bars)),
    }


def main(set_path, out_path):
    cfg = json.load(open(set_path, encoding="utf-8"))
    out = {"source": "iTunes 30-second previews", "songs": {}}
    for s in cfg["songs"]:
        info = lookup(s["itunes"])
        with tempfile.TemporaryDirectory() as work:
            y = load(info["previewUrl"], work)
        start, end = usable_window(y)
        a = analyse(y, start, end)
        a.update({
            "preview": info["previewUrl"], "page": info.get("trackViewUrl"),
            "itunes_title": f'{info.get("artistName")} - {info.get("trackName")}',
            "duration": round(len(y) / SR, 3), "usable": [round(start, 3), round(end, 3)],
        })
        out["songs"][s["key"]] = a
        log(f'{s["key"]:18s} {a["bpm"]:7.2f} bpm  {a["camelot"]:>3s}  triplet {a["triplet"]:.2f}  '
            f'usable {start:.1f}-{end:.1f}s  gain {a["gain_db"]:+.1f}dB')
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
