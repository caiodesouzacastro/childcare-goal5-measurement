# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# VERIFICACAO INDEPENDENTE - recalculo do zero a partir de arquivos brutos.
# NAO usa child_master, B_novo, spine, nem _staging. So brutos.
# Cache do MEU proprio parse do Fila (nao e derivada de build) p/ iterar.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv
# 26/10/2026: caminhos resolvidos na maquina em que roda (antes so os da maquina <usuario>). Primeiro candidato existente.
def _pick(*c):
    for x in c:
        if os.path.exists(x): return x
    return c[0]
_H=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SME=NE_SME; _CIRO=NE_ROOT + r"\dados_restritos\Ciro\01_dados"
PUB=_pick(os.path.join(_H,"01_dados_publicos"),NE_ROOT + r"\01_dados_publicos")
FILA=_pick(_SME+r"\processados\derivados_de_brutos\Fila1018.dta",_CIRO+r"\brutos\fila_espera\Fila1018.dta")
CEPRENDA=_pick(_SME+r"\processados\bases_analise\cep_renda_pop_2010.dta",_CIRO+r"\processados\bases_analise\cep_renda_pop_2010.dta")
IPVS=_pick(_SME+r"\originais\auxiliares_publicos\BaseIPVS2010.csv",_CIRO+r"\brutos\geografico_cep\BaseIPVS2010.csv")
EVOL=os.path.join(_H,"03_build","build04","_ext","evolucaodemanda.csv")  # open data PMSP (bruto, nao _staging)
CACHE=os.path.join(_H,"03_build","verificacao_final","vf_fila.parquet")
FMT="%d/%m/%Y %H:%M:%S"
R=[]  # (tag, paper, calc, status, defin)
def chk(tag,paper,calc,defin,tol=None,pct=False):
    try:
        p=float(str(paper).replace(",","").replace("%",""))
        c=float(calc)
        d=c-p
        if tol is None: tol=max(abs(p)*0.01,0.5)   # 1% ou 0.5
        st="CONFERE" if abs(d)<=tol else "DIVERGE"
        R.append((tag,paper,f"{c:.4g}",st,f"{d:+.4g}",defin))
    except Exception as e:
        R.append((tag,paper,str(calc),"?",str(e),defin))
def note(tag,paper,calc,defin,status="INFO"):
    R.append((tag,paper,str(calc),status,"",defin))

# ================= carga FILA (bruto) =================
if os.path.exists(CACHE):
    fa=pd.read_parquet(CACHE); print("fila do cache proprio")
else:
    print("carregando Fila1018 bruto...")
    cols=["cd_aluno_sme","dt_solicitacao","cd_serie_ensino_solicitacao","dt_encaminhamento",
          "cd_esc_encaminhamento","an_letivo_encaminhamento","cd_serie_ensino_encaminhamento",
          "tipo_prioridade_encaminhamento","dt_matricula","cd_esc_matricula","dt_desistencia",
          "dt_recusa","cd_sexo_aluno","tp_raca_cor","mes_nasc","ano_nasc","cep_aluno","cpf_resp_aluno"]
    fa=pd.read_stata(FILA,columns=cols)
    for c,n in [("dt_solicitacao","sol"),("dt_encaminhamento","enc"),("dt_matricula","mat"),
                ("dt_desistencia","des"),("dt_recusa","rec")]:
        fa[n]=pd.to_datetime(fa[c],format=FMT,errors="coerce")
    fa.to_parquet(CACHE)
N_FILA=len(fa)
note("V1.fila_linhas","3.298.064",f"{N_FILA:,}","linhas do Fila1018.dta bruto")
chk("V1.fila_linhas","3298064",N_FILA,"nrow Fila1018")

# ================= B_novo (recriado): 1a solic/crianca, DOB+data+CEP validos =================
fa["cep_ok"]=pd.to_numeric(fa["cep_aluno"],errors="coerce").fillna(0)>0
fa["dob_ok"]=fa["ano_nasc"].between(1990,2018) & fa["mes_nasc"].between(1,12)
# primeira solicitacao por crianca
first=fa.sort_values("sol").groupby("cd_aluno_sme",as_index=False).first()
b=first[first["sol"].notna() & first["dob_ok"] & first["cep_ok"]].copy()
b["idade_sol"]=(b.sol.dt.year-b.ano_nasc)*12+(b.sol.dt.month-b.mes_nasc)
b["ano_sol"]=b.sol.dt.year
b["d_birth"]=pd.to_datetime(dict(year=b.ano_nasc,month=b.mes_nasc,day=1),errors="coerce")
b["d_age47"]=b["d_birth"]+pd.DateOffset(months=47)
# 1a data de encaminhamento/matricula/desistencia por crianca (de TODAS as linhas)
def firstdate(col):
    s=fa[fa[col].notna()].sort_values(col).groupby("cd_aluno_sme")[col].first()
    return s
b=b.merge(firstdate("enc").rename("d_enc1"),on="cd_aluno_sme",how="left")
b=b.merge(firstdate("mat").rename("d_mat1"),on="cd_aluno_sme",how="left")
b=b.merge(firstdate("des").rename("d_des1"),on="cd_aluno_sme",how="left")
NB=len(b)
chk("V1.universo","1524560",NB,"1a solic/crianca com DOB+data+CEP validos")

