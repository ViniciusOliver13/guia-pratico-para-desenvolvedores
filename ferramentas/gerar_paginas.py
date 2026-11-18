import re, subprocess, html, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
raw = subprocess.run(["pdftotext", str(ROOT/"guia-pratico.pdf"), "-"], capture_output=True, text=True, check=True).stdout
raw = raw.replace("​", "").replace("●", "")
lines = [l.strip() for l in raw.splitlines()]
def idx(t, start=0):
    for i in range(start, len(lines)):
        if lines[i] == t: return i
    raise SystemExit("não achei: " + t)
def block(a, b, start=0):
    i = idx(a, start); j = idx(b, i + 1)
    return [l for l in lines[i+1:j]]
def join(ls): return " ".join(l for l in ls if l)
def paras(ls):
    out, cur = [], []
    for l in ls:
        if l: cur.append(l)
        elif cur: out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    return out
def items(ls):
    out = []
    for l in ls:
        if re.match(r"^\d+\.$", l): out.append([]); continue
        if out is not None and l: 
            if out: out[-1].append(l)
    return [" ".join(x) for x in out]
def tag(t, txt, **a):
    at = "".join(f' {k.replace("_","-")}="{v}"' for k, v in a.items())
    return f"<{t}{at}>{html.escape(txt, quote=False)}</{t}>"
E=lambda s: html.escape(s, quote=False)

# ---------- Apresentação
apr = paras(block("1. Apresentação", "2. Como Usar"))
# ---------- Como usar
i21 = idx("2.1 Ordem de uso"); i22 = idx("2.2 Como ler uma ficha"); i23 = idx("2.3 Formas de verificação"); i24 = idx("2.4 Diretrizes condicionais"); i3 = idx("3. Etapa de Preparação")
ordem = []
cur = None
for l in lines[i21+1:i22]:
    m = re.match(r"^(\d+)\.\s*(.*)$", l)
    if m:
        cur = [m.group(2)]; ordem.append(cur)
    elif l and cur is not None: cur.append(l)
ordem = [" ".join(x) for x in ordem]
l22 = lines[i22+1:i23]
k = next(n for n, l in enumerate(l22) if l.startswith("As fontes de cada ficha"))
intro22 = l22[0]
campos = []
for l in l22[1:k]:
    if re.match(r"^(ID|Diretriz|Como|Como verificar|Forma de verificação):", l): campos.append([l])
    elif l: campos[-1].append(l)
campos = [" ".join(c) for c in campos]
resto22 = join(l22[k:])
l23 = lines[i23+1:i24]
j = l23.index("Forma")
intro23 = paras(l23[:j])
fim23 = paras(l23[l23.index("Documento", j+10)+0:])  # placeholder, fixed below
# forma table rows: parse explicit
formas = [("Código","No código-fonte do sistema"),
 ("Repositório","Em outros arquivos versionados: testes, manifesto de dependências, histórico"),
 ("Banco de dados","No esquema ou no conteúdo do banco"),
 ("Configuração","Nas configurações do sistema, do servidor ou dos serviços usados"),
 ("Infraestrutura","Na rede, nos servidores ou no armazenamento"),
 ("Documento","Em registro escrito fora do sistema: do projeto (requisitos, relatórios), da operação (procedimentos, registros de revisão) ou da instituição (registro de tratamento, tabela de retenção, aviso de privacidade ou contratos)")]
pos = [n for n, l in enumerate(l23) if l.startswith("O tipo do")][0]
pos2 = [n for n, l in enumerate(l23) if l.startswith("O tipo do")][0]
fim23 = join(l23[pos:])
l24 = lines[i24+1:i3]
intro24 = join(l24[:l24.index("Diretriz")])
resto24 = None
cond = [("ARQ-09","Algum tratamento usa o consentimento como base legal"),
 ("ARQ-13","Há decisão tomada só por tratamento automatizado que afete o titular"),
 ("IMP-12","O sistema envia dados pessoais a outro órgão ou entidade"),
 ("NUV-01","O sistema roda ou guarda dados em serviço de nuvem")]
