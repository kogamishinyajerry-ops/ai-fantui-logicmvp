/*
 * timeseries_chart.js — shared multi-lane SVG timeseries renderer.
 *
 * Used by:
 *   - /fan_sim_panel.html      (GET /api/monitor-timeline, FANTUI)
 *   - /fan_console.html        (POST /api/fantui/tick, FANTUI live)
 *   - /c919_etras_panel/       (POST /api/tick, C919 live)
 *
 * Payload shape (matches the existing GET /api/monitor-timeline contract):
 *   {
 *     time_start_s: number,
 *     time_end_s:   number,
 *     series: [{
 *       id:           string,
 *       label:        string,
 *       color:        string,
 *       unit?:        string,
 *       display_min?: number,
 *       display_max?: number,
 *       samples:      Array<[t_s, value]>,
 *     }],
 *     events?: [{ time_s, label, detail? }],
 *   }
 *
 * Usage:
 *   const chart = TimeseriesChart.create({
 *     svg: document.getElementById('my-svg'),
 *     legend: document.getElementById('my-legend'),
 *     width: 1000, height: 420,
 *     laneLabels: ['INPUT','LOGIC','POWER','SENSOR','CMD'],
 *     laneSeries: { INPUT: ['ra','tra'], LOGIC: [...], ... },
 *   });
 *   chart.setData(payload);
 *   chart.startReplay();
 *   chart.stopReplay();
 *   chart.clear();
 *
 * Design notes:
 *   - Self-contained: no external deps, plain IIFE exposing window.TimeseriesChart.
 *   - Re-renders fully on every setData (small-N, fine for sub-kHz tick rate).
 *   - Boolean/discrete signals plot with stepped polylines automatically when
 *     the series has display_min=0, display_max=1 and integer-ish samples.
 */