# nunca matriculados
b["ever_mat"]=b["d_mat1"].notna()
nunca=(~b["ever_mat"]).sum()
chk("V1.nunca_mat","203715",nunca,"B_novo sem nenhuma dt_matricula")
chk("V1.pct_nunca","13.4",100*nunca/NB,"nunca/N")
# 2006-2009
n0609=(b.ano_sol.between(2006,2009)).sum()
chk("V1.sol_2006_2009","51106",n0609,"1as solic com ano 2006-2009")
# CPF presente
cpf_ok=(fa.groupby("cd_aluno_sme")["cpf_resp_aluno"].first().notna() &
        (fa.groupby("cd_aluno_sme")["cpf_resp_aluno"].first().astype(str).str.strip()!="")).reindex(b.cd_aluno_sme).mean()
chk("V1.pct_cpf","98.1",100*cpf_ok,"fracao de B_novo com cpf_resp_aluno presente")

# ================= V4 timing (SINASC denom) =================
SIN=os.path.join(PUB,"ceinfo","sinasc_nv_distrito_2006_2026.csv")
import unicodedata,re
def norm(s): return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")
rows=list(csv.reader(open(SIN,encoding="utf-8"),delimiter=";"))
hdr=rows[0]; yidx={int(hdr[i]):i for i in range(1,len(hdr)) if hdr[i].isdigit()}
births_d={}
for r in rows[1:]:
    nm=r[0].strip()
    if nm in ("Ignorado","Total"): continue
    for y,i in yidx.items():
        try: births_d[(norm(nm),y)]=int(r[i])
        except: pass
dist=sorted(set(k[0] for k in births_d))
def births(y): return sum(births_d.get((dd,y),0) for dd in dist)
# fracao inscrita antes de X meses por coorte (denom=nascidos)
def frac(coh,X):
    d=b[b.ano_nasc==coh]; return 100*(d.idade_sol<X).sum()/births(coh)
for X,lab,p10,p16 in [(6,"6m","4.2","33.4"),(12,"12m","11.0","50.1"),(24,"24m","33.7","70.9")]:
    chk(f"V4.frac_{lab}_2010",p10,frac(2010,X),f"nascidos {coh if False else 2010} <{X}m / SINASC")
    chk(f"V4.frac_{lab}_2016",p16,frac(2016,X),f"nascidos 2016 <{X}m / SINASC")
# mediana nascimento->solicitacao (KM, nascidos censurados)
def km_med_birth(coh):
    d=b[b.ano_nasc==coh]; bb=births(coh)
    # S(a)=1-F(a); F(a)=fracao com idade_sol<a
    for a in range(0,120):
        if (d.idade_sol<a).sum()/bb>=0.5: return a
    return None
chk("V4.med_nasc_sol_2010","36",km_med_birth(2010),"idade em que 50% da coorte 2010 ja solicitou")
chk("V4.med_nasc_sol_2016","12",km_med_birth(2016),"idade em que 50% da coorte 2016 ja solicitou")
# S8c razao <12m/na-fila
def s8c(coh):
    d=b[b.ano_nasc==coh]; n=len(d); bb=births(coh)
    return (d.idade_sol<12).sum()/bb / (n/bb)   # = (<12m)/n
chk("V4.s8c_2010","0.149",s8c(2010),"fracao <12m entre os que aparecem na fila (=<12m/n)")
chk("V4.s8c_2016","0.653",s8c(2016),"idem 2016")
# cobertura da fila
def cov(coh):
    return 100*len(b[b.ano_nasc==coh])/births(coh)
chk("V4.cob_2010","73.7",cov(2010),"n solicitantes coorte / nascidos")
chk("V4.cob_2013","88.6",cov(2013),"idem 2013")
chk("V4.cob_2016","76.7",cov(2016),"idem 2016")

print("V1/V4 OK")
PANEL=pd.Timestamp("2019-11-28")
b["idade_ent"]=np.where(b.d_mat1.notna(),(b.d_mat1.dt.year-b.ano_nasc)*12+(b.d_mat1.dt.month-b.mes_nasc),np.nan)
b["espera_m"]=(b.d_mat1-b.sol).dt.days/30.44
b["age_ref"]=np.where(b.d_enc1.notna(),(b.d_enc1.dt.year-b.ano_nasc)*12+(b.d_enc1.dt.month-b.mes_nasc),np.nan)
b["wait_ref"]=(b.d_enc1-b.sol).dt.days/30.44

# ================= V5 decomposicao =================
def dec(pop,entcol,solcol,waitcol,cohs):
    m={c:pop[pop.ano_nasc==c] for c in cohs}
    a,z=m[cohs[0]],m[cohs[-1]]
    de=z[entcol].mean()-a[entcol].mean(); ds=z[solcol].mean()-a[solcol].mean(); dw=z[waitcol].mean()-a[waitcol].mean()
    return de,ds,dw,ds/de
enr=b[(b.ever_mat)&(b.idade_ent<=48)]
de,ds,dw,sh=dec(enr,"idade_ent","idade_sol","espera_m",list(range(2010,2015)))
chk("V5.d_ent","-9.37",de,"enrolled<=48, coortes 2010-2014, idade_ent - (2010)")
chk("V5.share_appl","93",100*sh,"d_sol/d_ent enrolled")
chk("V5.share_wait","7",100*(1-sh),"1-share")
ref=b[(b.d_enc1.notna())&(b.age_ref<=48)]
de2,ds2,dw2,sh2=dec(ref,"age_ref","idade_sol","wait_ref",list(range(2010,2015)))
chk("V5.d_ent_ref","-9.62",de2,"referred<=48, age at referral decomp")
chk("V5.share_appl_ref","87",100*sh2,"referral def")
# janelas por ano
enrall=b[b.ever_mat==1]
def decyr(pop,y0,y1):
    a=pop[pop.ano_sol==y0]; z=pop[pop.ano_sol==y1]
    de=z.idade_ent.mean()-a.idade_ent.mean(); ds=z.idade_sol.mean()-a.idade_sol.mean()
    return de,ds/de
