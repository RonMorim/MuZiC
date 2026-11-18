"""MuZiC automix: analyse songs, order them like a DJ, pick a transition per pair, render one mix.

Runs in the cloud (GitHub Actions). Needs: ffmpeg, rubberband-cli, numpy, scipy, librosa, soundfile.
Usage: python mixer/automix.py mixer/tracks_demo.json out_dir
Every decision is written to out_dir/mix.json so a single transition can be inspected or re-rendered.
"""
import json, math, os, subprocess, sys, tempfile, urllib.request

import numpy as np
import librosa
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

SR = 44100
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CAMELOT_MAJ = {0: "8B", 7: "9B", 2: "10B", 9: "11B", 4: "12B", 11: "1B", 6: "2B", 1: "3B", 8: "4B", 3: "5B", 10: "6B", 5: "7B"}
CAMELOT_MIN = {9: "8A", 4: "9A", 11: "10A", 6: "11A", 1: "12A", 8: "1A", 3: "2A", 10: "3A", 5: "4A", 0: "5A", 7: "6A", 2: "7A"}
MAJ_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


# ---------------------------------------------------------------- helpers
def log(*a):
    print(*a, flush=True)


def fetch(track, work):
    mp3 = os.path.join(work, track["id"] + ".mp3")
    wav = os.path.join(work, track["id"] + ".wav")
    if not os.path.exists(mp3):
        req = urllib.request.Request(track["url"], headers={"User-Agent": "MuZiC-automix/0.1"})
        with urllib.request.urlopen(req, timeout=120) as r, open(mp3, "wb") as f:
            f.write(r.read())
    # loudness-normalise every song to the same level (EBU R128, -14 LUFS) and decode to 44.1k stereo wav
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", str(SR), "-ac", "2", wav], check=True)
    audio, _ = sf.read(wav, dtype="float32", always_2d=True)
    return audio  # (n, 2)


def camelot_ok(a, b):
    if a == b:
        return True
    na, la, nb, lb = int(a[:-1]), a[-1], int(b[:-1]), b[-1]
    if la == lb and (abs(na - nb) == 1 or abs(na - nb) == 11):
        return True
    return na == nb and la != lb


def bpm_gap(a, b):
    """relative tempo gap, allowing half/double time (6/8 songs are often detected at double)."""
    return min(abs(x - a) / a for x in (b, b * 2, b / 2))


def lowpass(x, hz):
    return sosfiltfilt(butter(4, hz, "low", fs=SR, output="sos"), x, axis=0).astype(np.float32)


def highpass(x, hz):
    return sosfiltfilt(butter(4, hz, "high", fs=SR, output="sos"), x, axis=0).astype(np.float32)


def stretch(x, target_len):
    """time-stretch with Rubber Band (keeps pitch) to exactly target_len samples."""
    if len(x) == 0 or abs(len(x) - target_len) < 32:
        return fit(x, target_len)
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "i.wav"), os.path.join(d, "o.wav")
        sf.write(i, x, SR)
        ratio = target_len / len(x)
        cmd = ["rubberband", "-q", "--fine", "-t", f"{ratio:.6f}", i, o]
        if subprocess.run(cmd, capture_output=True).returncode != 0:
            subprocess.run(["rubberband", "-q", "-t", f"{ratio:.6f}", i, o], check=True, capture_output=True)
        y, _ = sf.read(o, dtype="float32", always_2d=True)
    return fit(y, target_len)


def fit(x, n):
    if len(x) >= n:
        return x[:n]
    return np.vstack([x, np.zeros((n - len(x), 2), np.float32)])


def ramp(n, start, end, shape="eqpow"):
    t = np.linspace(0, 1, n, dtype=np.float32)
    if shape == "eqpow":  # equal-power curve, no volume dip in the middle
        t = np.sin(t * math.pi / 2) ** 2
    return (start + (end - start) * t)[:, None]


