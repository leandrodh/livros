import csv, re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dados import RAW
F=["categoria","titulo","autor","serie","genero","ano_leitura","formato","idioma","status","observacao","nota"]
rows=[];cat=None
for l in RAW.strip().splitlines():
    if "|" not in l: cat=l;continue
    p=l.split("|")
    while len(p) < 9: p.append("")
    rows.append(dict(zip(F,[cat]+p[:9]+[""])))
# preserva nota mesmo se o título oficial mudou
ALIASES={
 "Somos Bob":"Somos Legião (Somos Bob)",
 "Fumaça e Espelhos":"Fumaça e Espelhos: Contos e Ilusões",
 "Artemis Fowl 1":"Artemis Fowl",
 "Artemis Fowl 2":"Artemis Fowl: Uma Aventura no Ártico",
 "A Guerra do Velho":"Guerra do Velho",
 "O Círculo dos Dias":"Círculo dos Dias",
 "Armadilha da Singularidade":"A Armadilha da Singularidade",
 "O Horror na Colina de Darrington":"Horror na Colina de Darrington",
 "Angus 1":"Angus: O Primeiro Guerreiro",
 "Angus 2":"Angus: O Guerreiro de Deus",
 "Estudo para Concurso (Pier)":"Inteligência em Concursos",
 "Desvendando o Arco-Íris (Feynman)":"O Arco-Íris de Feynman",
 "O Veneno do Escorpião":"O Doce Veneno do Escorpião",
 "Como Ler Mais e Melhor":"Leitura Eficiente: Como Ler Mais e Melhor",
 "Contos (Neil Gaiman)":"Contos",
 "Por que Engordamos":"Por que Engordamos: e o que Fazer para Evitar",
 "Comprar ou Vender":"Comprar ou Vender?",
 "Antologia 2":"Antologia 2: 1974-1989",
}
os.chdir(os.path.join(os.path.dirname(__file__),".."))
# preserve existing ratings
old={}
if os.path.exists("livros.csv"):
    for r in csv.DictReader(open("livros.csv",encoding="utf-8")):
        old[ALIASES.get(r["titulo"], r["titulo"])]=r.get("nota","")
for r in rows: r["nota"]=old.get(r["titulo"],"")
with open("livros.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,F);w.writeheader();w.writerows(rows)
os.makedirs("generos",exist_ok=True)
slug=lambda s: re.sub(r"[^a-z0-9]+","-",s.lower().translate(str.maketrans("áàãâéêíóôõúç","aaaaeeiooouc"))).strip("-")
idx=[]
for c in dict.fromkeys(r["categoria"] for r in rows):
    rs=[r for r in rows if r["categoria"]==c]; fn=f"generos/{slug(c)}.md"; idx.append((c,fn,len(rs)))
    out=[f"# {c}\n",f"{len(rs)} livros. Nota de 1 a 5 (preencha em `livros.csv` e rode `python scripts/gerar.py`).\n"]
    for a in dict.fromkeys(r["autor"] for r in rs):
        ar=[r for r in rs if r["autor"]==a]
        out+= [f"\n## {a}\n","| Título | Série | Gênero | Ano | Formato | Idioma | Status | Nota |","|---|---|---|---|---|---|---|---|"]
        out+= [f"| {r['titulo']} | {r['serie']} | {r['genero']} | {r['ano_leitura']} | {r['formato']} | {r['idioma']} | {r['status']} | {r['nota']} |" for r in ar]
        notes=[f"- {r['titulo']}: {r['observacao']}" for r in ar if r["observacao"]]
        if notes: out += ["", "Conferência:"] + notes
    open(fn,"w",encoding="utf-8").write("\n".join(out)+"\n")
n=len(rows); au=sum(1 for r in rows if "Audiobook" in r["formato"])
md=["# Livros","","Registro pessoal de leituras e audiobooks, organizado por categoria e autor, para descobrir próximas leituras.","",
f"Total: **{n}** livros · {au} audiobooks registrados · {sum(r['status']=='lendo' for r in rows)} em andamento.","",
"## Categorias",""]+[f"- [{c}]({fn}) — {k}" for c,fn,k in idx]+["",
"## Arquivos","","- `livros.csv` — base única (edite aqui as notas)","- `generos/` — páginas geradas por categoria e autor","- [perfil-e-recomendacoes.md](perfil-e-recomendacoes.md) — análise de gosto e próximos livros","- `scripts/gerar.py` — regenera as páginas a partir dos dados","",
"## Preferências","","- Formato preferido: audiobook, em português ou espanhol.","- Inglês só com atenção total (não ideal para ouvir em treino).",""]
pend=[r for r in rows if r["observacao"]]
md += ["## Notas de conferência","","Títulos ajustados com editoras, Audible e bibliografias. O que ainda precisa de confirmação está marcado abaixo.",""]
md += [f"- **{r['titulo']}** ({r['autor'] or 'autor em aberto'}): {r['observacao']}" for r in pend]
open("README.md","w",encoding="utf-8").write("\n".join(md)+"\n")
print(n,au)
