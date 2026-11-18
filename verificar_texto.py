#!/usr/bin/env python3
"""Confere se o texto do site é fiel ao PDF do guia.

Uso:  python3 verificar_texto.py guia-pratico.pdf site/
Lê todos os .html e .json da pasta do site, extrai as frases e verifica se cada uma
existe no texto do PDF (ignorando espaços e quebras de linha). Frases da interface
(botões, filtros, rodapé) devem ser listadas em textos_interface.txt, uma por linha,
para serem ignoradas. Precisa do pdftotext (pacote poppler-utils). Só usa a biblioteca padrão.
"""
import html, json, pathlib, re, subprocess, sys

def norm(t):
    t = t.replace("​", "").replace("●", "").replace("“", '"').replace("”", '"')
    t = re.sub(r"\s+", " ", t)
    return t.replace(" .", ".").strip()

pdf, pasta = sys.argv[1], pathlib.Path(sys.argv[2])
G = norm(subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True, check=True).stdout)
ignorar = set()
lista = pasta / "textos_interface.txt"
if lista.exists():
    ignorar = {norm(l) for l in lista.read_text(encoding="utf-8").splitlines() if l.strip()}

textos = []
for arq in pasta.rglob("*"):
    if arq.suffix == ".html":
        h = arq.read_text(encoding="utf-8")
        h = re.sub(r"(?s)<(script|style)\b.*?</\1>", " ", h)
        textos += [(arq, t) for t in re.split(r"<[^>]+>", h)]
    elif arq.suffix == ".json":
        def varre(x):
            if isinstance(x, str): textos.append((arq, x))
            elif isinstance(x, dict): [varre(v) for v in x.values()]
            elif isinstance(x, list): [varre(v) for v in x]
        varre(json.loads(arq.read_text(encoding="utf-8")))

falhas = 0
for arq, t in textos:
    t = norm(html.unescape(t))
    if len(t) < 25 or t in ignorar:
        continue
    for frase in re.split(r"(?<=[.!?])\s+", t):
        if len(frase) >= 25 and frase not in ignorar and frase not in G:
            falhas += 1
            print(f"{arq}: NÃO está no PDF: {frase[:120]}")
print(f"\n{falhas} frase(s) fora do PDF." if falhas else "\nTodo o texto do site está no PDF do guia.")
sys.exit(1 if falhas else 0)
