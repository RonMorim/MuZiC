// MuZiC in-browser song analyser.
// Finds a song on iTunes (free, no key), streams its official 30-second preview into memory
// (nothing is saved to disk) and estimates tempo (BPM) and key (Camelot). Runs entirely in the browser.
(function () {
  const SR = 22050, N = 1024, HOP = 256;
  const NOTES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  const MAJ = [6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88];
  const MIN = [6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17];
  const CAM_MAJ = {0:'8B',7:'9B',2:'10B',9:'11B',4:'12B',11:'1B',6:'2B',1:'3B',8:'4B',3:'5B',10:'6B',5:'7B'};
  const CAM_MIN = {9:'8A',4:'9A',11:'10A',6:'11A',1:'12A',8:'1A',3:'2A',10:'3A',5:'4A',0:'5A',7:'6A',2:'7A'};

  // radix-2 FFT (in place) for any power-of-two size
  const TABLES = {};
  function tables(n) {
    if (TABLES[n]) return TABLES[n];
    const rev = new Uint32Array(n); for (let i = 0, j = 0; i < n; i++) { rev[i] = j; let b = n >> 1; while (j & b) { j ^= b; b >>= 1; } j |= b; }
    const cos = new Float64Array(n / 2), sin = new Float64Array(n / 2);
    for (let i = 0; i < n / 2; i++) { cos[i] = Math.cos(2 * Math.PI * i / n); sin[i] = -Math.sin(2 * Math.PI * i / n); }
    const win = new Float64Array(n); for (let i = 0; i < n; i++) win[i] = 0.5 - 0.5 * Math.cos(2 * Math.PI * i / n);
    return TABLES[n] = {rev, cos, sin, win};
  }
  function fft(re, im) {
    const n = re.length, {rev, cos, sin} = tables(n);
    for (let i = 0; i < n; i++) { const j = rev[i]; if (j > i) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (let size = 2; size <= n; size <<= 1) {
      const half = size >> 1, step = n / size;
      for (let i = 0; i < n; i += size) for (let j = 0, k = 0; j < half; j++, k += step) {
        const a = i + j, b = a + half;
        const tr = re[b] * cos[k] - im[b] * sin[k], ti = re[b] * sin[k] + im[b] * cos[k];
        re[b] = re[a] - tr; im[b] = im[a] - ti; re[a] += tr; im[a] += ti;
      }
    }
  }

  // key: chroma from a long FFT (fine frequency resolution), 100-2000 Hz, per-frame normalised
  function keyOf(x) {
    const n = 8192, {win} = tables(n), re = new Float64Array(n), im = new Float64Array(n), chroma = new Float64Array(12);
    const pc = new Int8Array(n / 2).fill(-1);
    for (let k = 1; k < n / 2; k++) { const f = k * SR / n; if (f >= 100 && f <= 2000) pc[k] = ((Math.round(12 * Math.log2(f / 440)) + 9) % 12 + 12) % 12; }
    for (let o = 0; o + n <= x.length; o += n / 2) {
      for (let i = 0; i < n; i++) { re[i] = x[o + i] * win[i]; im[i] = 0; }
      fft(re, im);
      const fr = new Float64Array(12);
      for (let k = 1; k < n / 2; k++) if (pc[k] >= 0) {
        const f = k * SR / n, cents = 1200 * Math.log2(f / 440) - 100 * Math.round(12 * Math.log2(f / 440));
        if (Math.abs(cents) > 35) continue;                       // only bins close to a note centre
        fr[pc[k]] += Math.sqrt(re[k] * re[k] + im[k] * im[k]);
      }
      const mx = Math.max(...fr) || 1; for (let i = 0; i < 12; i++) chroma[i] += fr[i] / mx;
    }
    let kb = -2, tonic = 0, mode = 'maj';
    const corr = (p, r) => { let mp = 0, mc = 0; for (let i = 0; i < 12; i++) { mp += p[(i - r + 12) % 12]; mc += chroma[i]; } mp /= 12; mc /= 12; let num = 0, dp = 0, dc = 0; for (let i = 0; i < 12; i++) { const u = p[(i - r + 12) % 12] - mp, v = chroma[i] - mc; num += u * v; dp += u * u; dc += v * v; } return num / Math.sqrt(dp * dc || 1); };
    for (let r = 0; r < 12; r++) for (const [p, m] of [[MAJ, 'maj'], [MIN, 'min']]) { const v = corr(p, r); if (v > kb) { kb = v; tonic = r; mode = m; } }
    return {key: `${NOTES[tonic]} ${mode === 'maj' ? 'major' : 'minor'}`, camelot: (mode === 'maj' ? CAM_MAJ : CAM_MIN)[tonic], keyConfidence: Math.round(kb * 100) / 100};
  }

  function analyse(x) {
    const {win} = tables(N);
    const frames = Math.floor((x.length - N) / HOP);
    const flux = new Float64Array(frames);
    const re = new Float64Array(N), im = new Float64Array(N);
    let prev = new Float64Array(N / 2), cur = new Float64Array(N / 2);
    for (let t = 0; t < frames; t++) {
      const o = t * HOP;
      for (let i = 0; i < N; i++) { re[i] = x[o + i] * win[i]; im[i] = 0; }
      fft(re, im);
      let fl = 0;
      for (let k = 1; k < N / 2; k++) {
        const m = Math.sqrt(re[k] * re[k] + im[k] * im[k]);
        cur[k] = Math.log1p(100 * m);
        const d = cur[k] - prev[k]; if (d > 0) fl += k < 60 ? 2 * d : d;   // weight the low end: kicks carry the beat
      }
      flux[t] = fl; const sw = prev; prev = cur; cur = sw;
    }
    // onset envelope: remove the slow trend
    const env = new Float64Array(frames), W = 16;
    for (let t = 0; t < frames; t++) { let s = 0, c = 0; for (let j = Math.max(0, t - W); j < Math.min(frames, t + W); j++) { s += flux[j]; c++; } env[t] = Math.max(0, flux[t] - s / c); }
    // autocorrelation over 70..180 BPM, with a soft preference for dance tempos
    const fps = SR / HOP, scores = [];
    let best = 0, bestLag = 0;
    const minLag = Math.floor(fps * 60 / 180), maxLag = Math.ceil(fps * 60 / 70);
    const ac = lag => { let s = 0; for (let t = lag; t < frames; t++) s += env[t] * env[t - lag]; return s / (frames - lag); };
    for (let lag = minLag; lag <= maxLag; lag++) scores[lag] = ac(lag);
    for (let lag = minLag; lag <= maxLag; lag++) {
      // a real beat also repeats every 2 and 4 beats; a 3/4 or 4/3 "ghost" tempo does not
      const s = scores[lag] + 0.5 * ac(2 * lag) + 0.25 * ac(4 * lag);
      const bpm = 60 * fps / lag, prior = Math.exp(-0.5 * Math.pow(Math.log2(bpm / 118) / 0.5, 2));
      if (s * prior > best) { best = s * prior; bestLag = lag; }
    }
    // parabolic refinement of the peak
    let lag = bestLag;
    const a = scores[bestLag - 1], b = scores[bestLag], c = scores[bestLag + 1];
    if (a !== undefined && c !== undefined) { const d = (a - c) / (2 * (a - 2 * b + c)); if (Math.abs(d) < 1) lag += d; }
    const bpm = 60 * fps / lag;
    return {bpm: Math.round(bpm * 10) / 10, ...keyOf(x)};
  }

  async function find(query, country) {
    const url = `https://itunes.apple.com/search?media=music&entity=song&limit=1&country=${country}&term=${encodeURIComponent(query)}`;
    const r = await fetch(url); if (!r.ok) throw new Error('iTunes ' + r.status);
    const j = await r.json(); return j.results && j.results[0];
  }

  // query: "song - artist". Returns {title, artist, duration, bpm, camelot, key, link} or null.
  async function lookup(query) {
    const q = query.replace(/\s+[-–]\s+/, ' ');
    const he = /[֐-׿]/.test(query);
    let hit = await find(q, he ? 'il' : 'us');
    if (!hit) hit = await find(q, he ? 'us' : 'il');
    if (!hit || !hit.previewUrl) return hit ? {title: hit.trackName, artist: hit.artistName, duration: Math.round(hit.trackTimeMillis / 1000), link: hit.trackViewUrl} : null;
    const buf = await (await fetch(hit.previewUrl)).arrayBuffer();
    const Ctx = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    const audio = await new Promise((ok, bad) => new Ctx(1, SR, SR).decodeAudioData(buf, ok, bad));
    const x = audio.getChannelData(0);
    const an = analyse(x.subarray(Math.floor(SR * 1), Math.max(Math.floor(SR * 1) + SR * 8, x.length - SR * 2)));
    return {title: hit.trackName, artist: hit.artistName, duration: Math.round(hit.trackTimeMillis / 1000), link: hit.trackViewUrl, ...an};
  }

  window.MuzicAnalyzer = {lookup, analyse};
})();