# ---------------------------------------------------------------- analysis
def analyse(track, audio):
    mono = librosa.to_mono(audio.T)
    y = librosa.resample(mono, orig_sr=SR, target_sr=22050)
    sr = 22050
    # skip leading silence
    nz = np.nonzero(np.abs(y) > 0.01)[0]
    lead = int(nz[0]) if len(nz) else 0

    hop = 128
    _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, tightness=120)
    raw = librosa.frames_to_samples(beat_frames, hop_length=hop).astype(float)
    raw = raw[raw >= lead]
    # electronic tracks keep one tempo: fit a straight beat grid through the detected beats (removes jitter,
    # gives sub-millisecond tempo precision instead of the coarse frame grid)
    k = np.arange(len(raw))
    T, t0 = np.polyfit(k, raw, 1)
    for _ in range(2):
        res = raw - (t0 + T * k)
        keep = np.abs(res) < 0.2 * T
        if keep.sum() > 16:
            T, t0 = np.polyfit(k[keep], raw[keep], 1)
    tempo = 60.0 * sr / T
    while tempo < 85:
        tempo *= 2
        T /= 2
    while tempo > 170:
        tempo /= 2
        T *= 2
    t0 = t0 % T
    beats = np.arange(t0, len(y), T).astype(int)
    beats = beats[beats >= lead - T / 2]

    # downbeat phase: in 4/4 dance music the kick is strongest on beat 1 of the bar
    lows = librosa.onset.onset_strength(y=librosa.effects.preemphasis(y, coef=-0.97), sr=sr, hop_length=hop)
    bf = librosa.samples_to_frames(beats, hop_length=hop)
    bf = bf[bf < len(lows)]
    phase = int(np.argmax([lows[bf[p::4]].sum() for p in range(4)])) if len(bf) >= 8 else 0
    downbeats = beats[phase::4]

    # key (Krumhansl-Schmuckler on the averaged chroma)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    best = (-9, 0, "maj")
    for k in range(12):
        for prof, mode in ((MAJ_PROFILE, "maj"), (MIN_PROFILE, "min")):
            r = np.corrcoef(np.roll(prof, k), chroma)[0, 1]
            if r > best[0]:
                best = (r, k, mode)
    _, tonic, mode = best
    key = f"{NOTES[tonic]} {'major' if mode == 'maj' else 'minor'}"
    camelot = (CAMELOT_MAJ if mode == "maj" else CAMELOT_MIN)[tonic]

    # loudness per bar -> energy, hook, first "beat is in" bar
    scale = SR / sr
    db = (downbeats * scale).astype(int)
    rms_bar = []
    for i in range(len(db) - 1):
        seg = audio[db[i]:db[i + 1]]
        rms_bar.append(float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0)
    rms_bar = np.array(rms_bar) if rms_bar else np.array([0.0])
    # energy = loudness of the busy part + rhythmic density
    onset_rate = float(np.mean(librosa.onset.onset_strength(y=y, sr=sr)))
    energy_raw = float(np.percentile(rms_bar, 75)) * 10 + onset_rate * 0.3

    strong = np.nonzero(rms_bar >= 0.6 * rms_bar.max())[0]
    first_strong = int(strong[0]) if len(strong) else 0
    win = 8
    limit = max(1, int(len(rms_bar) * 0.7))
    sums = [rms_bar[i:i + win].mean() for i in range(0, max(1, limit - win))]
    hook = int(np.argmax(sums)) if sums else first_strong

    return {
        "id": track["id"], "bpm": round(tempo, 1), "key": key, "camelot": camelot,
        "duration": round(len(audio) / SR, 1), "downbeats": db.tolist(),
        "first_strong_bar": first_strong, "hook_bar": hook, "energy_raw": energy_raw,
    }


# ---------------------------------------------------------------- ordering (the "brain")
def energy_target(pos, n):
    """warm start, climb, peak around 70%, small release at the end (waves, not a straight line)."""
    x = pos / max(1, n - 1)
    return 0.35 + 0.6 * math.sin(min(x / 0.75, 1) * math.pi / 2) - (0.15 if x > 0.9 else 0)