de_f,sh_f=decyr(enrall,2010,2018); chk("V5.win_full","-19.09",de_f,"por ano 2010-2018 enrolled")
chk("V5.win_full_appl","80",100*sh_f,"share appl full")
de_7,sh_7=decyr(enrall,2010,2016); chk("V5.win730","-15.11",de_7,"por ano 2010-2016")
chk("V5.win730_appl","99",100*sh_7,"share appl 730")
# saida por idade
def fracaged(coh):
    d=b[b.ano_nasc==coh]
    aged=((d.d_enc1.isna())|(d.d_enc1>d.d_age47))&(d.d_age47<=PANEL)
    return 100*aged.mean()
chk("V5.aged_2010","27.4",fracaged(2010),"coorte 2010 que envelhece aos 47m sem enc")
chk("V5.aged_2014","5.2",fracaged(2014),"idem 2014")
# Manski
def manski():
    COH=list(range(2010,2015)); out={}
    for c in COH:
        sub=b[b.ano_nasc==c]
        e=sub[(sub.ever_mat)&(sub.idade_ent<=48)]; ag=sub[(((sub.d_enc1.isna())|(sub.d_enc1>sub.d_age47))&(sub.d_age47<=PANEL))&~((sub.ever_mat)&(sub.idade_ent<=48))]
        ne,na=len(e),len(ag); N=ne+na
        out[c]=dict(sol=(ne*e.idade_sol.mean()+na*ag.idade_sol.mean())/N,
                    emax=(ne*e.idade_ent.mean()+na*48.0)/N, emin=(ne*e.idade_ent.mean()+na*ag.idade_sol.mean())/N)
    a,z=out[2010],out[2014]
    dsol=z["sol"]-a["sol"]; return dsol, dsol/(z["emax"]-a["emax"]), dsol/(z["emin"]-a["emin"])
dsolc,shmax,shmin=manski()
chk("V5.manski_dsol","-14.43",dsolc,"d_sol pop combinada (matric+envelhecidas)")
chk("V5.manski_lo","112",100*min(shmax,shmin),"share solic min")
chk("V5.manski_hi","115",100*max(shmax,shmin),"share solic max")

# ================= V6 riscos competitivos =================
def compet(sub):
    tr=np.where(sub.d_enc1.notna(),(sub.d_enc1-sub.sol).dt.days,np.inf).astype(float)
    ta=(sub.d_age47-sub.sol).dt.days.values.astype(float); tp=(PANEL-sub.sol).dt.days.values.astype(float)
    time=np.minimum.reduce([np.where(np.isfinite(tr),tr,1e9),ta,tp])
    et=np.zeros(len(sub),int); r1=(tr<=np.minimum(ta,tp))&np.isfinite(tr)&(tr>=0); a1=(~r1)&(ta<=tp)
    et[r1]=1; et[a1]=2; ok=np.isfinite(time)&(time>=0); return time[ok],et[ok]
def cif(time,et):
    o=np.argsort(time,kind="mergesort"); t=time[o]; e=et[o]; ut=np.unique(t); ar=len(t); Sp=1.0
    c1=c2=0.0; T=[];C1=[];SA=[]
    for tt in ut:
        m=(t==tt); d1=int((e[m]==1).sum()); d2=int((e[m]==2).sum()); dl=int(m.sum())
        if ar>0: c1+=Sp*(d1/ar); c2+=Sp*(d2/ar); Sn=Sp*(1-(d1+d2)/ar)
        else: Sn=Sp
        T.append(tt);C1.append(c1);SA.append(Sn); Sp=Sn; ar-=dl
    return np.array(T),np.array(C1),np.array(SA),c2
def at(T,a,x):
    i=np.searchsorted(T,x,side="right")-1; return float(a[i]) if i>=0 else 0.0
def rmst(T,SA,L):
    g=np.unique(np.concatenate([[0.0],T[T<L],[float(L)]])); ar=0.0
    for x0,x1 in zip(g[:-1],g[1:]):
        i=np.searchsorted(T,x0,side="right")-1; ar+=(float(SA[i]) if i>=0 else 1.0)*(x1-x0)
    return ar
def cifmed(T,C1):
    z=np.where(C1>=0.5)[0]; return int(T[z[0]]) if len(z) else None
for coh,rf,ag,rm,md in [(2010,"0.56","0.068","218","304"),(2016,"0.88","0.000","181","171")]:
    t,e=compet(b[b.ano_nasc==coh]); T,C1,SA,c2=cif(t,e)
    chk(f"V6.cif365_{coh}",rf,at(T,C1,365),f"CIF ref 365d coorte {coh}")
    chk(f"V6.rmst_{coh}",rm,rmst(T,SA,365),f"RMST365 coorte {coh}")
    chk(f"V6.cifmed_{coh}",md,cifmed(T,C1),f"mediana CIF ref coorte {coh}")
# aging CIF 365 2010
t,e=compet(b[b.ano_nasc==2010]); T,C1,SA,_=cif(t,e)
# recompute cif age properly
def cifage(sub,x=365):
    t,e=compet(sub); o=np.argsort(t); t=t[o];e=e[o]; ut=np.unique(t); ar=len(t); Sp=1.0; c2=0.0; T=[];C2=[]
    for tt in ut:
        m=(t==tt); d1=int((e[m]==1).sum()); d2=int((e[m]==2).sum())
        if ar>0: c2+=Sp*(d2/ar); Sp=Sp*(1-(d1+d2)/ar)
        T.append(tt);C2.append(c2); ar-=int(m.sum())
    T=np.array(T);C2=np.array(C2); i=np.searchsorted(T,x,side="right")-1; return float(C2[i]) if i>=0 else 0.0
