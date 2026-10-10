/* Matsense Reels kit: builders for the app screens the ads show, and the caption engine.
   Everything is built synchronously from data in the page (no fetches, no clocks). */
(function () {
  const P = {
    flame: "M10 2 C10.5 6 15 8 15 12.5 A5 5 0 0 1 5 12.5 C5 10.2 6.3 8.6 7.6 7.4 C7.8 9.2 8.6 10.4 9.8 10.8 C9.2 8 8.6 5 10 2 Z",
    home: "M3 9 L10 3 L17 9 V17 H3 Z M8 17 V12 H12 V17",
    library: "M3 3 H6 V17 H3 Z M8 3 H11 V17 H8 Z M13 4.5 L16 3.7 L18.6 16.2 L15.6 17 Z",
    video: "M2 4 H18 V16 H2 Z M8 7.5 L13 10 L8 12.5 Z",
    check: "M4 10 L8 14 L16 6",
    next: "M4 10 H16 M11 5 L16 10 L11 15",
    back: "M12 4 L6 10 L12 16",
    more: "M5 10 H5.01 M10 10 H10.01 M15 10 H15.01",
    plus: "M10 4 V16 M4 10 H16",
    bookmark: "M5 3 H15 V17 L10 13 L5 17 Z",
    folder: "M2 5 H8 L10 7 H18 V16 H2 Z",
    cup: "M6 3 H14 V8 A4 4 0 0 1 6 8 Z M10 12 V15 M7 17 H13 M6 5 H3 V6 A3 3 0 0 0 6 9 M14 5 H17 V6 A3 3 0 0 1 14 9",
    play: "M6 4 L16 10 L6 16 Z",
  };
  function icon(name, opt) {
    opt = opt || {};
    const c = opt.color || "currentColor";
    const fill = opt.fill ? c : "none";
    const sw = opt.sw || 1.9;
    return `<svg viewBox="0 0 20 20" aria-hidden="true" style="${opt.style || ""}"><path d="${P[name]}" fill="${fill}" stroke="${c}" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }
  const MARK = (accent) => `<svg class="mark" viewBox="0 0 60 60" fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 6H10C7.791 6 6 7.791 6 10V20" stroke="#fff" stroke-width="4"/>
      <path d="M40 6H50C52.209 6 54 7.791 54 10V20" stroke="#fff" stroke-width="4"/>
      <path d="M6 40V50C6 52.209 7.791 54 10 54H20" stroke="#fff" stroke-width="4"/>
      <path d="M54 40V50C54 52.209 52.209 54 50 54H40" stroke="#fff" stroke-width="4"/>
      <path d="M30 19A11 11 0 0 0 19 30" stroke="#fff" stroke-width="3.5"/>
      <path class="arc2" d="M30 41A11 11 0 0 0 41 30" stroke="${accent}" stroke-width="3.5"/>
      <circle class="dot" cx="30" cy="30" r="4" fill="${accent}"/></svg>`;

  const FAM = { sweep: "sweep", pass: "guardpass", near: "nearpass", sweepatt: "sweepatt", sub: "subatt", pen: "penalty", pull: "guardpull", scr: "scramble", rev: "reversal" };
  const chip = (fam, txt) => `<span class="chip" style="color:var(--ev-${FAM[fam]}-fg);background:var(--ev-${FAM[fam]}-bg)">${txt}</span>`;
  const mmss = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;

  // The match screen: top bar, player (a slot the page fills with a <video>), the strip, Breakdown, rows.
  function matchScreen(o) {
    const ticks = (o.events || []).map((e, i) => `<i class="tick ${e.side} ev-tick" data-i="${i}" id="${o.id}-tick-${i}"
        style="left:${(100 * e.t) / o.duration}%;height:${e.key ? 20 : 11}px;background:var(--ev-${FAM[e.fam]}-mark)"></i>`).join("");
    const rows = (o.rows || []).map((r, i) => `<div class="row card" id="${o.id}-row-${i}">
        <span class="time">${mmss(r.t)}</span><span class="sq ${r.side === "b" ? "o" : ""}"></span>
        <div class="mid2">${chip(r.fam, r.name)}<div class="who">${r.who}</div></div>
        <span class="pts">${r.pts}</span><span style="width:20px;height:20px;color:var(--ink-muted)">${icon("bookmark")}</span></div>`).join("");
    return `<div class="pad">
      <div class="topbar"><div class="circle">${icon("back")}</div>
        <div style="flex:1"><div class="t-title">${o.title}</div><div class="t-sub">${o.sub}</div></div>
        <div class="circle">${icon("more")}</div></div>
      <div class="player" id="${o.id}-player"><div class="tc" id="${o.id}-tc">${o.tc || "0:00"}</div><div class="bar"><i id="${o.id}-prog"></i></div></div>
      <div class="strip card"><div class="mid"></div><span class="lab a">${o.a}</span><span class="lab b">${o.b}</span>
        <div class="area">${ticks}<i class="head" id="${o.id}-head" style="left:0%"></i></div></div>
      <div class="brandbar"><span class="dot">${icon("bookmark", { color: "#5d55e6", fill: true })}</span><span class="lbl">Breakdown</span><span class="pill">${o.toSort || "3 to sort"}</span>
        <span style="width:22px;height:22px;margin-right:6px">${icon("next")}</span></div>
      <div id="${o.id}-rows">${rows}</div></div>
      <div class="tabbar"><span>${icon("home")}</span><span style="color:var(--brand-ink)">${icon("video")}</span><span>${icon("library")}</span>
        <span class="plus">${icon("plus", { sw: 2.4 })}</span></div>`;
  }

  // Fight breakdown: the Strong / Weak / Improve switch and its areas.
  function breakdownScreen(o) {
    const seg = ["Strong", "Weak", "Improve"].map((s, i) => `<div id="${o.id}-seg-${i}" class="${i === (o.sel || 0) ? "sel" : ""}">${s}</div>`).join("");
    const areas = (o.areas || []).map((a, i) => `<div class="area-card card" id="${o.id}-area-${i}">
        <div class="h">${a.h}</div><div class="times">${a.times}</div><div class="p">${a.p}</div>
        <div class="acts"><span class="btn brand" id="${o.id}-train-${i}">Train</span><span class="btn">Keep</span></div></div>`).join("");
    return `<div class="pad">
      <div class="topbar"><div class="circle">${icon("back")}</div>
        <div style="flex:1"><div class="t-sub" style="margin:0">${o.match}</div><div class="t-title">Fight breakdown</div></div></div>
      <div class="card" style="margin-top:14px;padding:12px 14px;font-weight:800;font-size:14px;line-height:1.35">${o.result}</div>
      <div class="seg">${seg}</div><div id="${o.id}-areas">${areas}</div></div>`;
  }

  function taskCard(o) {
    return `<div class="taskcard card" id="${o.id}">
      <div class="top"><span class="badge" style="background:var(--task-${o.n})">${o.n}</span><span class="nm">${o.name}</span>
        <span class="pc" id="${o.id}-pc">${o.pc || 0}%</span></div>
      <div class="track"><i id="${o.id}-bar" style="background:var(--task-${o.n}-mark);transform:scaleX(${(o.pc || 0) / 100})"></i></div>
      <div class="meta"><span>${o.notes || 1} notes</span><span id="${o.id}-sess">${o.sess || 0} sessions</span></div></div>`;
  }

  function weekStrip(o) {
    const d = ["M", "T", "W", "T", "F", "S", "S"];
    return `<div class="days card" id="${o.id}">${d.map((x, i) => {
      const on = (o.on || []).includes(i);
      return `<div class="day ${on ? "on" : ""}" id="${o.id}-d${i}"><div class="fl" style="color:${on ? "var(--streak)" : "var(--ink-subtle)"}">
        <span style="width:20px;height:20px">${icon("flame", { fill: on })}</span></div><div class="d">${x}</div><div class="tm">${(o.times || {})[i] || ""}</div></div>`;
    }).join("")}</div>`;
  }

  // Captions: words [{text,start,end}] grouped into pages; pages never cross a line break
  // in `breaks` (a list of times) and hold at most `max` words. `skip` hides word ranges [a,b].
  function captions(tl, el, words, opt) {
    opt = opt || {};
    const max = opt.max || 4, skip = opt.skip || [], hot = opt.hot || [];
    const ws = words.filter((w) => !skip.some(([a, b]) => w.start >= a && w.start < b));
    const pages = []; let cur = [];
    ws.forEach((w, i) => {
      cur.push(w);
      const nx = ws[i + 1];
      const endsSentence = /[.?!:,]$/.test(w.text);
      const gap = nx ? nx.start - w.end : 9;
      const nextCloses = nx && /[.?!]$/.test(nx.text) && !endsSentence && cur.length === max;
      if (!nx || endsSentence || gap > 0.45 || (cur.length >= max && !nextCloses)) { pages.push(cur); cur = []; }
    });
    pages.forEach((pg, pi) => {
      const div = document.createElement("div");
      div.className = "cap-page";
      pg.forEach((w) => {
        const s = document.createElement("span");
        const clean = w.text.replace(/^[^A-Za-z0-9']+/, "").replace(/[.,:;]+$/, "");
        s.className = "cw" + (hot.some((h) => clean.toLowerCase().startsWith(h)) ? " k" : "");
        s.textContent = clean;
        div.appendChild(s);
      });
      el.appendChild(div);
      const t0 = pg[0].start - 0.04;
      const nextStart = pages[pi + 1] ? pages[pi + 1][0].start - 0.04 : pg[pg.length - 1].end + 0.6;
      const t1 = Math.min(nextStart, pg[pg.length - 1].end + 0.6);
      tl.set(div, { opacity: 0 }, 0);
      tl.set(div, { opacity: 1 }, t0);
      div.querySelectorAll(".cw").forEach((s, j) => {
        tl.fromTo(s, { opacity: 0.0, y: 16, scale: 0.92 }, { opacity: 1, y: 0, scale: 1, duration: 0.14, ease: "power2.out" }, pg[j].start - 0.03);
      });
      tl.set(div, { opacity: 0 }, t1);
    });
  }

  // Seeded PRNG for any random-looking placement.
  function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

  window.K = { icon, MARK, chip, mmss, matchScreen, breakdownScreen, taskCard, weekStrip, captions, rng, FAM };
})();