def pair_score(a, b, ta, tb, pos, n, lang_run):
    s = 0.0
    if camelot_ok(a["camelot"], b["camelot"]):
        s += 4
    g = bpm_gap(a["bpm"], b["bpm"])
    s += 4 if g <= 0.03 else 3 if g <= 0.06 else 1.5 if g <= 0.10 else -min(3.0, g * 10)
    s -= 2.5 * abs(b["energy"] - energy_target(pos, n))
    if ta["artist"] == tb["artist"]:
        s -= 0.7  # avoid long runs of one artist
    if tb["lang"] == ta["lang"] and lang_run >= 3:
        s -= 2.5  # a DJ switches lane after 3-4 songs of one kind
    return s


def order(tracks, an):
    n = len(tracks)
    idx = list(range(n))
    beams = [([i], -4 * abs(an[i]["energy"] - energy_target(0, n))) for i in idx]
    for pos in range(1, n):
        nxt = []
        for seq, sc in beams:
            last = seq[-1]
            run = 1
            for k in range(len(seq) - 2, -1, -1):
                if tracks[seq[k]]["lang"] == tracks[last]["lang"]:
                    run += 1
                else:
                    break
            for j in idx:
                if j in seq:
                    continue
                nxt.append((seq + [j], sc + pair_score(an[last], an[j], tracks[last], tracks[j], pos, n, run)))
        nxt.sort(key=lambda t: -t[1])
        beams = nxt[:60]
    return beams[0][0]


# ---------------------------------------------------------------- transitions
def choose_transition(a, b, ta, tb):
    g = bpm_gap(a["bpm"], b["bpm"])
    keys = camelot_ok(a["camelot"], b["camelot"])
    lang_change = ta["lang"] != tb["lang"]
    jump = b["energy"] - a["energy"]
    drift = " ואז חזרה הדרגתית לקצב המקורי של השיר החדש" if g > 0.015 else ""
    if g <= 0.10 and keys and not lang_change:
        return "blend", "BPM וסולם תואמים: מיקס ארוך של 16 תיבות עם החלפת בס" + drift
    if g <= 0.10 and keys and lang_change:
        return "blend", "שינוי שפה אבל קצב וסולם תואמים: מיקס ארוך, הקהל לא מרגיש תפר" + drift
    if g <= 0.10 and not keys:
        return "filter", "קצב קרוב אבל הסולמות מתנגשים: פילטר שמסתיר את ההתנגשות במשך 8 תיבות" + drift
    if jump > 0.25:
        return "cut", "קפיצת אנרגיה: קאט חד על תחילת תיבה, ישר לפזמון/דרופ של השיר הבא"
    return "echo", "קצב רחוק מדי לסנכרון: אקו־אאוט של השיר היוצא והשיר הבא נכנס על הביט הראשון"


def bars_len(an, bar_i, nbars):
    db = an["downbeats"]
    if bar_i + nbars < len(db):
        return db[bar_i + nbars] - db[bar_i]
    return int(nbars * 4 * 60 / an["bpm"] * SR)