# ---------- Etapa de Preparação
i4 = idx("4. Fichas de Diretrizes")
prep = lines[i3+1:i4]
prep_intro = join(prep[:prep.index("Passo")])
passos = [("1. Delimitar o recorte","Quais módulos ou funcionalidades serão avaliados"),
 ("2. Inventariar os dados","Quais dados pessoais o recorte trata, onde ficam e quais são sensíveis (Art. 5º, II)"),
 ("3. Responder às condições","O sistema usa consentimento? Toma decisão automatizada? Compartilha dados? Roda em nuvem? Está no setor público?"),
 ("4. Registrar o que vem da instituição","Base legal escolhida, tabela de temporalidade, encarregado, contexto (público ou privado)")]
# ---------- Fontes e limites
i6 = idx("6. Fontes e Limites"); i7 = idx("7. Referências")
i61 = idx("6.1 Fontes", i6); i62 = idx("6.2 Limites", i6)
l61 = lines[i61+1:i62]
f_intro = join(l61[:l61.index("Tipo")])
f_final = join(l61[l61.index("Também foram usados os princípios de Privacy by Design de Cavoukian (2011), como") if "Também foram usados os princípios de Privacy by Design de Cavoukian (2011), como" in l61 else [n for n,l in enumerate(l61) if l.startswith("Também foram")][0]:])
fontes = [("Lei","Lei nº 13.709/2018 (LGPD)"),
 ("Norma","ABNT NBR ISO/IEC 27701:2019 e ABNT NBR ISO/IEC 27002:2013"),
 ("Orientação","Guia orientativo da ANPD sobre segurança da informação para agentes de tratamento de pequeno porte (2021) e Guia orientativo da ANPD sobre tratamento de dados pessoais pelo Poder Público (versão 2.0, 2023)"),
 ("Guia europeu","ENISA, Guidelines for SMEs on the security of personal data processing (2016)")]
l62 = lines[i62+1:i7]
limites = []
for l in l62:
    m = re.match(r"^(\d+)\.\s+(.*)$", l)
    if m: limites.append([m.group(2)]); continue
    if l and limites: limites[-1].append(l)
limites = [" ".join(x) for x in limites]
# ---------- Referências
refs_l = lines[i7+1:]
entries = []
start = re.compile(r"^[A-ZÁÂÃÉÊÍÓÔÕÚÇ’'][A-ZÁÂÃÉÊÍÓÔÕÚÇ’' ]{2,}[,.]")
for l in refs_l:
    if not l: continue
    if start.match(l): entries.append([l])
    else: entries[-1].append(l)
def join_entry(ls):
    out = ""; urlmode = False
    parts = []  # list of text pieces; None marker = wbr
    s = ls[0]
    for n, l in enumerate(ls[1:], 1):
        last = s.split(" ")[-1]
        if ("http" in last or urlmode) and not last.endswith(".") and not last.endswith("/"):
            s += "\x00" + l
        else:
            s += " " + l
        lt = s.split(" ")[-1]
        urlmode = False
    return s
ref_entries = [join_entry(e) for e in entries]

# ---------- HTML
import json
FICHAS = json.load(open(ROOT/"guia-fichas.json", encoding="utf-8"))["fichas"]
def indice(fn):
    def a(href, t, page=None):
        cur = ' aria-current="page"' if page == fn and "#" not in href else ""
        return f'<a href="{href}"{cur}>{t}</a>'
    grupos = ""
    for et in ["Requisitos","Arquitetura","Implementação","Nuvem"]:
        ids = [f["id"] for f in FICHAS if f["etapa"] == et]
        grupos += f'<li class="grupo-et"><span>{et}</span><ul class="ids">' + "".join(f'<li><a href="fichas.html#{i}">{i}</a></li>' for i in ids) + "</ul></li>"
    ab = ""
    return (
      '<ol>'
      f'<li>{a("index.html#apresentacao","1. Apresentação","index.html")}</li>'
      f'<li>{a("index.html#como-usar","2. Como Usar","index.html")}<ol>'
      f'<li>{a("index.html#ordem-de-uso","2.1 Ordem de uso")}</li><li>{a("index.html#como-ler","2.2 Como ler uma ficha")}</li>'
      f'<li>{a("index.html#formas","2.3 Formas de verificação")}</li><li>{a("index.html#condicionais","2.4 Diretrizes condicionais")}</li></ol></li>'
      f'<li>{a("preparacao.html","3. Etapa de Preparação","preparacao.html")}</li>'
      f'<li>{a("fichas.html","4. Fichas de Diretrizes","fichas.html")}<details class="ids-det"{ab}><summary>Fichas por ID</summary><ul>{grupos}</ul></details></li>'
      f'<li>{a("checklist.html","Checklist","checklist.html")}</li>'
      f'<li>{a("fontes.html","6. Fontes e Limites","fontes.html")}<ol><li>{a("fontes.html#fontes","6.1 Fontes")}</li><li>{a("fontes.html#limites","6.2 Limites")}</li></ol></li>'
      f'<li>{a("referencias.html","7. Referências","referencias.html")}</li>'
      '</ol>')
