# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD02 - robustez da decomposicao T3 do BUILD01. Trunc. a direita e estoque->fluxo.
# Descritivo. Reaproveita child_master.feather (BUILD01) + 1a data de encaminhamento.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
B1=(NE_ROOT + r"\03_build\build01\_staging")
STG=(NE_ROOT + r"\03_build\build02\_staging")
EP=pd.Timestamp("1960-01-01")
PANEL_ENC=pd.Timestamp("2019-11-28"); PANEL_MAT=pd.Timestamp("2019-11-27")
def w(df,n): df.to_csv(os.path.join(STG,n),index=False); print("  ->",n)

b=pd.read_feather(os.path.join(B1,"child_master.feather"))
enc=pd.read_feather(os.path.join(STG,"child_dtenc.feather"))
b=b.merge(enc,on="cd_aluno_sme",how="left")
b["dt_sol_ts"]=EP+pd.to_timedelta(b["dt_sol"],unit="D")
b["dt_mat_ts"]=EP+pd.to_timedelta(b["dt_mat_first"],unit="D")
b["fu"]=(PANEL_ENC-b["dt_sol_ts"]).dt.days
b["esp_enc"]=(b["dt_enc"]-b["dt_sol_ts"]).dt.days
b["enc_event"]=b["dt_enc"].notna() & (b["esp_enc"]>=0)
b.loc[b["esp_enc"]<0,"esp_enc"]=np.nan
b["enc180"]=(b["enc_event"] & (b["esp_enc"]<=180)).astype(int)
YEARS=list(range(2010,2019))

# ================= R1b: follow-up por ano =================
print("R1b follow-up:")
rows=[]
for y in YEARS:
    d=b[b["ano_sol"]==y]
    rows.append({"ano_sol":y,"N":len(d),
        "pct_fu180":100*(d["fu"]>=180).mean(),
        "pct_fu365":100*(d["fu"]>=365).mean(),
        "pct_fu730":100*(d["fu"]>=730).mean()})
R1b=pd.DataFrame(rows); w(R1b,"R1b_followup.csv")
comp730=R1b[R1b["pct_fu730"]>=99.9]["ano_sol"].max()
print("  ultimo ano com follow-up 730 completo (>=99.9%):",comp730)

# ================= R2a: espera com janela fixa 180 =================
b["esp180"]=np.where(b["enc_event"] & (b["esp_enc"]<=180), b["esp_enc"], 180.0)
rows=[]
for y in YEARS:
    d=b[b["ano_sol"]==y]
    rows.append({"ano_sol":y,"N":len(d),"pct_enc180":100*d["enc180"].mean(),
                 "espera_180_media":d["esp180"].mean()})
R2a=pd.DataFrame(rows); w(R2a,"R2a_janela180.csv")

# ================= R2b: Kaplan-Meier tempo ate encaminhamento =================
def km(times,events,horizons=(90,180,365,730)):
    # times: dias (evento ou censura); events: 1 evento, 0 censura
    order=np.argsort(times); t=np.asarray(times)[order]; e=np.asarray(events)[order]
    n=len(t); S=1.0; surv=[]; ts=[]; at_risk=n
    i=0; med=np.nan
    uniq=np.unique(t)
    S_at={h:np.nan for h in horizons}
    cur=1.0; idx=0
    tt=t; ee=e
    # passo a passo por tempos de evento
    n_at=n
    surv_curve=[(0,1.0)]
    j=0
    while j<n:
        tj=tt[j]; d=0; c=0
        k=j
        while k<n and tt[k]==tj:
            if ee[k]==1: d+=1
            else: c+=1
            k+=1
        if d>0:
            cur*= (1 - d/n_at)
        n_at-= (k-j)
        surv_curve.append((tj,cur))
        j=k
    # avaliar em horizontes e mediana
    sc=surv_curve
    def S_of(x):
        s=1.0
        for tj,cv in sc:
            if tj<=x: s=cv
            else: break
        return s
    res={h:S_of(h) for h in horizons}
    # mediana KM: menor t com S<=0.5
    medv=np.nan
    for tj,cv in sc:
        if cv<=0.5: medv=tj; break
    return res,medv
print("R2b Kaplan-Meier (sobrevivencia = ainda nao encaminhado):")
rows=[]
for y in YEARS:
    d=b[b["ano_sol"]==y].copy()
    time=np.where(d["enc_event"], d["esp_enc"], d["fu"]).astype(float)
    ev=d["enc_event"].astype(int).values
    ok=time>=0
    res,med=km(time[ok],ev[ok])
    rows.append({"ano_sol":y,"S90":res[90],"S180":res[180],"S365":res[365],"S730":res[730],"mediana_KM_dias":med})
    print(f"  {y}: S180={res[180]:.3f} S365={res[365]:.3f} mediana={med}")
R2b=pd.DataFrame(rows); w(R2b,"R2b_km.csv")

# ================= decomposicao T3 (helper) =================
def decomp(d):
    return pd.Series({"N":len(d),"idade_sol":d["idade_sol"].mean(),
        "espera":d["espera_m"].mean(),"idade_ent":d["idade_ent"].mean()})
def split(tab):
    base=tab.iloc[0]; last=tab.iloc[-1]
    d_ent=last["idade_ent"]-base["idade_ent"]
    d_sol=last["idade_sol"]-base["idade_sol"]; d_esp=last["espera"]-base["espera"]
    return d_ent,d_sol,d_esp,d_sol/d_ent,d_esp/d_ent

