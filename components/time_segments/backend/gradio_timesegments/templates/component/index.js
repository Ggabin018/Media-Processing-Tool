const {
  SvelteComponent: Fe,
  append_hydration: _e,
  attr: M,
  binding_callbacks: de,
  children: ce,
  claim_element: Z,
  claim_space: qe,
  claim_text: ze,
  destroy_each: Re,
  detach: U,
  element: x,
  empty: le,
  ensure_array_like: me,
  get_svelte_dataset: Ge,
  init: He,
  insert_hydration: F,
  listen: L,
  noop: ge,
  run_all: Je,
  safe_not_equal: Qe,
  set_data: We,
  space: Ve,
  text: Oe,
  toggle_class: ee
} = window.__gradio__svelte__internal, { createEventDispatcher: Xe, tick: Ye } = window.__gradio__svelte__internal;
function be(l, e, t) {
  const i = l.slice();
  return i[32] = e[t], i[33] = e, i[34] = t, i;
}
function Ze(l) {
  let e, t, i = me(
    /*parts*/
    l[7]
  ), n = [];
  for (let a = 0; a < i.length; a += 1)
    n[a] = ve(be(l, i, a));
  let s = (
    /*allow_empty*/
    l[1] && !/*disabled*/
    l[3] && ke(l)
  );
  return {
    c() {
      e = x("div");
      for (let a = 0; a < n.length; a += 1)
        n[a].c();
      t = Ve(), s && s.c(), this.h();
    },
    l(a) {
      e = Z(a, "DIV", {
        class: !0,
        role: !0,
        "aria-label": !0
      });
      var g = ce(e);
      for (let c = 0; c < n.length; c += 1)
        n[c].l(g);
      t = qe(g), s && s.l(g), g.forEach(U), this.h();
    },
    h() {
      M(e, "class", "time svelte-1nan7r1"), M(e, "role", "group"), M(
        e,
        "aria-label",
        /*aria_label*/
        l[5]
      ), ee(
        e,
        "invalid",
        /*invalid*/
        l[4]
      ), ee(
        e,
        "disabled",
        /*disabled*/
        l[3]
      );
    },
    m(a, g) {
      F(a, e, g);
      for (let c = 0; c < n.length; c += 1)
        n[c] && n[c].m(e, null);
      _e(e, t), s && s.m(e, null), l[25](e);
    },
    p(a, g) {
      if (g[0] & /*parts, NAMES, disabled, inputs, on_focus, on_blur, on_keydown, on_paste*/
      31944) {
        i = me(
          /*parts*/
          a[7]
        );
        let c;
        for (c = 0; c < i.length; c += 1) {
          const S = be(a, i, c);
          n[c] ? n[c].p(S, g) : (n[c] = ve(S), n[c].c(), n[c].m(e, t));
        }
        for (; c < n.length; c += 1)
          n[c].d(1);
        n.length = i.length;
      }
      /*allow_empty*/
      a[1] && !/*disabled*/
      a[3] ? s ? s.p(a, g) : (s = ke(a), s.c(), s.m(e, null)) : s && (s.d(1), s = null), g[0] & /*aria_label*/
      32 && M(
        e,
        "aria-label",
        /*aria_label*/
        a[5]
      ), g[0] & /*invalid*/
      16 && ee(
        e,
        "invalid",
        /*invalid*/
        a[4]
      ), g[0] & /*disabled*/
      8 && ee(
        e,
        "disabled",
        /*disabled*/
        a[3]
      );
    },
    d(a) {
      a && U(e), Re(n, a), s && s.d(), l[25](null);
    }
  };
}
function xe(l) {
  let e, t, i, n;
  return {
    c() {
      e = x("button"), t = Oe(
        /*empty_label*/
        l[2]
      ), this.h();
    },
    l(s) {
      e = Z(s, "BUTTON", {
        type: !0,
        class: !0,
        "aria-label": !0
      });
      var a = ce(e);
      t = ze(
        a,
        /*empty_label*/
        l[2]
      ), a.forEach(U), this.h();
    },
    h() {
      M(e, "type", "button"), M(e, "class", "time empty svelte-1nan7r1"), e.disabled = /*disabled*/
      l[3], M(
        e,
        "aria-label",
        /*aria_label*/
        l[5]
      );
    },
    m(s, a) {
      F(s, e, a), _e(e, t), i || (n = L(
        e,
        "click",
        /*start_editing*/
        l[15]
      ), i = !0);
    },
    p(s, a) {
      a[0] & /*empty_label*/
      4 && We(
        t,
        /*empty_label*/
        s[2]
      ), a[0] & /*disabled*/
      8 && (e.disabled = /*disabled*/
      s[3]), a[0] & /*aria_label*/
      32 && M(
        e,
        "aria-label",
        /*aria_label*/
        s[5]
      );
    },
    d(s) {
      s && U(e), i = !1, n();
    }
  };
}
function $e(l) {
  let e, t = ":";
  return {
    c() {
      e = x("span"), e.textContent = t, this.h();
    },
    l(i) {
      e = Z(i, "SPAN", { class: !0, "data-svelte-h": !0 }), Ge(e) !== "svelte-mw58sz" && (e.textContent = t), this.h();
    },
    h() {
      M(e, "class", "sep svelte-1nan7r1");
    },
    m(i, n) {
      F(i, e, n);
    },
    d(i) {
      i && U(e);
    }
  };
}
function ve(l) {
  let e, t, i = (
    /*i*/
    l[34]
  ), n, s, a, g;
  const c = () => (
    /*input_binding*/
    l[20](e, i)
  ), S = () => (
    /*input_binding*/
    l[20](null, i)
  );
  function p() {
    return (
      /*focus_handler*/
      l[21](
        /*i*/
        l[34]
      )
    );
  }
  function y() {
    return (
      /*click_handler*/
      l[22](
        /*i*/
        l[34]
      )
    );
  }
  function D(...o) {
    return (
      /*keydown_handler*/
      l[23](
        /*i*/
        l[34],
        ...o
      )
    );
  }
  function b(...o) {
    return (
      /*input_handler*/
      l[24](
        /*i*/
        l[34],
        ...o
      )
    );
  }
  let v = (
    /*i*/
    l[34] < 2 && $e()
  );
  return {
    c() {
      e = x("input"), n = Ve(), v && v.c(), s = le(), this.h();
    },
    l(o) {
      e = Z(o, "INPUT", {
        inputmode: !0,
        size: !0,
        "aria-label": !0,
        class: !0
      }), n = qe(o), v && v.l(o), s = le(), this.h();
    },
    h() {
      e.value = t = ue(
        /*part*/
        l[32]
      ), M(e, "inputmode", "numeric"), M(e, "size", "2"), M(
        e,
        "aria-label",
        /*NAMES*/
        l[10][
          /*i*/
          l[34]
        ]
      ), e.disabled = /*disabled*/
      l[3], M(e, "class", "svelte-1nan7r1");
    },
    m(o, f) {
      F(o, e, f), c(), F(o, n, f), v && v.m(o, f), F(o, s, f), a || (g = [
        L(e, "focus", p),
        L(e, "click", y),
        L(
          e,
          "blur",
          /*on_blur*/
          l[12]
        ),
        L(e, "keydown", D),
        L(
          e,
          "paste",
          /*on_paste*/
          l[14]
        ),
        L(e, "input", b)
      ], a = !0);
    },
    p(o, f) {
      l = o, f[0] & /*parts*/
      128 && t !== (t = ue(
        /*part*/
        l[32]
      )) && e.value !== t && (e.value = t), f[0] & /*disabled*/
      8 && (e.disabled = /*disabled*/
      l[3]), i !== /*i*/
      l[34] && (S(), i = /*i*/
      l[34], c());
    },
    d(o) {
      o && (U(e), U(n), U(s)), S(), v && v.d(o), a = !1, Je(g);
    }
  };
}
function ke(l) {
  let e, t, i, n;
  return {
    c() {
      e = x("button"), t = Oe("×"), this.h();
    },
    l(s) {
      e = Z(s, "BUTTON", { type: !0, class: !0, title: !0 });
      var a = ce(e);
      t = ze(a, "×"), a.forEach(U), this.h();
    },
    h() {
      M(e, "type", "button"), M(e, "class", "reset svelte-1nan7r1"), M(
        e,
        "title",
        /*empty_label*/
        l[2]
      );
    },
    m(s, a) {
      F(s, e, a), _e(e, t), i || (n = L(
        e,
        "click",
        /*clear*/
        l[16]
      ), i = !0);
    },
    p(s, a) {
      a[0] & /*empty_label*/
      4 && M(
        e,
        "title",
        /*empty_label*/
        s[2]
      );
    },
    d(s) {
      s && U(e), i = !1, n();
    }
  };
}
function et(l) {
  let e;
  function t(s, a) {
    return (
      /*allow_empty*/
      s[1] && /*value*/
      s[0] === null && !/*editing*/
      s[8] ? xe : Ze
    );
  }
  let i = t(l), n = i(l);
  return {
    c() {
      n.c(), e = le();
    },
    l(s) {
      n.l(s), e = le();
    },
    m(s, a) {
      n.m(s, a), F(s, e, a);
    },
    p(s, a) {
      i === (i = t(s)) && n ? n.p(s, a) : (n.d(1), n = i(s), n && (n.c(), n.m(e.parentNode, e)));
    },
    i: ge,
    o: ge,
    d(s) {
      s && U(e), n.d(s);
    }
  };
}
function ae(l) {
  return l = Math.max(0, Math.floor(l)), [
    Math.min(99, Math.floor(l / 3600)),
    Math.floor(l % 3600 / 60),
    l % 60
  ];
}
function ue(l) {
  return String(l).padStart(2, "0");
}
function tt(l) {
  return l[0] * 3600 + l[1] * 60 + l[2];
}
function re(l) {
  const e = l.trim();
  return /^\d+(:\d+){0,2}$/.test(e) ? e.split(":").reduce((t, i) => t * 60 + Number(i), 0) : null;
}
function lt(l, e, t) {
  let { value: i = 0 } = e, { max: n = null } = e, { allow_empty: s = !1 } = e, { empty_label: a = "fin de la vidéo" } = e, { disabled: g = !1 } = e, { invalid: c = !1 } = e, { aria_label: S = "time" } = e;
  const p = Xe(), y = [99, 59, 59], D = ["heures", "minutes", "secondes"];
  let b = [], v = [0, 0, 0], o = 0, f = -1, d = !1, w;
  function m() {
    let u = tt(v);
    if (n != null && n > 0 && u > n && (u = Math.floor(n), t(7, v = ae(u))), s && u === 0) {
      i !== null && (t(0, i = null), p("change", i));
      return;
    }
    u !== i && (t(0, i = u), p("change", i));
  }
  async function k(u) {
    u < 0 || u > 2 || (await Ye(), b[u]?.focus(), b[u]?.select());
  }
  function r(u) {
    t(19, f = u), o = 0, b[u]?.select();
  }
  function h() {
    t(19, f = -1), o = 0, m(), s && setTimeout(
      () => {
        !w?.contains(document.activeElement) && i === null && t(8, d = !1);
      },
      0
    );
  }
  function E(u, j) {
    t(7, v[u] = Math.max(0, Math.min(y[u], j)), v), t(7, v), t(19, f), t(0, i), m();
  }
  function B(u, j) {
    if (g) return;
    const Q = j.key;
    if (/^[0-9]$/.test(Q)) {
      j.preventDefault();
      const Y = Number(Q);
      o === 0 ? (E(u, Y), o = 1, Y * 10 > y[u] && (o = 0, k(u + 1))) : (E(u, v[u] % 10 * 10 + Y), o = 0, k(u + 1)), u === 2 && o === 0 && b[u]?.select();
      return;
    }
    switch (Q) {
      case "ArrowUp":
      case "ArrowDown": {
        j.preventDefault();
        const Y = (j.shiftKey ? 10 : 1) * (Q === "ArrowUp" ? 1 : -1);
        E(u, v[u] + Y), o = 0, b[u]?.select();
        return;
      }
      case "ArrowLeft":
        j.preventDefault(), k(u - 1);
        return;
      case "ArrowRight":
      case ":":
      case ".":
      case " ":
        j.preventDefault(), k(u + 1);
        return;
      case "Backspace":
      case "Delete":
        j.preventDefault(), v[u] !== 0 ? (E(u, 0), o = 0, b[u]?.select()) : Q === "Backspace" && k(u - 1);
        return;
      case "Tab":
      case "Enter":
      case "Escape":
        return;
      default:
        Q.length === 1 && !j.ctrlKey && !j.metaKey && j.preventDefault();
    }
  }
  function R(u) {
    if (g) return;
    const j = re(u.clipboardData?.getData("text") ?? "");
    u.preventDefault(), j != null && (t(7, v = ae(j)), o = 0, m(), b[f]?.select());
  }
  async function ne() {
    g || (t(8, d = !0), t(7, v = [0, 0, 0]), await k(0));
  }
  function ie() {
    t(8, d = !1), t(0, i = null), p("change", i);
  }
  function _(u, j) {
    de[u ? "unshift" : "push"](() => {
      b[j] = u, t(6, b);
    });
  }
  const q = (u) => r(u), J = (u) => b[u]?.select(), X = (u, j) => B(u, j), se = (u, j) => j.currentTarget.value = ue(v[u]);
  function Le(u) {
    de[u ? "unshift" : "push"](() => {
      w = u, t(9, w);
    });
  }
  return l.$$set = (u) => {
    "value" in u && t(0, i = u.value), "max" in u && t(17, n = u.max), "allow_empty" in u && t(1, s = u.allow_empty), "empty_label" in u && t(2, a = u.empty_label), "disabled" in u && t(3, g = u.disabled), "invalid" in u && t(4, c = u.invalid), "aria_label" in u && t(5, S = u.aria_label);
  }, l.$$.update = () => {
    l.$$.dirty[0] & /*focused, value*/
    524289 && f === -1 && t(7, v = ae(i ?? 0));
  }, [
    i,
    s,
    a,
    g,
    c,
    S,
    b,
    v,
    d,
    w,
    D,
    r,
    h,
    B,
    R,
    ne,
    ie,
    n,
    re,
    f,
    _,
    q,
    J,
    X,
    se,
    Le
  ];
}
class we extends Fe {
  constructor(e) {
    super(), He(
      this,
      e,
      lt,
      et,
      Qe,
      {
        value: 0,
        max: 17,
        allow_empty: 1,
        empty_label: 2,
        disabled: 3,
        invalid: 4,
        aria_label: 5,
        parse: 18
      },
      null,
      [-1, -1]
    );
  }
  get parse() {
    return re;
  }
}
const {
  SvelteComponent: nt,
  append_hydration: A,
  attr: C,
  check_outros: it,
  children: O,
  claim_component: pe,
  claim_element: I,
  claim_space: z,
  claim_text: G,
  create_component: ye,
  destroy_component: Se,
  detach: N,
  element: P,
  ensure_array_like: Ee,
  flush: T,
  get_svelte_dataset: he,
  group_outros: st,
  init: at,
  insert_hydration: K,
  listen: Ke,
  mount_component: je,
  noop: ut,
  outro_and_destroy_block: rt,
  safe_not_equal: ft,
  set_data: $,
  set_style: te,
  space: V,
  text: H,
  toggle_class: W,
  transition_in: fe,
  transition_out: oe,
  update_keyed_each: ot
} = window.__gradio__svelte__internal;
function Ae(l, e, t) {
  const i = l.slice();
  i[25] = e[t], i[28] = t;
  const n = ct(
    /*seg*/
    i[25],
    /*i*/
    i[28],
    /*value*/
    i[0].length,
    /*maximum*/
    i[6]
  );
  return i[26] = n, i;
}
function De(l) {
  let e, t;
  return {
    c() {
      e = P("span"), t = H(
        /*label*/
        l[1]
      ), this.h();
    },
    l(i) {
      e = I(i, "SPAN", { class: !0 });
      var n = O(e);
      t = G(
        n,
        /*label*/
        l[1]
      ), n.forEach(N), this.h();
    },
    h() {
      C(e, "class", "block-label svelte-1d0rigj");
    },
    m(i, n) {
      K(i, e, n), A(e, t);
    },
    p(i, n) {
      n & /*label*/
      2 && $(
        t,
        /*label*/
        i[1]
      );
    },
    d(i) {
      i && N(e);
    }
  };
}
function Ne(l) {
  let e, t;
  return {
    c() {
      e = P("span"), t = H(
        /*info*/
        l[2]
      ), this.h();
    },
    l(i) {
      e = I(i, "SPAN", { class: !0 });
      var n = O(e);
      t = G(
        n,
        /*info*/
        l[2]
      ), n.forEach(N), this.h();
    },
    h() {
      C(e, "class", "block-info svelte-1d0rigj");
    },
    m(i, n) {
      K(i, e, n), A(e, t);
    },
    p(i, n) {
      n & /*info*/
      4 && $(
        t,
        /*info*/
        i[2]
      );
    },
    d(i) {
      i && N(e);
    }
  };
}
function Ce(l) {
  let e, t, i = Be(
    /*maximum*/
    l[6]
  ) + "", n;
  return {
    c() {
      e = P("span"), t = H("max "), n = H(i), this.h();
    },
    l(s) {
      e = I(s, "SPAN", { class: !0 });
      var a = O(e);
      t = G(a, "max "), n = G(a, i), a.forEach(N), this.h();
    },
    h() {
      C(e, "class", "max svelte-1d0rigj");
    },
    m(s, a) {
      K(s, e, a), A(e, t), A(e, n);
    },
    p(s, a) {
      a & /*maximum*/
      64 && i !== (i = Be(
        /*maximum*/
        s[6]
      ) + "") && $(n, i);
    },
    d(s) {
      s && N(e);
    }
  };
}
function Me(l) {
  let e, t = (
    /*i*/
    l[28] + 1 + ""
  ), i;
  return {
    c() {
      e = P("span"), i = H(t), this.h();
    },
    l(n) {
      e = I(n, "SPAN", { class: !0 });
      var s = O(e);
      i = G(s, t), s.forEach(N), this.h();
    },
    h() {
      C(e, "class", "num svelte-1d0rigj");
    },
    m(n, s) {
      K(n, e, s), A(e, i);
    },
    p(n, s) {
      s & /*value*/
      1 && t !== (t = /*i*/
      n[28] + 1 + "") && $(i, t);
    },
    d(n) {
      n && N(e);
    }
  };
}
function Te(l) {
  let e, t, i, n, s;
  function a() {
    return (
      /*click_handler*/
      l[23](
        /*i*/
        l[28]
      )
    );
  }
  return {
    c() {
      e = P("button"), t = H("✖"), this.h();
    },
    l(g) {
      e = I(g, "BUTTON", { type: !0, class: !0, title: !0 });
      var c = O(e);
      t = G(c, "✖"), c.forEach(N), this.h();
    },
    h() {
      C(e, "type", "button"), C(e, "class", "remove svelte-1d0rigj"), C(e, "title", "Supprimer ce segment"), e.disabled = i = /*value*/
      l[0].length <= 1;
    },
    m(g, c) {
      K(g, e, c), A(e, t), n || (s = Ke(e, "click", a), n = !0);
    },
    p(g, c) {
      l = g, c & /*value*/
      1 && i !== (i = /*value*/
      l[0].length <= 1) && (e.disabled = i);
    },
    d(g) {
      g && N(e), n = !1, s();
    }
  };
}
function Ie(l) {
  let e, t = (
    /*why*/
    l[26] + ""
  ), i;
  return {
    c() {
      e = P("span"), i = H(t), this.h();
    },
    l(n) {
      e = I(n, "SPAN", { class: !0 });
      var s = O(e);
      i = G(s, t), s.forEach(N), this.h();
    },
    h() {
      C(e, "class", "why svelte-1d0rigj");
    },
    m(n, s) {
      K(n, e, s), A(e, i);
    },
    p(n, s) {
      s & /*value, maximum*/
      65 && t !== (t = /*why*/
      n[26] + "") && $(i, t);
    },
    d(n) {
      n && N(e);
    }
  };
}
function Pe(l, e) {
  let t, i, n, s, a, g = "→", c, S, p, y, D, b = !/*single*/
  e[12] && Me(e);
  function v(...w) {
    return (
      /*change_handler*/
      e[21](
        /*i*/
        e[28],
        ...w
      )
    );
  }
  n = new we({
    props: {
      value: (
        /*seg*/
        e[25][0]
      ),
      max: (
        /*maximum*/
        e[6]
      ),
      invalid: (
        /*why*/
        e[26] !== ""
      ),
      disabled: !/*interactive*/
      e[10],
      aria_label: `début du segment ${/*i*/
      e[28] + 1}`
    }
  }), n.$on("change", v);
  function o(...w) {
    return (
      /*change_handler_1*/
      e[22](
        /*i*/
        e[28],
        ...w
      )
    );
  }
  S = new we({
    props: {
      value: (
        /*seg*/
        e[25][1] != null && /*seg*/
        e[25][1] > 0 ? (
          /*seg*/
          e[25][1]
        ) : null
      ),
      max: (
        /*maximum*/
        e[6]
      ),
      allow_empty: !0,
      invalid: (
        /*why*/
        e[26] !== ""
      ),
      disabled: !/*interactive*/
      e[10],
      aria_label: `fin du segment ${/*i*/
      e[28] + 1}`
    }
  }), S.$on("change", o);
  let f = !/*single*/
  e[12] && /*interactive*/
  e[10] && Te(e), d = (
    /*why*/
    e[26] && Ie(e)
  );
  return {
    key: l,
    first: null,
    c() {
      t = P("div"), b && b.c(), i = V(), ye(n.$$.fragment), s = V(), a = P("span"), a.textContent = g, c = V(), ye(S.$$.fragment), p = V(), f && f.c(), y = V(), d && d.c(), this.h();
    },
    l(w) {
      t = I(w, "DIV", { class: !0 });
      var m = O(t);
      b && b.l(m), i = z(m), pe(n.$$.fragment, m), s = z(m), a = I(m, "SPAN", { class: !0, "data-svelte-h": !0 }), he(a) !== "svelte-1ckiewm" && (a.textContent = g), c = z(m), pe(S.$$.fragment, m), p = z(m), f && f.l(m), y = z(m), d && d.l(m), m.forEach(N), this.h();
    },
    h() {
      C(a, "class", "arrow svelte-1d0rigj"), C(t, "class", "row svelte-1d0rigj"), W(
        t,
        "bad",
        /*why*/
        e[26] !== ""
      ), this.first = t;
    },
    m(w, m) {
      K(w, t, m), b && b.m(t, null), A(t, i), je(n, t, null), A(t, s), A(t, a), A(t, c), je(S, t, null), A(t, p), f && f.m(t, null), A(t, y), d && d.m(t, null), D = !0;
    },
    p(w, m) {
      e = w, /*single*/
      e[12] ? b && (b.d(1), b = null) : b ? b.p(e, m) : (b = Me(e), b.c(), b.m(t, i));
      const k = {};
      m & /*value*/
      1 && (k.value = /*seg*/
      e[25][0]), m & /*maximum*/
      64 && (k.max = /*maximum*/
      e[6]), m & /*value, maximum*/
      65 && (k.invalid = /*why*/
      e[26] !== ""), m & /*interactive*/
      1024 && (k.disabled = !/*interactive*/
      e[10]), m & /*value*/
      1 && (k.aria_label = `début du segment ${/*i*/
      e[28] + 1}`), n.$set(k);
      const r = {};
      m & /*value*/
      1 && (r.value = /*seg*/
      e[25][1] != null && /*seg*/
      e[25][1] > 0 ? (
        /*seg*/
        e[25][1]
      ) : null), m & /*maximum*/
      64 && (r.max = /*maximum*/
      e[6]), m & /*value, maximum*/
      65 && (r.invalid = /*why*/
      e[26] !== ""), m & /*interactive*/
      1024 && (r.disabled = !/*interactive*/
      e[10]), m & /*value*/
      1 && (r.aria_label = `fin du segment ${/*i*/
      e[28] + 1}`), S.$set(r), !/*single*/
      e[12] && /*interactive*/
      e[10] ? f ? f.p(e, m) : (f = Te(e), f.c(), f.m(t, y)) : f && (f.d(1), f = null), /*why*/
      e[26] ? d ? d.p(e, m) : (d = Ie(e), d.c(), d.m(t, null)) : d && (d.d(1), d = null), (!D || m & /*problem, value, maximum*/
      65) && W(
        t,
        "bad",
        /*why*/
        e[26] !== ""
      );
    },
    i(w) {
      D || (fe(n.$$.fragment, w), fe(S.$$.fragment, w), D = !0);
    },
    o(w) {
      oe(n.$$.fragment, w), oe(S.$$.fragment, w), D = !1;
    },
    d(w) {
      w && N(t), b && b.d(), Se(n), Se(S), f && f.d(), d && d.d();
    }
  };
}
function Ue(l) {
  let e, t = "+ Ajouter un segment", i, n;
  return {
    c() {
      e = P("button"), e.textContent = t, this.h();
    },
    l(s) {
      e = I(s, "BUTTON", {
        type: !0,
        class: !0,
        "data-svelte-h": !0
      }), he(e) !== "svelte-u9c8uv" && (e.textContent = t), this.h();
    },
    h() {
      C(e, "type", "button"), C(e, "class", "add svelte-1d0rigj");
    },
    m(s, a) {
      K(s, e, a), i || (n = Ke(
        e,
        "click",
        /*add*/
        l[14]
      ), i = !0);
    },
    p: ut,
    d(s) {
      s && N(e), i = !1, n();
    }
  };
}
function _t(l) {
  let e, t, i, n, s, a, g = "début → fin · cliquez sur hh, mm ou ss et tapez", c, S, p = [], y = /* @__PURE__ */ new Map(), D, b, v, o = (
    /*show_label*/
    l[7] && /*label*/
    l[1] && De(l)
  ), f = (
    /*info*/
    l[2] && Ne(l)
  ), d = (
    /*maximum*/
    l[6] != null && /*maximum*/
    l[6] > 0 && Ce(l)
  ), w = Ee(
    /*value*/
    l[0]
  );
  const m = (r) => (
    /*i*/
    r[28]
  );
  for (let r = 0; r < w.length; r += 1) {
    let h = Ae(l, w, r), E = m(h);
    y.set(E, p[r] = Pe(E, h));
  }
  let k = !/*single*/
  l[12] && /*can_add*/
  l[11] && Ue(l);
  return {
    c() {
      e = P("div"), o && o.c(), t = V(), f && f.c(), i = V(), n = P("div"), s = P("div"), a = P("span"), a.textContent = g, c = V(), d && d.c(), S = V();
      for (let r = 0; r < p.length; r += 1)
        p[r].c();
      D = V(), k && k.c(), this.h();
    },
    l(r) {
      e = I(r, "DIV", { id: !0, class: !0 });
      var h = O(e);
      o && o.l(h), t = z(h), f && f.l(h), i = z(h), n = I(h, "DIV", { class: !0 });
      var E = O(n);
      s = I(E, "DIV", { class: !0 });
      var B = O(s);
      a = I(B, "SPAN", { "data-svelte-h": !0 }), he(a) !== "svelte-2aht1g" && (a.textContent = g), c = z(B), d && d.l(B), B.forEach(N), S = z(E);
      for (let R = 0; R < p.length; R += 1)
        p[R].l(E);
      D = z(E), k && k.l(E), E.forEach(N), h.forEach(N), this.h();
    },
    h() {
      C(s, "class", "head svelte-1d0rigj"), C(n, "class", "segments svelte-1d0rigj"), C(
        e,
        "id",
        /*elem_id*/
        l[3]
      ), C(e, "class", b = "block " + /*elem_classes*/
      (l[4]?.join(" ") || "") + " svelte-1d0rigj"), W(
        e,
        "hidden",
        /*visible*/
        l[5] === !1
      ), W(
        e,
        "auto-margin",
        /*scale*/
        l[8] === null
      ), te(
        e,
        "flex-grow",
        /*scale*/
        l[8]
      ), te(e, "min-width", `calc(min(${/*min_width*/
      l[9] ?? 0}px, 100%))`);
    },
    m(r, h) {
      K(r, e, h), o && o.m(e, null), A(e, t), f && f.m(e, null), A(e, i), A(e, n), A(n, s), A(s, a), A(s, c), d && d.m(s, null), A(n, S);
      for (let E = 0; E < p.length; E += 1)
        p[E] && p[E].m(n, null);
      A(n, D), k && k.m(n, null), v = !0;
    },
    p(r, [h]) {
      /*show_label*/
      r[7] && /*label*/
      r[1] ? o ? o.p(r, h) : (o = De(r), o.c(), o.m(e, t)) : o && (o.d(1), o = null), /*info*/
      r[2] ? f ? f.p(r, h) : (f = Ne(r), f.c(), f.m(e, i)) : f && (f.d(1), f = null), /*maximum*/
      r[6] != null && /*maximum*/
      r[6] > 0 ? d ? d.p(r, h) : (d = Ce(r), d.c(), d.m(s, null)) : d && (d.d(1), d = null), h & /*problem, value, maximum, remove, single, interactive, set*/
      46145 && (w = Ee(
        /*value*/
        r[0]
      ), st(), p = ot(p, h, m, 1, r, w, y, n, rt, Pe, D, Ae), it()), !/*single*/
      r[12] && /*can_add*/
      r[11] ? k ? k.p(r, h) : (k = Ue(r), k.c(), k.m(n, null)) : k && (k.d(1), k = null), (!v || h & /*elem_id*/
      8) && C(
        e,
        "id",
        /*elem_id*/
        r[3]
      ), (!v || h & /*elem_classes*/
      16 && b !== (b = "block " + /*elem_classes*/
      (r[4]?.join(" ") || "") + " svelte-1d0rigj")) && C(e, "class", b), (!v || h & /*elem_classes, visible*/
      48) && W(
        e,
        "hidden",
        /*visible*/
        r[5] === !1
      ), (!v || h & /*elem_classes, scale*/
      272) && W(
        e,
        "auto-margin",
        /*scale*/
        r[8] === null
      ), h & /*scale*/
      256 && te(
        e,
        "flex-grow",
        /*scale*/
        r[8]
      ), h & /*min_width*/
      512 && te(e, "min-width", `calc(min(${/*min_width*/
      r[9] ?? 0}px, 100%))`);
    },
    i(r) {
      if (!v) {
        for (let h = 0; h < w.length; h += 1)
          fe(p[h]);
        v = !0;
      }
    },
    o(r) {
      for (let h = 0; h < p.length; h += 1)
        oe(p[h]);
      v = !1;
    },
    d(r) {
      r && N(e), o && o.d(), f && f.d(), d && d.d();
      for (let h = 0; h < p.length; h += 1)
        p[h].d();
      k && k.d();
    }
  };
}
function Be(l) {
  const e = Math.floor(l), t = (i) => String(i).padStart(2, "0");
  return `${t(Math.floor(e / 3600))}:${t(Math.floor(e % 3600 / 60))}:${t(e % 60)}`;
}
function ct(l, e, t, i) {
  const [n, s] = l, a = s != null && s > 0;
  return !a && e < t - 1 ? "seule la dernière ligne peut aller jusqu'à la fin" : a && s <= n ? "la fin doit être après le début" : i != null && i > 0 && n >= i ? "le début est après la fin de la vidéo" : "";
}
function ht(l, e, t) {
  let i, n, { gradio: s } = e, { label: a = "Segments" } = e, { info: g = void 0 } = e, { elem_id: c = "" } = e, { elem_classes: S = [] } = e, { visible: p = !0 } = e, { value: y = [[0, null]] } = e, { max_segments: D = null } = e, { maximum: b = null } = e, { show_label: v = !0 } = e, { scale: o = null } = e, { min_width: f = void 0 } = e, { loading_status: d = void 0 } = e, { value_is_output: w = !1 } = e, { interactive: m = !0 } = e, { root: k } = e;
  function r() {
    s.dispatch("change"), w || s.dispatch("input");
  }
  function h(_, q, J) {
    t(0, y = y.map((X, se) => se === _ ? q === 0 ? [J ?? 0, X[1]] : [X[0], J] : X)), r();
  }
  function E() {
    const _ = y[y.length - 1], q = _ ? _[1] != null && _[1] > 0 ? _[1] : _[0] : 0;
    t(0, y = [...y, [q, null]]), r();
  }
  function B(_) {
    y.length <= 1 || (t(0, y = y.filter((q, J) => J !== _)), r());
  }
  const R = (_, q) => h(_, 0, q.detail), ne = (_, q) => h(_, 1, q.detail), ie = (_) => B(_);
  return l.$$set = (_) => {
    "gradio" in _ && t(16, s = _.gradio), "label" in _ && t(1, a = _.label), "info" in _ && t(2, g = _.info), "elem_id" in _ && t(3, c = _.elem_id), "elem_classes" in _ && t(4, S = _.elem_classes), "visible" in _ && t(5, p = _.visible), "value" in _ && t(0, y = _.value), "max_segments" in _ && t(17, D = _.max_segments), "maximum" in _ && t(6, b = _.maximum), "show_label" in _ && t(7, v = _.show_label), "scale" in _ && t(8, o = _.scale), "min_width" in _ && t(9, f = _.min_width), "loading_status" in _ && t(18, d = _.loading_status), "value_is_output" in _ && t(19, w = _.value_is_output), "interactive" in _ && t(10, m = _.interactive), "root" in _ && t(20, k = _.root);
  }, l.$$.update = () => {
    l.$$.dirty & /*value*/
    1 && (!Array.isArray(y) || y.length === 0) && t(0, y = [[0, null]]), l.$$.dirty & /*max_segments*/
    131072 && t(12, i = D === 1), l.$$.dirty & /*interactive, max_segments, value*/
    132097 && t(11, n = m && (D == null || y.length < D));
  }, [
    y,
    a,
    g,
    c,
    S,
    p,
    b,
    v,
    o,
    f,
    m,
    n,
    i,
    h,
    E,
    B,
    s,
    D,
    d,
    w,
    k,
    R,
    ne,
    ie
  ];
}
class dt extends nt {
  constructor(e) {
    super(), at(this, e, ht, _t, ft, {
      gradio: 16,
      label: 1,
      info: 2,
      elem_id: 3,
      elem_classes: 4,
      visible: 5,
      value: 0,
      max_segments: 17,
      maximum: 6,
      show_label: 7,
      scale: 8,
      min_width: 9,
      loading_status: 18,
      value_is_output: 19,
      interactive: 10,
      root: 20
    });
  }
  get gradio() {
    return this.$$.ctx[16];
  }
  set gradio(e) {
    this.$$set({ gradio: e }), T();
  }
  get label() {
    return this.$$.ctx[1];
  }
  set label(e) {
    this.$$set({ label: e }), T();
  }
  get info() {
    return this.$$.ctx[2];
  }
  set info(e) {
    this.$$set({ info: e }), T();
  }
  get elem_id() {
    return this.$$.ctx[3];
  }
  set elem_id(e) {
    this.$$set({ elem_id: e }), T();
  }
  get elem_classes() {
    return this.$$.ctx[4];
  }
  set elem_classes(e) {
    this.$$set({ elem_classes: e }), T();
  }
  get visible() {
    return this.$$.ctx[5];
  }
  set visible(e) {
    this.$$set({ visible: e }), T();
  }
  get value() {
    return this.$$.ctx[0];
  }
  set value(e) {
    this.$$set({ value: e }), T();
  }
  get max_segments() {
    return this.$$.ctx[17];
  }
  set max_segments(e) {
    this.$$set({ max_segments: e }), T();
  }
  get maximum() {
    return this.$$.ctx[6];
  }
  set maximum(e) {
    this.$$set({ maximum: e }), T();
  }
  get show_label() {
    return this.$$.ctx[7];
  }
  set show_label(e) {
    this.$$set({ show_label: e }), T();
  }
  get scale() {
    return this.$$.ctx[8];
  }
  set scale(e) {
    this.$$set({ scale: e }), T();
  }
  get min_width() {
    return this.$$.ctx[9];
  }
  set min_width(e) {
    this.$$set({ min_width: e }), T();
  }
  get loading_status() {
    return this.$$.ctx[18];
  }
  set loading_status(e) {
    this.$$set({ loading_status: e }), T();
  }
  get value_is_output() {
    return this.$$.ctx[19];
  }
  set value_is_output(e) {
    this.$$set({ value_is_output: e }), T();
  }
  get interactive() {
    return this.$$.ctx[10];
  }
  set interactive(e) {
    this.$$set({ interactive: e }), T();
  }
  get root() {
    return this.$$.ctx[20];
  }
  set root(e) {
    this.$$set({ root: e }), T();
  }
}
export {
  dt as default
};
