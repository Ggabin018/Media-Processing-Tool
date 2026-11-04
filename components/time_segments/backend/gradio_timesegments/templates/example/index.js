const {
  SvelteComponent: h,
  append_hydration: d,
  attr: m,
  children: v,
  claim_element: g,
  claim_text: y,
  detach: s,
  element: b,
  init: S,
  insert_hydration: j,
  noop: u,
  safe_not_equal: p,
  set_data: q,
  text: w,
  toggle_class: f
} = window.__gradio__svelte__internal;
function E(t) {
  let e, n = (
    /*value*/
    (t[0] ?? []).map(
      /*func*/
      t[3]
    ).join(", ") + ""
  ), r;
  return {
    c() {
      e = b("div"), r = w(n), this.h();
    },
    l(l) {
      e = g(l, "DIV", { class: !0 });
      var a = v(e);
      r = y(a, n), a.forEach(s), this.h();
    },
    h() {
      m(e, "class", "svelte-1r0kqnm"), f(
        e,
        "table",
        /*type*/
        t[1] === "table"
      ), f(
        e,
        "gallery",
        /*type*/
        t[1] === "gallery"
      ), f(
        e,
        "selected",
        /*selected*/
        t[2]
      );
    },
    m(l, a) {
      j(l, e, a), d(e, r);
    },
    p(l, [a]) {
      a & /*value*/
      1 && n !== (n = /*value*/
      (l[0] ?? []).map(
        /*func*/
        l[3]
      ).join(", ") + "") && q(r, n), a & /*type*/
      2 && f(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), a & /*type*/
      2 && f(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), a & /*selected*/
      4 && f(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: u,
    o: u,
    d(l) {
      l && s(e);
    }
  };
}
function o(t) {
  if (t == null || t <= 0) return "fin";
  const e = (n) => String(n).padStart(2, "0");
  return `${e(Math.floor(t / 3600))}:${e(Math.floor(t % 3600 / 60))}:${e(t % 60)}`;
}
function M(t, e, n) {
  let { value: r } = e, { type: l } = e, { selected: a = !1 } = e;
  const _ = ([i, c]) => `${o(i || 0)} → ${o(c)}`;
  return t.$$set = (i) => {
    "value" in i && n(0, r = i.value), "type" in i && n(1, l = i.type), "selected" in i && n(2, a = i.selected);
  }, [r, l, a, _];
}
class k extends h {
  constructor(e) {
    super(), S(this, e, M, E, p, { value: 0, type: 1, selected: 2 });
  }
}
export {
  k as default
};
