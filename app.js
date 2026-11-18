(function () {
  "use strict";
  var ARQ_DADOS = "guia-fichas.json";
  var CHAVE = "guia-lgpd-checklist-v1";

  function norm(t) {
    return String(t).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  function el(tag, attrs, children) {
    var e = document.createElement(tag), k;
    for (k in (attrs || {})) {
      if (k === "text") e.textContent = attrs[k];
      else if (k === "class") e.className = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    (children || []).forEach(function (c) { if (c) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function carregar(destino, cb) {
    fetch(ARQ_DADOS).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (d) { cb(d.fichas); }).catch(function () {
      destino.appendChild(el("p", { "class": "aviso", role: "alert",
        text: "Não foi possível carregar os dados das fichas. Abra o site pelo endereço publicado ou por um servidor local (por exemplo, python3 -m http.server)." }));
    });
  }

  /* ---------- armazenamento (opcional) ---------- */
  var memoria = {};
  function lerMarcas() {
    try {
      var s = window.localStorage.getItem(CHAVE);
      if (s) { var o = JSON.parse(s); if (o && typeof o === "object") memoria = o; }
    } catch (e) { /* segue sem localStorage */ }
    return memoria;
  }
  function gravarMarcas() {
    try { window.localStorage.setItem(CHAVE, JSON.stringify(memoria)); } catch (e) { /* ignora */ }
  }

  /* ---------- página de fichas ---------- */
  var FORMAS = ["Código", "Repositório", "Banco de dados", "Configuração", "Infraestrutura", "Documento"];

  function montarFicha(f) {
    var cond = f.condicional;
    var sum = el("summary", {}, [
      el("span", { "class": "id", text: f.id }),
      el("span", { "class": "etapa", text: f.etapa }),
      cond ? el("span", { "class": "selo", text: "(condicional)" }) : null,
      el("span", { "class": "resumo-diretriz", text: f.diretriz })
    ]);
    var como = el("ul");
    if (f.mecanismo) como.appendChild(el("li", {}, [el("strong", { text: "Mecanismo ou padrão:" }), " " + f.mecanismo]));
    if (f.variacoes) como.appendChild(el("li", {}, [el("strong", { text: "Variações de contexto:" }), " " + f.variacoes]));
    var itens = el("ol");
    f.itens.forEach(function (i) { itens.appendChild(el("li", { text: i.texto })); });
    var refs = el("dd", {}, [
      el("p", {}, [el("strong", { text: "Base:" }), " " + f.referencias.base]),
      el("p", {}, [el("strong", { text: "Referências técnicas:" }), " " + f.referencias.referencias_tecnicas])
    ]);
    var dl = el("dl", {}, [
      el("dt", { text: "ID" }), el("dd", { text: f.id + (cond ? " (condicional)" : "") }),
      el("dt", { text: "Diretriz" }), el("dd", { text: f.diretriz }),
      el("dt", { text: "Como" }), el("dd", {}, [como]),
      el("dt", { text: "Como verificar" }), el("dd", {}, [itens]),
      el("dt", { text: "Forma de verificação" }), el("dd", { text: f.forma_verificacao }),
      el("dt", { text: "Referências" }), refs
    ]);
    var d = el("details", { "class": "ficha", id: f.id }, [sum]);
    if (cond) d.appendChild(el("p", { "class": "aplica" }, [el("strong", { text: "Aplica-se quando:" }), " " + f.aplica_se_quando]));
    d.appendChild(el("div", { "class": "corpo" }, [dl]));
    d._busca = norm([f.id, f.etapa, f.aplica_se_quando, f.diretriz, f.mecanismo, f.variacoes,
      f.itens.map(function (i) { return i.texto; }).join(" "), f.forma_verificacao,
      f.referencias.base, f.referencias.referencias_tecnicas].join(" "));
    d._ficha = f;
    return d;
  }

  function paginaFichas(raiz) {
    var lista = document.getElementById("lista-fichas");
    carregar(lista, function (fichas) {
      var els = fichas.map(montarFicha);
      els.forEach(function (e) { lista.appendChild(e); });
      var q = document.getElementById("busca"), et = document.getElementById("f-etapa"),
          fv = document.getElementById("f-forma"), co = document.getElementById("f-cond"),
          cont = document.getElementById("contagem");
      function filtrar() {
        var t = norm(q.value.trim()), n = 0;
        els.forEach(function (e) {
          var f = e._ficha;
          var ok = (!et.value || f.etapa === et.value) &&
            (!fv.value || norm(f.forma_verificacao).indexOf(norm(fv.value)) !== -1) &&
            (!co.checked || f.condicional) &&
            (!t || t.split(/\s+/).every(function (p) { return e._busca.indexOf(p) !== -1; }));
          e.hidden = !ok;
          if (ok) n++;
        });
        cont.textContent = n + " de " + els.length + " fichas";
      }
      [q, et, fv, co].forEach(function (c) { c.addEventListener("input", filtrar); c.addEventListener("change", filtrar); });
      document.getElementById("limpar-filtros").addEventListener("click", function () {
        q.value = ""; et.value = ""; fv.value = ""; co.checked = false; filtrar(); q.focus();
      });
      document.getElementById("abrir-todas").addEventListener("click", function () {
        els.forEach(function (e) { if (!e.hidden) e.open = true; });
      });
      document.getElementById("fechar-todas").addEventListener("click", function () {
        els.forEach(function (e) { e.open = false; });
      });
      function irParaHash() {
        var id = decodeURIComponent(location.hash.slice(1)), alvo = id && document.getElementById(id);
        if (!alvo || !alvo._ficha) return;
        if (alvo.hidden) { q.value = ""; et.value = ""; fv.value = ""; co.checked = false; filtrar(); }
        alvo.open = true;
        alvo.scrollIntoView();
      }
      window.addEventListener("hashchange", irParaHash);
      filtrar();
      irParaHash();
    });
  }

  /* ---------- página de checklist ---------- */
  var ROTULOS = { atende: "Atende", nao: "Não atende", na: "Não se aplica" };
  var ROTULO_CSV = { atende: "atende", nao: "não atende", na: "não se aplica" };

  function paginaChecklist() {
    var raiz = document.getElementById("grupos");
    carregar(raiz, function (fichas) {
      var marcas = lerMarcas(), total = 0, todos = [];
      fichas.forEach(function (f) {
        var g = el("section", { "class": "grupo", "aria-labelledby": "g-" + f.id }, [
          el("h2", { id: "g-" + f.id }, [el("a", { href: "fichas.html#" + f.id, text: f.id }), " " + f.diretriz])
        ]);
        f.itens.forEach(function (i) {
          total++; todos.push(i);
          var fs = el("fieldset", { "class": "item" }, [el("legend", { text: i.id + " " + i.texto })]);
          var op = el("div", { "class": "opcoes" });
          Object.keys(ROTULOS).forEach(function (v) {
            var inp = el("input", { type: "radio", name: i.id, value: v });
            if (marcas[i.id] === v) inp.checked = true;
            inp.addEventListener("change", function () { marcas[i.id] = v; gravarMarcas(); resumo(); });
            op.appendChild(el("label", {}, [inp, ROTULOS[v]]));
          });
          fs.appendChild(op);
          g.appendChild(fs);
        });
        raiz.appendChild(g);
      });
      var out = document.getElementById("resumo-marcas");
      function resumo() {
        var c = { atende: 0, nao: 0, na: 0 };
        todos.forEach(function (i) { if (c[marcas[i.id]] !== undefined) c[marcas[i.id]]++; });
        out.textContent = "Marcados: " + (c.atende + c.nao + c.na) + " de " + total +
          " · Atende: " + c.atende + " · Não atende: " + c.nao + " · Não se aplica: " + c.na;
      }
      document.getElementById("limpar-marcas").addEventListener("click", function () {
        if (!window.confirm("Limpar todas as marcações?")) return;
        marcas = {}; memoria = {}; gravarMarcas();
        Array.prototype.forEach.call(raiz.querySelectorAll("input[type=radio]"), function (r) { r.checked = false; });
        resumo();
      });
      document.getElementById("baixar-csv").addEventListener("click", function () {
        function cel(s) { return '"' + String(s).replace(/"/g, '""') + '"'; }
        var linhas = [["Item", "Texto", "Marcação"].map(cel).join(",")];
        todos.forEach(function (i) {
          linhas.push([i.id, i.texto, ROTULO_CSV[marcas[i.id]] || ""].map(cel).join(","));
        });
        var blob = new Blob(["﻿" + linhas.join("\r\n") + "\r\n"], { type: "text/csv;charset=utf-8" });
        var url = URL.createObjectURL(blob);
        var a = el("a", { href: url, download: "checklist-lgpd.csv" });
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      });
      resumo();
    });
  }


  /* ---------- índice lateral ---------- */
  (function () {
    document.documentElement.classList.add("js");
    var ind = document.getElementById("indice"), bt = document.getElementById("indice-botao");
    if (bt && ind) {
      bt.hidden = false;
      bt.addEventListener("click", function () {
        var ab = ind.classList.toggle("aberto");
        bt.setAttribute("aria-expanded", ab ? "true" : "false");
      });
      ind.addEventListener("click", function (e) {
        if (e.target.closest && e.target.closest("a") && window.matchMedia("(max-width:56rem)").matches) {
          ind.classList.remove("aberto"); bt.setAttribute("aria-expanded", "false");
        }
      });
      var mq = window.matchMedia("(max-width:56rem)");
      function ajusta() { bt.hidden = !mq.matches; }
      ajusta();
      if (mq.addEventListener) mq.addEventListener("change", ajusta);
    }
    /* destaca no índice a seção visível (páginas com âncoras) */
    if (!("IntersectionObserver" in window) || !ind) return;
    var links = {};
    Array.prototype.forEach.call(ind.querySelectorAll('a[href*="#"]'), function (a) {
      var h = a.getAttribute("href"), p = h.split("#");
      if (p[0] === location.pathname.split("/").pop() || (p[0] === "index.html" && /\/$/.test(location.pathname))) links[p[1]] = a;
    });
    var alvos = Object.keys(links).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    if (!alvos.length) return;
    var obs = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
          links[e.target.id].setAttribute("aria-current", "location");
        }
      });
    }, { rootMargin: "0px 0px -70% 0px" });
    alvos.forEach(function (a) { obs.observe(a); });
  })();

  if (document.getElementById("lista-fichas")) paginaFichas();
  if (document.getElementById("grupos")) paginaChecklist();
})();
