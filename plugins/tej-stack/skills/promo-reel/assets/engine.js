/* motion-kit engine: every value is a pure function of time.
   Paste into the page's <script> (or load before the scene code).
   Rules: no CSS transitions, no timers, no requestAnimationFrame state.
   The scene exposes window.seek(t) and window.T; the renderer calls seek for every subframe. */

// Loop length in seconds. Scene code must set this before building tracks: T = bars * 4 * 60 / BPM
var T = 16;
// LOOP = true: every track must end on its start value and the video loops seamlessly.
// LOOP = false (ads with an end card): tracks may end anywhere; t is clamped to [0, T].
var LOOP = true;

/* Closed-form unit step response of a damped spring.
   w = natural frequency (higher is faster), z = damping ratio (1 = no overshoot, 0.8 = ~1.5% overshoot). */
function S(x, w, z){
  if (x <= 0) return 0;
  if (w === Infinity) return 1;
  if (z >= 1) return 1 - Math.exp(-w*x)*(1 + w*x);
  const wd = w*Math.sqrt(1 - z*z);
  return 1 - Math.exp(-z*w*x)*(Math.cos(wd*x) + (z*w/wd)*Math.sin(wd*x));
}

// Presets used in the reference build. Keep overshoot tiny: z >= 0.75 everywhere.
const GEO   = {w:20,  z:.82};  // shape size, radius, position
const CAM   = {w:10.5,z:1};    // camera: slower, no overshoot, starts ~0.05s before the shape
const IN    = {w:30,  z:1};    // content enter
const OUT   = {w:60,  z:1};    // content exit (faster than enter so swaps never overlap)
const FAST  = {w:36,  z:.75};  // press
const LEAD  = {w:30,  z:.82};  // leading edge of a liquid indicator
const TRAIL = {w:12.5,z:.97};  // trailing edge
const CUR   = {w:15,  z:.96};  // cursor / finger travel
const DRAG  = {w:10,  z:1};    // cursor motion while dragging
const GRAB  = {w:40,  z:1};    // smooths any mismatch at the moment of grab
const COL   = {w:34,  z:1};    // colour (fast, avoids muddy midpoints)
const INST  = {w:Infinity, z:1}; // instant set (use only while invisible)

/* Track: a value that changes target many times is the sum of one spring per change.
   Each step is also counted one loop earlier, so the value is exactly periodic with period T.
   REQUIREMENT: the last target of every track must equal its first value (sum of deltas = 0). */
class Tr{
  constructor(v){ this.v0=v; this.c=v; this.s=[]; this.h=[]; }
  to(t, v, sp=GEO){ this.s.push([t, v - this.c, sp.w, sp.z]); this.c = v; return this; }
  base(t){ let v=this.v0; for (const [a,d,w,z] of this.s) v += d*(S(t-a,w,z) + (LOOP ? S(t+T-a,w,z) : 0)); return v; }
  // Direct manipulation: while held, value = fn(t) (usually derived from cursor position).
  // On release it springs back from wherever it was, using spring `rel`.
  hold(t0, t1, fn, rel=GEO){ this.h.push({t0,t1,fn,rel}); return this; }
  held(h, t){ return h.fn(t) + (this.base(h.t0) - h.fn(h.t0))*(1 - S(t-h.t0, GRAB.w, GRAB.z)); }
  at(t){
    for (const h of this.h) if (t >= h.t0 && t < h.t1) return this.held(h, t);
    let v = this.base(t);
    for (const h of this.h) if (t >= h.t1) v += (this.held(h, h.t1) - this.base(h.t1))*(1 - S(t-h.t1, h.rel.w, h.rel.z));
    return v;
  }
  closes(){ return Math.abs(this.c - this.v0) < 1e-9; }
}
class Col{
  constructor(c){ this.r=new Tr(c[0]); this.g=new Tr(c[1]); this.b=new Tr(c[2]); }
  to(t,c,sp=COL){ this.r.to(t,c[0],sp); this.g.to(t,c[1],sp); this.b.to(t,c[2],sp); return this; }
  at(t){ return [this.r.at(t), this.g.at(t), this.b.at(t)]; }
}
// Visibility track: V(startValue, [t, 1], [t, 0], ...). Enter uses IN, exit uses OUT.
const V = (v0, ...p) => { const tr=new Tr(v0); for (const [t,v] of p) tr.to(t, v, v>0.5?IN:OUT); return tr; };

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)), mix=(a,b,k)=>a+(b-a)*k;
const css=(c,a=1)=>`rgba(${Math.round(c[0])},${Math.round(c[1])},${Math.round(c[2])},${a})`;
const mixc=(a,b,k)=>[mix(a[0],b[0],k),mix(a[1],b[1],k),mix(a[2],b[2],k)];

/* Content swap inside a morphing container: opacity + short blur + slight scale.
   Blur is divided by camera scale so it looks the same on screen at any zoom.
   Returns the scale to apply. */
function layer(el, v, cam, sc=.965){
  el.style.opacity = v.toFixed(4);
  el.style.visibility = v < .002 ? 'hidden' : 'visible';
  const b = (1-v)*11/cam;
  el.style.filter = b > .02 ? `blur(${b.toFixed(3)}px)` : 'none';
  return mix(sc,1,v);
}

// World to screen for a camera that scales around the frame centre (cx, cy are frame centre px).
const toScreen = (wx, wy, s, camY=0, cx=720, cy=720) => [cx + wx*s, cy + (wy-camY)*s];