(function (global) {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";

  function svgEl(tag, attrs) {
    const el = document.createElementNS(SVG_NS, tag);
    for (const [k, v] of Object.entries(attrs || {})) el.setAttribute(k, v);
    return el;
  }

  function create(opts) {
    if (!opts || !opts.svg) throw new Error("TimeseriesChart.create requires opts.svg");
    const svg = opts.svg;
    const legend = opts.legend || null;
    const progress = opts.progress || null;

    const W = opts.width  || 1000;
    const H = opts.height || 420;
    const PAD_LEFT   = opts.padLeft   != null ? opts.padLeft   : 52;
    const PAD_RIGHT  = opts.padRight  != null ? opts.padRight  : 24;
    const PAD_TOP    = opts.padTop    != null ? opts.padTop    : 12;
    const PAD_BOTTOM = opts.padBottom != null ? opts.padBottom : 26;
    const LANE_GAP   = opts.laneGap   != null ? opts.laneGap   : 4;

    const laneLabels = (opts.laneLabels || []).slice();
    const laneSeries = opts.laneSeries || {};
    // Lane height is computed to fill remaining vertical space evenly.
    const chartH = H - PAD_TOP - PAD_BOTTOM;
    const LANE_H = laneLabels.length > 0
      ? (chartH - LANE_GAP * (laneLabels.length - 1)) / laneLabels.length
      : chartH;
    const TOTAL_LANE_H = (LANE_H + LANE_GAP) * laneLabels.length - LANE_GAP;
    const CHART_W = W - PAD_LEFT - PAD_RIGHT;

    // Palette for background bands; dark-theme friendly.
    const BG_EVEN = opts.bgEven || "#091520";
    const BG_ODD  = opts.bgOdd  || "#0b1624";
    const AXIS    = opts.axis   || "#1e3050";
    const TEXT_DIM= opts.textDim|| "#46597a";
    const TICK    = opts.tick   || "#6a7d95";
    const EVENT   = opts.event  || "#f5c518";
    const CURSOR  = opts.cursor || "#00e5a0";

    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("width", W);
    svg.setAttribute("height", H);

    let payload = null;
    let cursorLine = null;
    let replayTimer = null;

    function scaleX(t, tStart, tEnd) {
      if (tEnd <= tStart) return PAD_LEFT;
      return PAD_LEFT + ((t - tStart) / (tEnd - tStart)) * CHART_W;
    }
    function laneTop(idx) {
      return PAD_TOP + idx * (LANE_H + LANE_GAP);
    }
    function scaleY(norm, top) {
      const inset = 4;
      return top + LANE_H - inset - norm * (LANE_H - 2 * inset);
    }

    function seriesMap() {
      if (!payload || !payload.series) return new Map();
      return new Map(payload.series.map((s) => [s.id, s]));
    }

    function clear() {
      payload = null;
      cursorLine = null;
      svg.innerHTML = "";
      if (legend) legend.innerHTML = "";
      if (progress) progress.textContent = "";
    }

    function setData(next) {
      payload = next;
      render();
    }

    function render() {
      svg.innerHTML = "";
      if (!payload) return;

      const tStart = payload.time_start_s != null ? payload.time_start_s : 0;
      // Guard against zero-span timelines by widening the window slightly.
      const tEndRaw = payload.time_end_s != null ? payload.time_end_s : (tStart + 1);
      const tEnd = tEndRaw > tStart ? tEndRaw : tStart + 1;
      const smap = seriesMap();

      // Background frame
      svg.appendChild(svgEl("rect", {
        x: 0, y: 0, width: W, height: H, fill: BG_ODD,
      }));

      // Lane bands + labels
      laneLabels.forEach((lane, li) => {
        const top = laneTop(li);
        svg.appendChild(svgEl("rect", {
          x: PAD_LEFT, y: top, width: CHART_W, height: LANE_H,
          fill: li % 2 === 0 ? BG_EVEN : BG_ODD,
          stroke: AXIS, "stroke-width": "0.5",
        }));
        const lbl = svgEl("text", {
          x: PAD_LEFT - 4, y: top + LANE_H / 2 + 4,
          fill: TEXT_DIM, "font-size": "9", "text-anchor": "end",
          "font-family": "Courier New, monospace",
        });
        lbl.textContent = lane;
        svg.appendChild(lbl);
      });

      // X-axis ticks
      const axisY = PAD_TOP + TOTAL_LANE_H + 4;
      const span = tEnd - tStart;
      // Dynamic tick step: 1s for ≤15s, 2s for ≤30s, else 5s.
      const tickStep = span <= 15 ? 1 : (span <= 30 ? 2 : 5);
      for (let t = Math.ceil(tStart / tickStep) * tickStep; t <= tEnd; t += tickStep) {
        const x = scaleX(t, tStart, tEnd);
        svg.appendChild(svgEl("line", {
          x1: x, y1: PAD_TOP, x2: x, y2: axisY,
          stroke: AXIS, "stroke-width": "0.5", "stroke-dasharray": "2,4",
        }));
        const tick = svgEl("text", {
          x, y: axisY + 12,
          fill: TICK, "font-size": "9", "text-anchor": "middle",
          "font-family": "Courier New, monospace",
        });
        tick.textContent = t.toFixed(tickStep < 1 ? 1 : 0) + "s";
        svg.appendChild(tick);
      }

      // Event annotations
      (payload.events || []).forEach((ev) => {
        if (ev.time_s == null || ev.time_s < tStart || ev.time_s > tEnd) return;
        const x = scaleX(ev.time_s, tStart, tEnd);
        svg.appendChild(svgEl("line", {
          x1: x, y1: PAD_TOP, x2: x, y2: axisY,
          stroke: EVENT, "stroke-width": "0.8",
          "stroke-dasharray": "3,3", opacity: "0.55",
        }));
        const evLbl = svgEl("text", {
          x: x + 2, y: PAD_TOP + 8,
          fill: EVENT, "font-size": "8", opacity: "0.8",
          "font-family": "Courier New, monospace",
        });
        evLbl.textContent = ev.label || "";
        svg.appendChild(evLbl);
      });

      // Series polylines per lane
      laneLabels.forEach((lane, li) => {
        const top = laneTop(li);
        const ids = laneSeries[lane] || [];
        ids.forEach((id, idIdx) => {
          const s = smap.get(id);
          if (!s || !s.samples || s.samples.length === 0) return;

          const vMin = s.display_min != null ? s.display_min : 0;
          const vMax = s.display_max != null ? s.display_max : 1;
          const range = vMax - vMin || 1;
          const color = s.color || "#6a7d95";
          const isBoolean = vMin === 0 && vMax === 1;

          // Unit label on first series of the lane
          if (idIdx === 0) {
            const yLbl = svgEl("text", {
              x: W - PAD_RIGHT + 2, y: top + 10,
              fill: TEXT_DIM, "font-size": "8", "text-anchor": "start",
              "font-family": "Courier New, monospace",
            });
            yLbl.textContent = s.unit || "";
            svg.appendChild(yLbl);
          }

          // Build polyline — stepped for boolean, linear for analog
          const pts = [];
          for (let i = 0; i < s.samples.length; i++) {
            const [t, v] = s.samples[i];
            const x = scaleX(t, tStart, tEnd);
            const norm = Math.max(0, Math.min(1, (v - vMin) / range));
            const y = scaleY(norm, top);
            if (isBoolean && i > 0) {
              const [, vPrev] = s.samples[i - 1];
              const normPrev = Math.max(0, Math.min(1, (vPrev - vMin) / range));
              const yPrev = scaleY(normPrev, top);
              pts.push(`${x.toFixed(1)},${yPrev.toFixed(1)}`);
            }
            pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
          }
          svg.appendChild(svgEl("polyline", {
            points: pts.join(" "),
            stroke: color,
            "stroke-width": "1.4",
            fill: "none",
            opacity: "0.9",
          }));

          // End label
          const last = s.samples[s.samples.length - 1];
          if (last) {
            const [lt, lv] = last;
            const lx = scaleX(lt, tStart, tEnd);
            const norm = Math.max(0, Math.min(1, (lv - vMin) / range));
            const ly = scaleY(norm, top);
            const slbl = svgEl("text", {
              x: lx - 2, y: ly - 3,
              fill: color, "font-size": "8", "text-anchor": "end",
              "font-family": "Courier New, monospace", opacity: "0.8",
            });
            slbl.textContent = s.label || s.id;
            svg.appendChild(slbl);
          }
        });
      });

      // Replay cursor placeholder
      cursorLine = svgEl("line", {
        x1: PAD_LEFT, y1: PAD_TOP,
        x2: PAD_LEFT, y2: PAD_TOP + TOTAL_LANE_H,
        stroke: CURSOR, "stroke-width": "1.2", opacity: "0",
      });
      svg.appendChild(cursorLine);

      renderLegend();
    }

    function renderLegend() {
      if (!legend || !payload) return;
      legend.innerHTML = "";
      const smap = seriesMap();
      laneLabels.forEach((lane) => {
        (laneSeries[lane] || []).forEach((id) => {
          const s = smap.get(id);
          if (!s) return;
          const item = document.createElement("div");
          item.className = "tsc-legend-item";
          const sw = document.createElement("span");
          sw.className = "tsc-legend-swatch";
          sw.style.display = "inline-block";
          sw.style.width = "18px";
          sw.style.height = "3px";
          sw.style.verticalAlign = "middle";
          sw.style.marginRight = "5px";
          sw.style.background = s.color || "#6a7d95";
          const lab = document.createElement("span");
          lab.textContent = (s.label || s.id) + (s.unit ? " (" + s.unit + ")" : "");
          item.appendChild(sw);
          item.appendChild(lab);
          legend.appendChild(item);
        });
      });
    }

    function startReplay() {
      if (!payload || !cursorLine) return;
      stopReplay();
      const tStart = payload.time_start_s || 0;
      const tEndRaw = payload.time_end_s != null ? payload.time_end_s : tStart + 1;
      const tEnd = tEndRaw > tStart ? tEndRaw : tStart + 1;
      const durationMs = (tEnd - tStart) * 1000;
      let startTs = null;
      cursorLine.setAttribute("opacity", "0.85");
      function step(ts) {
        if (!startTs) startTs = ts;
        const elapsed = ts - startTs;
        const frac = Math.min(1, elapsed / durationMs);
        const t = tStart + frac * (tEnd - tStart);
        const x = scaleX(t, tStart, tEnd);
        cursorLine.setAttribute("x1", x);
        cursorLine.setAttribute("x2", x);
        if (progress) progress.textContent = `t = ${t.toFixed(2)}s`;
        if (frac < 1) {
          replayTimer = requestAnimationFrame(step);
        } else {
          cursorLine.setAttribute("opacity", "0.3");
          if (progress) progress.textContent = `t = ${tEnd.toFixed(2)}s  ▶ 完成`;
        }
      }
      replayTimer = requestAnimationFrame(step);
    }

    function stopReplay() {
      if (replayTimer) { cancelAnimationFrame(replayTimer); replayTimer = null; }
      if (cursorLine) cursorLine.setAttribute("opacity", "0");
      if (progress) progress.textContent = "";
    }

    return {
      setData,
      clear,
      render,
      startReplay,
      stopReplay,
      renderLegend,
      // Expose config for integration probes / tests
      get payload() { return payload; },
    };
  }

  // ── Helpers for composing payloads from live-tick records ────────────────

  /**
   * Build a monitor-timeline-shaped payload from an array of tick records.
   *
   * @param {Array<Object>} records — each record has `t_s` and signal fields
   * @param {Array<Object>} seriesDefs — [{id, label, color, unit?, display_min?, display_max?, field, transform?}]
   *        `field` = record key to extract; `transform(rec)` overrides if present.
   * @param {Object} opts — { timeStart?, timeEnd?, windowSeconds?, events? }
   *        If windowSeconds is set and records exceed it, payload is cropped to
   *        [tEnd - windowSeconds, tEnd] to keep the chart scroll-like.
   */
  function buildPayload(records, seriesDefs, opts) {
    opts = opts || {};
    const recs = Array.isArray(records) ? records : [];
    const tFirst = recs.length ? recs[0].t_s : 0;
    const tLast  = recs.length ? recs[recs.length - 1].t_s : (tFirst + 1);
    let tStart = opts.timeStart != null ? opts.timeStart : tFirst;
    let tEnd   = opts.timeEnd   != null ? opts.timeEnd   : Math.max(tLast, tStart + 1);
    if (opts.windowSeconds && (tEnd - tStart) > opts.windowSeconds) {
      tStart = tEnd - opts.windowSeconds;
    }

    const series = seriesDefs.map((def) => {
      const samples = [];
      for (const rec of recs) {
        if (rec.t_s == null) continue;
        if (rec.t_s < tStart) continue;
        let v;
        if (typeof def.transform === "function") {
          v = def.transform(rec);
        } else {
          v = rec[def.field];
        }
        if (v == null) continue;
        if (typeof v === "boolean") v = v ? 1 : 0;
        if (typeof v !== "number") continue;
        samples.push([rec.t_s, v]);
      }
      return {
        id: def.id,
        label: def.label || def.id,
        color: def.color || "#6a7d95",
        unit: def.unit || "",
        display_min: def.display_min != null ? def.display_min : 0,
        display_max: def.display_max != null ? def.display_max : 1,
        samples,
      };
    });

    return {
      time_start_s: tStart,
      time_end_s: tEnd,
      series,
      events: opts.events || [],
    };
  }

  global.TimeseriesChart = { create, buildPayload };
})(typeof window !== "undefined" ? window : this);
