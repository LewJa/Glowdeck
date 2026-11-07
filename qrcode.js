/* Minimal QR code generator (byte mode, error correction M, versions 1-10 = up to 213 bytes).
   window.qrSvg(text, {scale, margin}) -> SVG markup (black on white, with the required quiet zone). */
(function (root) {
  "use strict";
  // [EC codewords per block, [[blocks, data codewords per block], ...]] for level M
  const EC = {1: [10, [[1, 16]]], 2: [16, [[1, 28]]], 3: [26, [[1, 44]]], 4: [18, [[2, 32]]], 5: [24, [[2, 43]]],
    6: [16, [[4, 27]]], 7: [18, [[4, 31]]], 8: [22, [[2, 38], [2, 39]]], 9: [22, [[3, 36], [2, 37]]],
    10: [26, [[4, 43], [1, 44]]]};
  const ALIGN = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34], 7: [6, 22, 38],
    8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]};

  const mul = (x, y) => { let z = 0; for (let i = 7; i >= 0; i--) { z = (z << 1) ^ ((z >>> 7) * 0x11D); z ^= ((y >>> i) & 1) * x; } return z; };
  function rsDivisor(deg) {
    const r = new Array(deg).fill(0); r[deg - 1] = 1; let root = 1;
    for (let i = 0; i < deg; i++) {
      for (let j = 0; j < deg; j++) { r[j] = mul(r[j], root); if (j + 1 < deg) r[j] ^= r[j + 1]; }
      root = mul(root, 2);
    }
    return r;
  }
  function rsRemainder(data, div) {
    const r = new Array(div.length).fill(0);
    for (const b of data) { const f = b ^ r.shift(); r.push(0); div.forEach((c, i) => { r[i] ^= mul(c, f); }); }
    return r;
  }
  const bit = (x, i) => ((x >>> i) & 1) !== 0;

  function codewords(bytes) {
    let version = 0, dataCap = 0;
    for (let v = 1; v <= 10; v++) {
      const cap = EC[v][1].reduce((a, [n, d]) => a + n * d, 0);
      const countBits = v < 10 ? 8 : 16;
      if (4 + countBits + bytes.length * 8 <= cap * 8) { version = v; dataCap = cap; break; }
    }
    if (!version) throw new Error("text too long for the QR generator");
    const bits = [];
    const put = (val, n) => { for (let i = n - 1; i >= 0; i--) bits.push((val >>> i) & 1); };
    put(0b0100, 4); put(bytes.length, version < 10 ? 8 : 16);
    bytes.forEach(b => put(b, 8));
    put(0, Math.min(4, dataCap * 8 - bits.length));
    while (bits.length % 8) bits.push(0);
    for (let pad = 0xEC; bits.length < dataCap * 8; pad ^= 0xEC ^ 0x11) put(pad, 8);
    const data = [];
    for (let i = 0; i < bits.length; i += 8) data.push(parseInt(bits.slice(i, i + 8).join(""), 2));

    const [ecLen, groups] = EC[version];
    const div = rsDivisor(ecLen), blocks = [];
    let k = 0;
    groups.forEach(([n, d]) => { for (let i = 0; i < n; i++) { const dat = data.slice(k, k + d); k += d; blocks.push({dat, ec: rsRemainder(dat, div)}); } });
    const out = [], maxLen = Math.max(...blocks.map(b => b.dat.length));
    for (let i = 0; i < maxLen; i++) blocks.forEach(b => { if (i < b.dat.length) out.push(b.dat[i]); });
    for (let i = 0; i < ecLen; i++) blocks.forEach(b => out.push(b.ec[i]));
    return {version, out};
  }

  function matrix(text, forceMask) {
    const {version, out} = codewords(Array.from(new TextEncoder().encode(text)));
    const size = version * 4 + 17;
    const m = Array.from({length: size}, () => new Array(size).fill(false));
    const fn = Array.from({length: size}, () => new Array(size).fill(false));
    const setFn = (x, y, dark) => { m[y][x] = dark; fn[y][x] = true; };

    function formatBits(mask) {            // level M = 0b00
      const data = (0 << 3) | mask; let rem = data;
      for (let i = 0; i < 10; i++) rem = (rem << 1) ^ ((rem >>> 9) * 0x537);
      const bits = ((data << 10) | rem) ^ 0x5412;
      for (let i = 0; i <= 5; i++) setFn(8, i, bit(bits, i));
      setFn(8, 7, bit(bits, 6)); setFn(8, 8, bit(bits, 7)); setFn(7, 8, bit(bits, 8));
      for (let i = 9; i < 15; i++) setFn(14 - i, 8, bit(bits, i));
      for (let i = 0; i < 8; i++) setFn(size - 1 - i, 8, bit(bits, i));
      for (let i = 8; i < 15; i++) setFn(8, size - 15 + i, bit(bits, i));
      setFn(8, size - 8, true);
    }
    for (let i = 0; i < size; i++) { setFn(6, i, i % 2 === 0); setFn(i, 6, i % 2 === 0); }
    const finder = (cx, cy) => { for (let dy = -4; dy <= 4; dy++) for (let dx = -4; dx <= 4; dx++) {
      const d = Math.max(Math.abs(dx), Math.abs(dy)), x = cx + dx, y = cy + dy;
      if (x >= 0 && x < size && y >= 0 && y < size) setFn(x, y, d !== 2 && d !== 4); } };
    finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
    const al = ALIGN[version];
    al.forEach((cx, i) => al.forEach((cy, j) => {
      if ((i === 0 && j === 0) || (i === 0 && j === al.length - 1) || (i === al.length - 1 && j === 0)) return;
      for (let dy = -2; dy <= 2; dy++) for (let dx = -2; dx <= 2; dx++) setFn(cx + dx, cy + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
    }));
    formatBits(0);
    if (version >= 7) {
      let rem = version;
      for (let i = 0; i < 12; i++) rem = (rem << 1) ^ ((rem >>> 11) * 0x1F25);
      const bits = (version << 12) | rem;
      for (let i = 0; i < 18; i++) { const a = size - 11 + (i % 3), b = Math.floor(i / 3); setFn(a, b, bit(bits, i)); setFn(b, a, bit(bits, i)); }
    }
    // place data bits in the zigzag
    let i = 0;
    for (let right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (let vert = 0; vert < size; vert++) for (let j = 0; j < 2; j++) {
        const x = right - j, up = ((right + 1) & 2) === 0, y = up ? size - 1 - vert : vert;
        if (!fn[y][x] && i < out.length * 8) { m[y][x] = bit(out[i >>> 3], 7 - (i & 7)); i++; }
      }
    }
    const inv = (mask, x, y) => [(x + y) % 2 === 0, y % 2 === 0, x % 3 === 0, (x + y) % 3 === 0,
      (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0, (x * y) % 2 + (x * y) % 3 === 0,
      ((x * y) % 2 + (x * y) % 3) % 2 === 0, ((x + y) % 2 + (x * y) % 3) % 2 === 0][mask];
    const applyMask = mask => { for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) if (!fn[y][x] && inv(mask, x, y)) m[y][x] = !m[y][x]; };

    function penalty() {
      let p = 0;
      const line = get => {                           // runs and finder-like patterns along one line
        let run = 1, s = "";
        for (let k = 0; k < size; k++) { s += get(k) ? "1" : "0"; if (k && get(k) === get(k - 1)) { run++; if (run === 5) p += 3; else if (run > 5) p++; } else if (k) run = 1; }
        for (const pat of ["000010111010", "010111010000"]) { let at = -1; while ((at = s.indexOf(pat, at + 1)) !== -1) p += 40; }
        // patterns touching the border (treated as light outside)
        const padded = "0000" + s + "0000";
        let n = 0; for (const pat of ["000010111010", "010111010000"]) { let at = -1; while ((at = padded.indexOf(pat, at + 1)) !== -1) n++; }
        const inner = ["000010111010", "010111010000"].reduce((a, pat) => { let c = 0, at = -1; while ((at = s.indexOf(pat, at + 1)) !== -1) c++; return a + c; }, 0);
        p += (n - inner) * 40;
      };
      for (let y = 0; y < size; y++) line(k => m[y][k]);
      for (let x = 0; x < size; x++) line(k => m[k][x]);
      for (let y = 0; y < size - 1; y++) for (let x = 0; x < size - 1; x++) { const c = m[y][x]; if (c === m[y][x + 1] && c === m[y + 1][x] && c === m[y + 1][x + 1]) p += 3; }
      let dark = 0; m.forEach(r => r.forEach(c => { if (c) dark++; }));
      p += (Math.ceil(Math.abs(dark * 20 - size * size * 10) / (size * size)) - 1) * 10;
      return p;
    }
    let best = 0;
    if (forceMask === undefined) {
      let bestP = Infinity;
      for (let mask = 0; mask < 8; mask++) { applyMask(mask); formatBits(mask); const p = penalty(); if (p < bestP) { bestP = p; best = mask; } applyMask(mask); }
    } else best = forceMask;
    applyMask(best); formatBits(best);
    return m;
  }

  function qrSvg(text, opts) {
    opts = opts || {}; const margin = opts.margin === undefined ? 4 : opts.margin, scale = opts.scale || 6;
    const m = matrix(text, opts.mask), n = m.length + margin * 2;
    let d = ""; m.forEach((row, y) => row.forEach((c, x) => { if (c) d += `M${x + margin} ${y + margin}h1v1h-1z`; }));
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${n} ${n}" width="${n * scale}" height="${n * scale}" shape-rendering="crispEdges"><rect width="${n}" height="${n}" fill="#fff"/><path d="${d}" fill="#000"/></svg>`;
  }
  root.qrSvg = qrSvg; root.qrMatrix = matrix;
  if (typeof module !== "undefined") module.exports = {qrSvg, qrMatrix: matrix};
})(typeof window !== "undefined" ? window : globalThis);