# ================= R2c: T3 so com coortes follow-up 730 completo =================
m=b[b["ever_mat"]==1].copy()
COMPYEARS=list(range(2010,int(comp730)+1))
gc=m[m["ano_sol"].isin(COMPYEARS)].groupby("ano_sol").apply(decomp).reset_index()
gc["check"]=gc["idade_sol"]+gc["espera"]-gc["idade_ent"]
w(gc,"R2c_decomp730.csv")
d_ent,d_sol,d_esp,f_sol,f_esp=split(gc)
print(f"R2c (2010-{comp730}): d_ent={d_ent:.2f} d_sol={d_sol:.2f} d_esp={d_esp:.2f} frac_sol={f_sol:.2f} frac_esp={f_esp:.2f}")

# ================= R3a: idade na 1a solicitacao por coorte de nascimento =================
rows=[]
for c in range(2008,2017):
    d=b[b["ano_nasc"]==c]
    rows.append({"coorte_nasc":c,"N":len(d),"idade_sol_media":d["idade_sol"].mean(),
                 "idade_sol_mediana":d["idade_sol"].median()})
R3a=pd.DataFrame(rows); w(R3a,"R3a_coorte.csv")

# ================= R3b: fracao inscrita antes de 6/12/24 meses =================
rows=[]
for c in range(2008,2017):
    d=b[b["ano_nasc"]==c]
    rows.append({"coorte_nasc":c,"N":len(d),
        "pct_ate6m":100*(d["idade_sol"]<6).mean(),
        "pct_ate12m":100*(d["idade_sol"]<12).mean(),
        "pct_ate24m":100*(d["idade_sol"]<24).mean()})
R3b=pd.DataFrame(rows); w(R3b,"R3b_precoce.csv")

# ================= R3c: decomposicao encadeada (ano-a-ano) da idade de solicitacao =================
# Coortes de nascimento em 2010 e 2018 quase nao se sobrepoem (idade = ano_sol - nasc),
# entao a decomposicao 2010-vs-2018 direta e degenerada. Usa-se a identidade exata
# ano-a-ano: d(mean) = sum_c (s1-s0)(mu0+mu1)/2  [composicao]  +  (s0+s1)/2 (mu1-mu0) [within-coorte].
def cells(frame,y):
    d=frame[frame["ano_sol"]==y]; tot=len(d)
    c=d.groupby("ano_nasc").agg(sh=("idade_sol","size"),mu=("idade_sol","mean"))
    c["sh"]/=tot; return c
def chained(frame,y0,y1):
    COMP=0.0; WITHIN=0.0
    for t in range(y0,y1):
        c0=cells(frame,t); c1=cells(frame,t+1)
        idx=sorted(set(c0.index)|set(c1.index))
        for c in idx:
            s0=c0["sh"].get(c,0.0); s1=c1["sh"].get(c,0.0)
            m0=c0["mu"].get(c,np.nan); m1=c1["mu"].get(c,np.nan)
            if np.isnan(m0): m0=m1
            if np.isnan(m1): m1=m0
            COMP+=(s1-s0)*(m0+m1)/2.0
            WITHIN+=(s0+s1)/2.0*(m1-m0)
    return COMP,WITHIN
bb=b[b["ano_sol"].isin(YEARS)].copy()
tot_change=bb[bb.ano_sol==2018]["idade_sol"].mean()-bb[bb.ano_sol==2010]["idade_sol"].mean()
comp,within=chained(bb,2010,2018)
R3c=pd.DataFrame([{"total_change":tot_change,"composicao_coorte":comp,"within_coorte":within,
    "frac_composicao":comp/tot_change,"frac_within":within/tot_change}])
w(R3c,"R3c_shiftshare.csv")
print(f"R3c encadeada: total={tot_change:.2f} comp={comp:.2f}({comp/tot_change:.0%}) within={within:.2f}({within/tot_change:.0%})")

# ================= R3d: fracao de solicitacoes por >24 meses (backlog) =================
rows=[]
for y in YEARS:
    d=b[b["ano_sol"]==y]
    rows.append({"ano_sol":y,"pct_maior24m":100*(d["idade_sol"]>24).mean(),
                 "pct_maior36m":100*(d["idade_sol"]>36).mean()})
R3d=pd.DataFrame(rows); w(R3d,"R3d_backlog.csv")

# ================= R4a: T3 corrigido (730-completo) + within-coorte da idade sol =================
# repartir a queda da idade de entrada: idade_sol (comp+within, encadeada) e espera, 2010-comp730
mc=m[m["ano_sol"].isin(COMPYEARS)].copy()
sol_comp,sol_within=chained(mc,2010,int(comp730))
d_ent,d_sol,d_esp,_,_=split(gc)
R4a=pd.DataFrame([{"periodo":f"2010-{comp730}","d_idade_entrada":d_ent,
    "d_idade_sol":d_sol,"sol_composicao":sol_comp,"sol_within":sol_within,"d_espera":d_esp,
    "frac_sol_total":d_sol/d_ent,"frac_sol_comp":sol_comp/d_ent,"frac_sol_within":sol_within/d_ent,
    "frac_espera":d_esp/d_ent}])
w(R4a,"R4a_final.csv")
print(f"R4a: d_ent={d_ent:.2f} | idade_sol {d_sol:.2f} (comp {sol_comp:.2f}, within {sol_within:.2f}) | espera {d_esp:.2f}")
print("OK build02_build")