def page(fn, title, body, extra_js=""):
    full = "Guia Prático de Diretrizes da LGPD para Desenvolvedores" if fn=="index.html" else f"{title} – Guia Prático da LGPD"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<a class="pular" href="#conteudo">Ir para o conteúdo</a>
<div class="layout">
<aside class="indice" id="indice">
<p class="indice-titulo"><a href="index.html">Guia Prático de Diretrizes da LGPD para Desenvolvedores</a></p>
<nav aria-label="Índice"><p class="indice-cab">Índice</p>
{indice(fn)}
</nav>
</aside>
<div class="coluna">
<button type="button" class="indice-botao" id="indice-botao" aria-controls="indice" aria-expanded="false" hidden>Índice</button>
<main id="conteudo">
{body}
</main>
<footer class="rodape">
<p>Versão avaliada no TCC (texto de 28/10/2026)</p>
<p>Autor: Antonio Vinícius</p>
</footer>
</div>
</div>
{extra_js or '<script src="app.js" defer></script>'}
</body>
</html>
"""
def ul(items_, ordered=False):
    t = "ol" if ordered else "ul"
    return f"<{t}>" + "".join(f"<li>{x}</li>" for x in items_) + f"</{t}>"
def split_lead(s):
    m = re.match(r"^([^.:]+[.:])\s+(.*)$", s)
    return f"<strong>{E(m.group(1))}</strong> {E(m.group(2))}" if m else E(s)

# Início
b = '<h1>Guia Prático de Diretrizes da LGPD para Desenvolvedores</h1>\n<section aria-labelledby="apresentacao"><h2 id="apresentacao">1. Apresentação</h2>\n' + "\n".join(f"<p>{E(p)}</p>" for p in apr) + "\n</section>\n"
b += '<section aria-labelledby="como-usar"><h2 id="como-usar">2. Como Usar</h2>\n<h3 id="ordem-de-uso">2.1 Ordem de uso</h3>\n' + ul([split_lead(o) for o in ordem], True)
b += f'\n<h3 id="como-ler">2.2 Como ler uma ficha</h3>\n<p>{E(intro22)}</p>\n' + ul([ (lambda m: f"<strong>{E(m.group(1))}</strong> {E(m.group(2))}")(re.match(r"^([^:]+:)\s*(.*)$", c)) for c in campos]) + f"\n<p>{E(resto22)}</p>\n"
b += '<h3 id="formas">2.3 Formas de verificação</h3>\n' + "\n".join(f"<p>{E(p)}</p>" for p in intro23)
b += '\n<table><caption class="so-leitor">Formas de verificação</caption><thead><tr><th scope="col">Forma</th><th scope="col">Onde está a evidência</th></tr></thead><tbody>' + "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(c)}</td></tr>' for a,c in formas) + f"</tbody></table>\n<p>{E(fim23)}</p>\n"
b += f'<h3 id="condicionais">2.4 Diretrizes condicionais</h3>\n<p>{E(intro24)}</p>\n<table><caption class="so-leitor">Diretrizes condicionais</caption><thead><tr><th scope="col">Diretriz</th><th scope="col">Aplica-se quando</th></tr></thead><tbody>' + "".join(f'<tr><th scope="row"><a href="fichas.html#{a}">{a}</a></th><td>{E(c)}</td></tr>' for a,c in cond) + "</tbody></table>\n</section>"
open(ROOT/"index.html","w",encoding="utf-8").write(page("index.html","Início",b))
# Preparação
b = f'<h1>3. Etapa de Preparação</h1>\n<p>{E(prep_intro)}</p>\n<table><caption class="so-leitor">Passos da Etapa de Preparação</caption><thead><tr><th scope="col">Passo</th><th scope="col">O que se faz</th></tr></thead><tbody>' + "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(c)}</td></tr>' for a,c in passos) + "</tbody></table>"
open(ROOT/"preparacao.html","w",encoding="utf-8").write(page("preparacao.html","Etapa de Preparação",b))
# Fontes
b = f'<h1>6. Fontes e Limites</h1>\n<h2 id="fontes">6.1 Fontes</h2>\n<p>{E(f_intro)}</p>\n<table><caption class="so-leitor">Tipos de fonte</caption><thead><tr><th scope="col">Tipo</th><th scope="col">Fontes</th></tr></thead><tbody>' + "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(c)}</td></tr>' for a,c in fontes) + f"</tbody></table>\n<p>{E(f_final)}</p>\n<h2 id='limites'>6.2 Limites</h2>\n" + ul([split_lead(x) for x in limites], True)
open(ROOT/"fontes.html","w",encoding="utf-8").write(page("fontes.html","Fontes e limites",b))
# Referências
def ref_html(s):
    parts = s.split("\x00")
    # find URL spanning parts
    out = ""; i = 0
    txt = parts[0]
    segs = [(p) for p in parts]
    # reconstruct: a URL is a token starting with http, continued by following parts until a space appears
    res = []; n = 0
    cur = segs[0]
    # process tokens
    full = ""
    for k, p in enumerate(segs):
        full += ("\x00" if k else "") + p
    def repl(m):
        u = m.group(0)
        href = u.replace("\x00","")
        trail = ""
        while href and href[-1] in ".,;": trail = href[-1]+trail; href = href[:-1]
        shown = u.rstrip(".,;")
        return f'<a href="{html.escape(href)}">' + "<wbr>".join(E(x) for x in shown.split("\x00")) + f"</a>{trail}"
    parts2 = re.split(r"(https?://[^ ]+)", full)
    return "".join(repl(re.match(r".*", p, re.S)) if p.startswith("http") else E(p).replace("\x00"," ") for p in parts2)
b = '<h1>7. Referências</h1>\n<ul class="refs">' + "".join(f"<li>{ref_html(e)}</li>" for e in ref_entries) + "</ul>"
open(ROOT/"referencias.html","w",encoding="utf-8").write(page("referencias.html","Referências",b))
print(len(ref_entries),"referências;", len(limites),"limites;", len(ordem),"ordem;", len(campos),"campos")

SCRIPT = '<script src="app.js" defer></script>'
etapas = "".join(f'<option value="{e}">{e}</option>' for e in ["Requisitos","Arquitetura","Implementação","Nuvem"])
formas_opt = "".join(f'<option value="{f}">{f}</option>' for f in ["Código","Repositório","Banco de dados","Configuração","Infraestrutura","Documento"])
b = f"""<h1>4. Fichas de Diretrizes</h1>
<div class="ferramentas" role="search">
<div class="campo-busca"><label class="so-leitor" for="busca">Buscar nas fichas</label><input id="busca" type="search" placeholder="Buscar nas fichas" autocomplete="off"></div>
<label class="so-leitor" for="f-etapa">Etapa</label><select id="f-etapa"><option value="">Todas as etapas</option>{etapas}</select>
<label class="so-leitor" for="f-forma">Forma de verificação</label><select id="f-forma"><option value="">Todas as formas</option>{formas_opt}</select>
<span class="chip"><input id="f-cond" type="checkbox"><label for="f-cond">Condicionais</label></span>
<span class="acoes"><button type="button" id="limpar-filtros">Limpar</button><button type="button" id="abrir-todas">Abrir todas</button><button type="button" id="fechar-todas">Fechar todas</button></span>
<p id="contagem" class="contagem" aria-live="polite"></p>
</div>
<noscript><p class="aviso">Esta página precisa de JavaScript para listar as fichas.</p></noscript>
<div id="lista-fichas"></div>"""
open(ROOT/"fichas.html","w",encoding="utf-8").write(page("fichas.html","Fichas de Diretrizes",b,SCRIPT))
b = """<h1>Checklist</h1>
<p>Marque cada item como atende, não atende ou não se aplica. As marcações ficam apenas neste navegador.</p>
<div class="resumo"><p id="resumo-marcas" aria-live="polite"></p>
<div class="linha"><button type="button" class="principal" id="baixar-csv">Baixar CSV</button><button type="button" id="limpar-marcas">Limpar marcações</button></div></div>
<noscript><p class="aviso">Esta página precisa de JavaScript para listar os itens.</p></noscript>
<div id="grupos"></div>"""
open(ROOT/"checklist.html","w",encoding="utf-8").write(page("checklist.html","Checklist",b,SCRIPT))