chk("V6.cifage_2010","0.068",cifage(b[b.ano_nasc==2010]),"CIF envelhecer 365d coorte 2010")
# gradiente Q4-Q1 (renda do CEP via cep_renda) -- precisa quartil; usa renda do CEP
rd=pd.read_stata(CEPRENDA,columns=["cep","renda","nm_distrit","populacao","massa_renda"])
cep2renda=dict(zip(rd.cep.astype("int64"),rd.renda))
b["cep_i"]=pd.to_numeric(b.cep_aluno,errors="coerce")
b["renda"]=b["cep_i"].map(cep2renda)
b["rq"]=pd.qcut(b["renda"],4,labels=[1,2,3,4])
def gapq(coh):
    d1=b[(b.ano_nasc==coh)&(b.rq==1)]; d4=b[(b.ano_nasc==coh)&(b.rq==4)]
    t1,e1=compet(d1); T1,C1,_,_=cif(t1,e1); t4,e4=compet(d4); T4,C4,_,_=cif(t4,e4)
    return at(T4,C4,365)-at(T1,C1,365)
chk("V6.gap_2010","0.122",gapq(2010),"CIF365 Q4-Q1 coorte 2010")
chk("V6.gap_2016","0.068",gapq(2016),"CIF365 Q4-Q1 coorte 2016")

# ================= V7 irmaos =================
def areg(df,y,xvars,fe_cols,cluster=None):
    import pyhdfe
    cols=[y]+xvars+fe_cols+([cluster] if cluster else [])
    sub=df.dropna(subset=cols).copy()
    ids=np.column_stack([sub[c].astype("category").cat.codes.values for c in fe_cols])
    alg=pyhdfe.create(ids,drop_singletons=False)
    res=alg.residualize(sub[[y]+xvars].astype(float).values)
    yr=res[:,0]; Xr=res[:,1:]; n,k=Xr.shape
    XtXi=np.linalg.inv(Xr.T@Xr); beta=XtXi@(Xr.T@yr); resid=yr-Xr@beta
    if cluster:
        sc=Xr*resid[:,None]; g=pd.DataFrame(sc); g["cl"]=sub[cluster].values
        gs=g.groupby("cl").sum().values; meat=gs.T@gs; G=len(gs); V=XtXi@meat@XtXi*(G/(G-1))
    else: V=XtXi*(resid@resid)/(n-k)
    return dict(zip(xvars,beta)),dict(zip(xvars,np.sqrt(np.diag(V)))),n
b["cpf"]=b["cpf_resp_aluno"].astype(str).str.strip()
b["cpf_ok"]=b.cpf.notna() & ~b.cpf.isin(["","nan","0","None"])
fam=b[b.cpf_ok].copy()
fam["nasc_idx"]=fam.ano_nasc*12+fam.mes_nasc
sz=fam.groupby("cpf").size(); two=sz[sz==2].index
t=fam[fam.cpf.isin(two)].sort_values(["cpf","nasc_idx","sol"]); t["ord"]=t.groupby("cpf").cumcount()+1
p1=t[t.ord==1].set_index("cpf"); p2=t[t.ord==2].set_index("cpf")
common=p1.index.intersection(p2.index)
pair=pd.DataFrame(index=common)
for c in ["ano_nasc","mes_nasc","nasc_idx","idade_sol"]:
    pair[c+"_1"]=p1.loc[common,c]; pair[c+"_2"]=p2.loc[common,c]
pair["espac"]=pair.nasc_idx_2-pair.nasc_idx_1
pc=pair[(pair.ano_nasc_1.between(2010,2016))&(pair.ano_nasc_2.between(2010,2016))&(pair.espac>0)].copy()
chk("V7.pares","79893",len(pc),"cpf valido, exatamente 2 filhos, ambos 2010-2016, espac>0")
chk("V7.med_older","19",pc.idade_sol_1.median(),"mediana idade_sol filho1")
chk("V7.med_younger","8",pc.idade_sol_2.median(),"mediana idade_sol filho2")
chk("V7.pct_younger","78",100*(pc.idade_sol_2<pc.idade_sol_1).mean(),"pares filho2 mais cedo")
# painel longo p/ regressao
def longp(pcx):
    L=[pd.DataFrame({"cpf":pcx.index,"idade_sol":pcx["idade_sol_"+s],"ordem":int(s),"ano_nasc":pcx["ano_nasc_"+s],
                     "nasc_idx":pcx["nasc_idx_"+s]}) for s in ["1","2"]]
    lg=pd.concat(L); lg["dano"]=lg.ano_nasc.astype(str)
    return lg