def render_transition(kind, A, a_an, mo_bar, B, b_an, mi_bar):
    """returns (audio of the transition region, sample in B where B continues)."""
    beat_a = int(60 / a_an["bpm"] * SR)
    mo = a_an["downbeats"][mo_bar]
    mi = b_an["downbeats"][mi_bar] if mi_bar < len(b_an["downbeats"]) else 0

    if kind in ("blend", "filter"):
        nb = 16 if kind == "blend" else 8
        L = bars_len(a_an, mo_bar, nb)
        a_seg = fit(A[mo:mo + L], L)
        lb = bars_len(b_an, mi_bar, nb)
        b_seg = stretch(B[mi:mi + lb], L)  # B runs at A's tempo during the overlap
        if kind == "blend":
            swap = int(L * 12 / 16)
            fade = beat_a
            a_low, b_low = lowpass(a_seg, 150), lowpass(b_seg, 150)
            a_hi, b_hi = a_seg - a_low, b_seg - b_low
            g_b_hi = np.vstack([ramp(L // 2, 0, 1), np.ones((L - L // 2, 1), np.float32)])
            g_a_hi = np.vstack([np.ones((L // 2, 1), np.float32), ramp(L - L // 2, 1, 0)])
            g_a_low = np.vstack([np.ones((swap, 1), np.float32), ramp(fade, 1, 0, "lin"),
                                 np.zeros((L - swap - fade, 1), np.float32)])
            g_b_low = 1 - g_a_low
            out = a_hi * g_a_hi + a_low * g_a_low + b_hi * g_b_hi + b_low * g_b_low
        else:
            a_dark = lowpass(a_seg, 300)
            b_thin = highpass(b_seg, 900)
            t = ramp(L, 0, 1, "lin")
            a_part = (a_seg * (1 - t) + a_dark * t) * ramp(L, 1, 0)
            b_part = (b_thin * (1 - t) + b_seg * t) * ramp(L, 0, 1)
            out = a_part + b_part
        # tempo drift back: B's next 16 bars in 4 steps, from A's tempo back to B's own tempo
        cont = mi + lb
        if abs(a_an["bpm"] - b_an["bpm"]) / b_an["bpm"] > 0.015:
            steps = []
            bar0 = mi_bar + nb
            for k in range(4):
                n_native = bars_len(b_an, bar0 + 4 * k, 4)
                tempo = a_an["bpm"] + (b_an["bpm"] - a_an["bpm"]) * (k + 1) / 5
                chunk = B[cont:cont + n_native]
                steps.append(stretch(chunk, int(len(chunk) * b_an["bpm"] / tempo)))
                cont += n_native
            out = np.vstack([out] + steps)
        return out, cont

    if kind == "echo":
        L = 8 * beat_a  # two bars of echo tail
        dry = fit(A[mo - beat_a:mo], beat_a) if mo >= beat_a else fit(A[mo:mo + beat_a], beat_a)
        src = highpass(dry, 250)
        tail = np.zeros((L, 2), np.float32)
        for k in range(8):  # feedback delay of one beat
            g = 0.6 ** (k + 1)
            tail[k * beat_a:(k + 1) * beat_a] += src * g
        enter = 4 * beat_a  # new song drops on the downbeat after one bar of echo
        b_part = fit(B[mi:mi + (L - enter)], L - enter)
        b_part[: beat_a // 8] *= ramp(beat_a // 8, 0, 1, "lin")
        out = tail
        out[enter:] += b_part
        return out, mi + (L - enter)

    # cut: hard switch on the downbeat with a 15 ms de-click
    hook = b_an["downbeats"][min(b_an["hook_bar"], len(b_an["downbeats"]) - 1)]
    x = int(0.015 * SR)
    a_tail = fit(A[mo:mo + x], x) * ramp(x, 1, 0, "lin")
    b_head = fit(B[hook:hook + x], x) * ramp(x, 0, 1, "lin")
    return a_tail + b_head, hook + x


def bar_at(an, sample):
    db = np.array(an["downbeats"])
    i = int(np.searchsorted(db, sample))
    return min(i, len(db) - 1)


# ---------------------------------------------------------------- main
def main(cfg_path, out_dir):
    cfg = json.load(open(cfg_path))
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(out_dir, "_work")
    os.makedirs(work, exist_ok=True)
    tracks = cfg["tracks"]
    audio, an = [], []
    for t in tracks:
        log("analysing", t["title"])
        a = fetch(t, work)
        audio.append(a)
        an.append(analyse(t, a))
    e = np.array([x["energy_raw"] for x in an])
    for x, v in zip(an, (e - e.min()) / max(1e-9, e.max() - e.min())):
        x["energy"] = round(float(v), 2)
    for t, x in zip(tracks, an):
        log(f"  {t['title']:<18} {x['bpm']:6.1f} BPM  {x['key']:<9} {x['camelot']:<4} energy {x['energy']}")

    seq = order(tracks, an)
    log("order:", [tracks[i]["title"] for i in seq])

    play = int(cfg.get("play_seconds", 80) * SR)
    pieces, timeline, cursor_out = [], [], 0
    i0 = seq[0]
    start = an[i0]["downbeats"][0]
    cur = start
    for pos, i in enumerate(seq):
        A, a_an, ta = audio[i], an[i], tracks[i]
        entry_time = cursor_out
        last = pos == len(seq) - 1
        # mix-out: a downbeat ~play seconds after we entered, aligned to an 8-bar phrase from the entry
        entry_bar = bar_at(a_an, cur)
        want = bar_at(a_an, cur + play)
        mo_bar = entry_bar + max(8, ((want - entry_bar) // 8) * 8)
        mo_bar = min(mo_bar, max(entry_bar + 1, len(a_an["downbeats"]) - 18))
        mo = a_an["downbeats"][mo_bar]
        if last:
            end = min(len(A), mo + bars_len(a_an, mo_bar, 8))
            body = A[cur:end].copy()
            f = min(len(body), bars_len(a_an, mo_bar, 8))
            body[-f:] *= ramp(f, 1, 0)
            pieces.append(body)
            cursor_out += len(body)
            timeline.append({"pos": pos + 1, "id": ta["id"], "start": round(entry_time / SR, 1)})
            break
        pieces.append(A[cur:mo])
        cursor_out += max(0, mo - cur)
        j = seq[pos + 1]
        B, b_an, tb = audio[j], an[j], tracks[j]
        kind, why = choose_transition(a_an, b_an, ta, tb)
        mi_bar = 0 if kind in ("blend", "filter") else b_an["first_strong_bar"]
        try:
            region, b_cur = render_transition(kind, A, a_an, mo_bar, B, b_an, mi_bar)
        except Exception as ex:  # never fail the whole mix because of one pair
            log("  transition failed, falling back to echo:", ex)
            kind, why = "echo", "גיבוי: אקו־אאוט"
            region, b_cur = render_transition("echo", A, a_an, mo_bar, B, b_an, b_an["first_strong_bar"])
        timeline.append({
            "pos": pos + 1, "id": ta["id"], "start": round(entry_time / SR, 1),
            "transition": {"to": tb["id"], "type": kind, "why": why, "at": round(cursor_out / SR, 1),
                           "length_s": round(len(region) / SR, 1),
                           "bpm": [a_an["bpm"], b_an["bpm"]], "camelot": [a_an["camelot"], b_an["camelot"]],
                           "out_bar": int(mo_bar), "in_bar": int(mi_bar)},
        })
        pieces.append(region)
        cursor_out += len(region)
        cur = b_cur

    mix = np.vstack(pieces)
    wav = os.path.join(work, "mix.wav")
    sf.write(wav, mix, SR)
    mp3 = os.path.join(out_dir, "mix.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", "alimiter=limit=0.95",
                    "-codec:a", "libmp3lame", "-b:a", "160k", mp3], check=True)

    tmeta = {t["id"]: {k: t[k] for k in ("title", "artist", "lang", "style", "license", "page")} for t in tracks}
    for x in an:
        x.pop("downbeats", None)
        x.pop("energy_raw", None)
    json.dump({"title": cfg["title"], "duration": round(len(mix) / SR, 1), "tracks": tmeta,
               "analysis": {x["id"]: x for x in an}, "timeline": timeline},
              open(os.path.join(out_dir, "mix.json"), "w"), ensure_ascii=False, indent=1)
    log("done:", mp3, round(len(mix) / SR / 60, 1), "min")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
