# -*- coding: utf-8 -*-
# Grafia americana (decisao D8 do autor). Aplica-se a texto; protege \label, \ref, \cite*, \input,
# \includegraphics e URLs. Nao altera numeros. Uso: python build12_spelling.py arquivo1.tex ...
import sys, re
W=[("centres","centers"),("Centres","Centers"),("centre","center"),("Centre","Center"),
   ("enrolment","enrollment"),("Enrolment","Enrollment"),("enrolments","enrollments"),("enrols","enrolls"),
   ("enrol","enroll"),("Enrol","Enroll"),("neighbourhoods","neighborhoods"),("neighbourhood","neighborhood"),
   ("Neighbourhood","Neighborhood"),("behaviours","behaviors"),("behaviour","behavior"),("behavioural","behavioral"),
   ("Behavioural","Behavioral"),("labour","labor"),("Labour","Labor"),("kilometres","kilometers"),("kilometre","kilometer"),
   ("programme","program"),("judgement","judgment"),("artefact","artifact"),("artefacts","artifacts"),
   ("utilisation","utilization"),("organisation","organization"),("organisations","organizations"),("modelled","modeled")]
PROT=re.compile(r"\\(label|ref|eqref|cite[pt]?|citeauthor|input|includegraphics|url|href)(\[[^\]]*\])*\{[^}]*\}|https?://\S+")
def fix(text):
    out=[]; last=0
    for m in PROT.finditer(text):
        out.append(conv(text[last:m.start()])); out.append(m.group(0)); last=m.end()
    out.append(conv(text[last:])); return "".join(out)
def conv(t):
    for a,b in sorted(W,key=lambda x:-len(x[0])):
        t=re.sub(r"\b"+a+r"\b",b,t)
    return t
if __name__=="__main__":
    n=0
    for f in sys.argv[1:]:
        s=open(f,encoding="utf-8").read(); r=fix(s)
        if r!=s:
            open(f,"w",encoding="utf-8").write(r); n+=1
    print("files changed:",n)