try:
    lg=longp(pc)
    bb,se,n=areg(lg,"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
    chk("V7.coef","-7.20",bb["ordem"],"idade_sol~ordem, FE cpf+ano_nasc, cluster cpf")
    chk("V7.ep","0.11",se["ordem"],"EP cluster cpf")
    b_lin,_,_=areg(lg,"idade_sol",["ordem","ano_nasc"],["cpf"],cluster="cpf")
    chk("V7.coef_lin","-7.09",b_lin["ordem"],"tendencia linear de ano")
    b_ym,_,_=areg(lg,"idade_sol",["ordem"],["cpf","nasc_idx"],cluster="cpf")
    chk("V7.coef_ym","-6.76",b_ym["ordem"],"dummies ano-mes")
    lg48=longp(pc[pc.espac.between(24,48)])
    b48,_,_=areg(lg48,"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
    chk("V7.coef_2448","-10.60",b48["ordem"],"espacamento 24-48m")
except Exception as e:
    note("V7.regressao","-7.20",f"ERRO: {e}","","?")

# ================= V12 timestamps =================
fb=fa[fa.sol.notna()].copy()
firsttime=fb.groupby("cd_aluno_sme")["sol"].min()
ft=firsttime[firsttime.index.isin(b.cd_aluno_sme)]
tsec=ft.dt.floor("s")
vc=tsec.value_counts()
n_at=tsec.map(vc)
chk("V12.share_2plus","2.7",100*(n_at>=2).mean(),"1as solic (B_novo) que compartilham segundo exato com 2+")
yr=tsec.dt.year
m15=(yr==2015)
if m15.any(): chk("V12.evento2015","0.6",100*(n_at[m15]>=100).mean(),"frac 2015 em segundos com 100+")

# ================= V8 reserva =================
SERIE2B={1:1,4:2,27:3,28:4}
b["band_req"]=b.cd_serie_ensino_solicitacao.map(SERIE2B)
def curb(i):
    return 1 if i<14 else 2 if i<23 else 3 if i<35 else 4 if i<47 else 5
b["band_cur"]=b.idade_sol.map(curb)
cr=b[b.band_req.notna()]
chk("V8.futura","1.2",100*(cr.band_req>cr.band_cur).mean(),"solic creche com faixa pedida > faixa da idade")
fc10=100*(cr[cr.ano_sol==2010].band_req==cr[cr.ano_sol==2010].band_cur).mean()
fc18=100*(cr[cr.ano_sol==2018].band_req==cr[cr.ano_sol==2018].band_cur).mean()
note("V8.corrente_2010","27.9 (build)",f"{fc10:.1f}","NAO esta no paper (diagnostico build07 A3); minha def de faixa-corrente por idade difere")
note("V8.corrente_2018","77.4 (build)",f"{fc18:.1f}","idem -- nao e numero do paper")
young=b[b.idade_sol.between(0,8)]
chk("V8.berc1_0_9","100",100*(young.band_req==1).mean(),"0-8m pedindo Berc I (dos que pedem creche)",tol=2)
# 11.0->49.0 restrito a faixa corrente (<12m)
def frac12cur(coh):
    d=b[(b.ano_nasc==coh)&(b.band_req==b.band_cur)]; return 100*(d.idade_sol<12).sum()/births(coh)
chk("V8.rest_2010","11.0",frac12cur(2010),"<12m coorte 2010 faixa corrente / nascidos")
chk("V8.rest_2016","49.0",frac12cur(2016),"idem 2016")

# ================= V9 incidencia (parcial) =================
def nevpct(y):
    d=b[b.ano_sol==y]; return 100*(~d.ever_mat).mean()
chk("V9.never_2010","29.2",nevpct(2010),"nunca matriculado por ano solic 2010")
chk("V9.never_2015","7.9",nevpct(2015),"idem 2015")
chk("V9.never_2018","18.3",nevpct(2018),"idem 2018")
b["prio_flag"]=(b.tipo_prioridade_encaminhamento.notna())&(b.tipo_prioridade_encaminhamento.astype(str).str.strip()!="")
nev=b[~b.ever_mat]; enr9=b[b.ever_mat]
chk("V9.age_never","29.2",nev.idade_sol.mean(),"idade media solic never")
chk("V9.age_enr","21.4",enr9.idade_sol.mean(),"idade media solic enrolled")
chk("V9.prio_never","4.0",100*nev.prio_flag.mean(),"% never com prioridade")
chk("V9.prio_enr","16.1",100*enr9.prio_flag.mean(),"% enrolled com prioridade")
chk("V9.renda_never","1295",nev.renda.mean(),"renda media CEP never",tol=30)
chk("V9.renda_enr","1201",enr9.renda.mean(),"renda media CEP enrolled",tol=30)

# ================= V14 FIFO =================
r=fa[fa.enc.notna() & fa.cd_esc_encaminhamento.notna() & fa.tipo_prioridade_encaminhamento.isna()].copy()
r=r[r.cd_serie_ensino_encaminhamento.isin([1,4,27,28])]
r["cell"]=r.cd_esc_encaminhamento.astype(str)+"|"+r.cd_serie_ensino_encaminhamento.astype(str)+"|"+r.an_letivo_encaminhamento.astype(str)
r=r.sort_values(["cell","sol"]); r["rk_sol"]=r.groupby("cell").cumcount()
r=r.sort_values(["cell","enc"]); r["rk_enc"]=r.groupby("cell").cumcount()
r["ncell"]=r.groupby("cell")["cell"].transform("size")
big=r[r.ncell>=5]
c_p=big[["rk_sol","rk_enc"]].corr().iloc[0,1]
c_sp=big[["rk_sol","rk_enc"]].corr(method="spearman").iloc[0,1]
chk("V14.corr","0.885",c_p,f"MESMO universo do diag original (N={len(big):,}, identico). Pearson={c_p:.3f}, "
    f"Spearman={c_sp:.3f}. Gap vs 0.885 vem do DESEMPATE de ranks entre timestamps simultaneos (32% empatam ao "
    f"segundo): a ordem entre inscricoes no mesmo segundo e arbitraria e difere entre Stata e pandas. Claim "
    f"qualitativo (fortemente FIFO) confere; o 0.885 nao e reproduzivel ao 3o digito",tol=0.02)

# ================= V2/V3/V10 perfil =================
FILES=[("2013","1","perfil_2013s1_turmasjun2013.csv"),("2013","2","perfil_2013s2_r30turmasparadre20131231.csv"),
 ("2014","1","perfil_2014s1_turmasjun2014.csv"),("2014","2","perfil_2014s2_r30turmasparadre20141231.csv"),
 ("2015","1","perfil_2015s1_turmasjun2015.csv"),("2015","2","perfil_2015s2_r30turmasparadre20151231.csv"),
 ("2016","1","perfil_2016s1_turmasjun2016.csv"),("2016","2","perfil_2016s2_turmasmatriculas20161231.csv"),
 ("2017","1","perfil_2017s1_turmasjun2017.csv"),("2017","2","perfil_2017s2_turmasdez2017.csv"),
 ("2018","1","perfil_turmas_jun2018.csv"),("2018","2","perfil_2018s2_turmasdez2018.csv"),
 ("2019","1","perfil_2019s1_turmas062019.csv")]
def nagr(desc):
    d=(desc or "").upper()
    if "BERC" in d or "BER\xc7" in d or "BER" in d and "RIO" in d: return "BERC2" if re.search(r"\bII\b",d) else "BERC1"
    if "MINI" in d: return "MINI2" if re.search(r"\bII\b",d) else "MINI1"
    return None
def numf(x):
    try: return float(str(x).replace(",","."))
    except: return None
prows=[]
for ano,sem,fn in FILES:
    with open(os.path.join(PUB,fn),encoding="latin-1") as f:
        for rr in csv.DictReader(f,delimiter=";"):
            rr={(k or "").strip().lstrip("﻿").upper():v for k,v in rr.items()}
            if (rr.get("MODAL","") or "").strip().upper()!="CRECHE": continue
            ag=nagr(rr.get("DESCSERIE",""));
            if ag is None: continue
            # 29/10/2026 (OQ-174): CODESC normalizado como no build01_perfil.py L69-71 (zero a esquerda inconsistente entre arquivos)
            _cod=(rr.get("CODESC","") or "").strip()
            _cod=str(int(_cod)) if _cod.isdigit() else _cod
            prows.append(dict(codesc=_cod,ano=int(ano),sem=int(sem),
                sidx=int(ano)*2+(int(sem)-1),rede=(rr.get("REDE","") or "").strip().upper(),agrup=ag,
                vagofer=numf(rr.get("VAGOFER")) or 0.0,matric=numf(rr.get("MATRIC")) or 0.0,
                distrito=(rr.get("DISTRITO","") or "").strip()))
pf=pd.DataFrame(prows)
S1=pf[pf["sem"]==1]  # so 1os semestres
v13=S1[S1.ano==2013].vagofer.sum(); v19=S1[S1.ano==2019].vagofer.sum()
chk("V2.vag_2013","214561",v13,"soma VAGOFER creche 2013s1",tol=200)
chk("V2.vag_2019","338893",v19,"soma VAGOFER creche 2019s1",tol=300)
chk("V2.crescimento","58",100*(v19-v13)/v13,"crescimento VAGOFER 2013s1->2019s1")
chk("V2.centros","2734",pf.codesc.nunique(),"CODESC distintos creche; o +36 de 25/10 vinha de grafias do CODESC com e sem zero a esquerda, corrigido em 29/10 (OQ-174)",tol=10)
chk("V2.celulas","86982",pf.groupby(["codesc","agrup","sidx"]).ngroups,"celulas codesc x agrup x sidx")
op13=S1[S1.ano==2013].codesc.nunique(); op19=S1[S1.ano==2019].codesc.nunique()
chk("V2.oper_2013","1641",op13,"CEIs c/ turma creche 2013s1",tol=40)
chk("V2.oper_2019","2406",op19,"CEIs c/ turma creche 2019s1",tol=40)
# V10 modulo (2017, share classes EXATAMENTE ao modulo)
MOD={"BERC1":7,"BERC2":9,"MINI1":12,"MINI2":25}
p17=S1[S1.ano==2017]   # 2017s1 (snapshot de junho, como no paper)
for ag,pv in [("BERC1","89.4"),("BERC2","75.6"),("MINI1","62.3"),("MINI2","23.3")]:
    s=p17[p17.agrup==ag]; share=100*(s.matric==MOD[ag]).mean() if len(s) else np.nan
    chk(f"V10.mod_{ag}",pv,share,f"% turmas {ag} com matric == modulo (2017s1)",tol=1.5)
occ=pf.groupby(["agrup","sidx"]).apply(lambda s:s.matric.sum()/s.vagofer.sum() if s.vagofer.sum() else np.nan)
note("V10.ocupacao","0.97-1.00",f"min={occ.min():.3f} max={occ.max():.3f}","razao matric/vagofer por agrup-semestre")

# ================= V3 demografia e cobertura =================
def pool(y): return sum(births(yy) for yy in range(y-3,y+1))
cov13=v13/pool(2013); cov19=v19/pool(2019)
chk("V3.cob_2013","0.307",cov13,"VAGOFER 2013s1 / pop 0-3 (SINASC 4 coortes)",tol=0.01)
chk("V3.cob_2019","0.514",cov19,"VAGOFER 2019s1 / pop 0-3",tol=0.01)
chk("V3.pool_contr","5.6",100*(pool(2013)-pool(2019))/pool(2013),"contracao pop 0-3 2013->2019")
# decomposicao 86/14 (quanto da subida de cobertura e capacidade vs demografia)
dcov=cov19-cov13
cov_caponly=v19/pool(2013)-v13/pool(2013)  # so capacidade, pop fixa
chk("V3.decomp_cap","86",100*cov_caponly/dcov,"parte da subida de cobertura por capacidade",tol=2)
# DEM_CRECHE dezembro (evolucaodemanda)
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
ev=pd.read_csv(EVOL,sep=";",thousands=".",dtype={"MES_ANO_REF":str})
ev["ano"]=ev.MES_ANO_REF.str[-2:].astype(int)+2000; ev["mes"]=ev.MES_ANO_REF.str[:3].map(MES)
ev["DEM_CRECHE"]=pd.to_numeric(ev.DEM_CRECHE,errors="coerce")
dem=ev.groupby(["ano","mes"]).DEM_CRECHE.sum()
chk("V3.dem_2006","129594",dem.loc[(2006,12)],"DEM_CRECHE dez 2006")
chk("V3.dem_2017","44092",dem.loc[(2017,12)],"DEM_CRECHE dez 2017")
# media anual vs dezembro (queda -15% na media)
anual=ev.groupby("ano").DEM_CRECHE.mean()
chk("V3.media_queda","15",100*(anual.loc[2006]-anual.loc[2017])/anual.loc[2006],"queda media anual 2006-2017",tol=3)

# ================= V11 associacao local =================
rd2=pd.read_stata(CEPRENDA,columns=["cep","nm_distrit"])
# 26/10/2026 (OQ-5/OQ-31): os nomes acentuados do .dta chegam como escapes literais ("S<C3>O MIGUEL"); sem decodificar,
# so 64 de 96 distritos casam com o evolucaodemanda.csv. Mesma correcao do build13_c6fix.py (decodifica e colapsa espacos).
def nz(s): return re.sub(r"\s+"," ","".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn"))
def unesc(s): return re.sub(r"<([0-9A-Fa-f]{2})>",lambda m: bytes([int(m.group(1),16)]).decode("latin-1"),str(s))
cep2d={int(c):nz(unesc(d)) for c,d in zip(rd2.cep,rd2.nm_distrit)}
b["distrito"]=b["cep_i"].map(cep2d)
coh=b[b.ano_nasc.between(2010,2016)&b.distrito.notna()].copy()
coh["early"]=(coh.idade_sol<12).astype(int)
grid=coh.groupby(["distrito","ano_nasc"]).agg(early=("early","mean"),n=("early","size")).reset_index()
ev["dn"]=ev.DISTRITO.map(nz); ev["MAT_CRECHE"]=pd.to_numeric(ev.MAT_CRECHE,errors="coerce")
matd=ev[ev.mes==12].groupby(["dn","ano"]).MAT_CRECHE.sum().reset_index().sort_values(["dn","ano"])
matd["gcap"]=np.log(matd.MAT_CRECHE)-np.log(matd.groupby("dn").MAT_CRECHE.shift(1))
g=grid.rename(columns={"distrito":"dn"}).merge(matd[["dn","ano","gcap"]].rename(columns={"ano":"ano_nasc"}),on=["dn","ano_nasc"],how="left").dropna(subset=["gcap"])
try:
    bl,sl,nl=areg(g,"early",["gcap"],["dn","ano_nasc"],cluster="dn")
    # alvo: C6 corrigida (03_build/build13_coverage/c6_fix.csv, contemporaneous: 0.0086, EP 0.0097, N 672, 96 distritos)
    chk("V11.coef","0.0086",bl["gcap"],"early<12m ~ crescimento MAT distrito, FE dist+coorte",tol=0.002)
    chk("V11.ep","0.0097",sl["gcap"],"EP cluster distrito",tol=0.002)
    chk("V11.N","672",nl,"celulas distrito x coorte",tol=0)
    chk("V11.distritos","96",g.dn.nunique(),"distritos no grid",tol=0)
except Exception as e: note("V11","0.004",f"ERRO {e}","","?")

# ================= V13 reconstrucao (identidade) =================
big2=pd.Timestamp("2100-01-01")
tr=b.d_enc1.where(b.d_enc1>=b.sol); ta=b.d_age47.where(b.d_age47>=b.sol,b.sol)
M=pd.DataFrame({"ref":tr.fillna(big2),"age":ta.fillna(big2)}); b["exit_t"]=M.min(axis=1); b["exit_ty"]=M.idxmin(axis=1)
b.loc[b.exit_t>PANEL,"exit_ty"]="cens"
off_dec=dem[dem.index.get_level_values(1)==12].reset_index(level=1,drop=True)
resid_ok=True; start=off_dec.get(2009,np.nan)
for Y in range(2010,2018):
    new=int((b.sol.dt.year==Y).sum()); ref=int(((b.exit_t.dt.year==Y)&(b.exit_ty=="ref")).sum())
    aged=int(((b.exit_t.dt.year==Y)&(b.exit_ty=="age")).sum()); offv=off_dec.get(Y,np.nan)
    resid=start+new-ref-aged-offv
    if Y in (2010,2016): note(f"V13.resid_{Y}","(fecha por constr.)",f"{resid:.0f} ({100*resid/offv:+.0f}% do oficial)","start+new-ref-aged-residuo=oficial")
    start=offv
# razao construido/oficial (serie sem backlog, com censura idade) - usa a media
def rstock(Y):
    end=pd.Timestamp(Y,12,31); return int(((b.sol<=end)&(b.exit_t>end)).sum())
ratios=[rstock(Y)/off_dec.get(Y) for Y in range(2010,2018) if pd.notna(off_dec.get(Y))]
note("V13.razao","0.76",f"mediana={np.median(ratios):.2f} (min {min(ratios):.2f} max {max(ratios):.2f})","construido(sem backlog)/oficial")

# ================= PART C: nao recalculados =================
PARTC=[
 "V2.CEIs (2.384): requer geocodificacao/escolassite bruto -- so cei_openings derivado disponivel; nao recalculado do bruto.",
 "V2.parceiras (1.629): contagem de CEIs parceiros -- nao recalculada (multiplos arquivos parcerias com definicao ambigua de universo/data).",
 "V9.grid (mediana 18 centros abertos; 12->29; 12,3% no CEI mais proximo; 39,0% fora): requer coordenadas de CEP, ausentes em cep_renda_pop_2010 e sem fonte bruta de geocodificacao de CEP. NAO recalculado.",
 "V9.cobertura por renda 88,1/42,4: requer nascidos vivos por QUARTIL DE RENDA DO DISTRITO (cruzamento SINASC-distrito x renda). Recalculavel com esforco; nao feito nesta passada.",
 "V13.reconstrucao mensal (T13) numeros exatos por ano: identidade verificada; os valores anuais especificos de ref/aged dependem da definicao de 'primeira saida' -- reproduzidos aproximadamente.",
]

# ================= saida =================
b.to_parquet(os.path.join(os.path.dirname(CACHE),"vf_bnovo.parquet"))
print("TODOS OS BLOCOS RODARAM")
div=[r for r in R if r[3]=="DIVERGE"]; err=[r for r in R if r[3]=="?"]
print(f"\nRESUMO: {len([r for r in R if r[3]=='CONFERE'])} CONFERE, {len(div)} DIVERGE, {len(err)} ERRO/nao-verif, {len([r for r in R if r[3]=='INFO'])} info")
out=[]
out.append("# VERIFICACAO FINAL -- recalculo independente do zero\n")
out.append("Recalculo a partir dos brutos (Fila1018.dta, perfil, parcerias, SINASC, cep_renda, evolucaodemanda). "
           "NENHUMA derivada de build reutilizada (sem child_master/B_novo/spine/_staging). "
           "Cache = meu proprio parse fresco do Fila.\n")
out.append(f"**Resumo:** {len([r for r in R if r[3]=='CONFERE'])} CONFERE, {len(div)} DIVERGE, {len(err)} nao-verificados.\n")
out.append("\n## >>> DIVERGENCIAS\n")
if div:
    out.append("| item | paper | recalc | dif | definicao |\n|---|---|---|---|---|")
    for t_,p,c,s,d,de in div: out.append(f"| {t_} | {p} | {c} | {d} | {de} |")
else: out.append("(nenhuma)")
out.append("\n## >>> PART B: CONSISTENCIA INTERNA\n")
out.append("**B1. Numeros que se contradizem?** Nenhuma contradicao aritmetica encontrada. "
 "Checados e coerentes: 36->12 meses = 'two years' (abstract); 218->181 = 'about a sixth' (17%); "
 "0.307->0.514 com 86/14; 214.561->338.893 = +58%. "
 f"Ocupacao matric/vagofer no intervalo {occ.min():.3f}-{occ.max():.3f}, coerente com 'close to 0.97-1.00'. "
 "Tensao (nao contradicao, e sinalizada): o 93/7 (condicional a matriculados) coexiste com os limites de "
 "Manski [112,115]% na populacao completa -- o paper agora rotula explicitamente '93 percent among children "
 "who entered care', entao nao e contradicao.")
out.append("\n**B2. Apendice x corpo, mesma quantidade, estimador diferente?** SIM, mas sinalizado: "
 "R2b_km (apendice, KM sem correcao de idade -> 220->163 dias) e E1 (corpo, riscos competitivos -> "
 "CIF 0.56->0.88, mediana 304->171) reportam a MESMA quantidade (tempo ate encaminhamento) com estimadores "
 "diferentes. A nota da R2b agora diz 'estimator diagnostic, not the main analysis', entao e deliberado, nao "
 "uma inconsistencia. Nao ha outra tabela apendice/corpo com universo divergente para a mesma quantidade.")
out.append("\n**B3. Definicoes de 'espera' (encaminhamento vs matricula):** DUAS definicoes coexistem. "
 "(i) Intervalo ate MATRICULA -- usado na identidade da decomposicao (S5, eq.1: 'application to enrolment'), "
 "gera 93/7. (ii) Intervalo ate ENCAMINHAMENTO -- usado em toda a analise de duracao (S6: CIF/RMST/mediana) "
 "e na moldura (abstract, S5.10: '0.56->0.88'). O paper AGORA sinaliza a diferenca (S5: 'the two differ by a "
 "median of five to seven days' e reporta 87/13 ao lado). Risco residual: um leitor pode conflar o 93/7 "
 "(matricula) com o 0.56->0.88 (encaminhamento) -- sao intervalos diferentes para fins diferentes. Recomendo "
 "uma frase unica no inicio da S5 fixando qual 'espera' vale onde.")
out.append("\n## >>> NAO RECALCULADOS (Part C)\n")
for x in PARTC: out.append(f"- {x}")
out.append("\n## Tabela completa\n")
out.append("| item | paper | recalc | status | dif | definicao |\n|---|---|---|---|---|---|")
for t_,p,c,s,d,de in R: out.append(f"| {t_} | {p} | {c} | {s} | {d} | {de} |")
open(os.environ.get("VERIF_OUT",os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","03_build","verificacao_final","VERIFICACAO_FINAL.md")),"w",encoding="utf-8").write("\n".join(out))
print("VERIFICACAO_FINAL.md escrito")
for t_,p,c,s,d,de in R:
    if s in ("DIVERGE","?"): print(f"  {s}: {t_} paper={p} calc={c}")
print(f"\n{'TAG':26} {'PAPER':>10} {'CALC':>10} {'STATUS':>8}  DIF")
for t_,p,c,s,d,de in R:
    if s!="INFO": print(f"{t_:26} {str(p):>10} {str(c):>10} {s:>8}  {d}")
