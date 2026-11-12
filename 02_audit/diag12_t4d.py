# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG12 TESTE 4 (complemento) - T4d com coordenadas brutas (o cep_cei_pairs esta
# truncado em ~2km, entao dist>2km precisa de haversine CEP->CEI), T4e com irmao
# (sib_mat = data de matricula do irmao; presenca = tem irmao matriculado), e
# placebos limpos (sem FE de distrito, que tornava jul/2015 singular).
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
AUD=NE_ROOT + r"\02_audit"
STG=NE_ROOT + r"\03_build\build01\_staging"
FILAdir=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera"

def hav(lat1,lon1,lat2,lon2):
    R=6371.0; p=np.pi/180
    a=(np.sin((lat2-lat1)*p/2)**2 +
       np.cos(lat1*p)*np.cos(lat2*p)*np.sin((lon2-lon1)*p/2)**2)
    return 2*R*np.arcsin(np.sqrt(a))

b=pd.read_feather(os.path.join(STG,"child_master.feather"))
mm=b[b["ever_mat"]==1].copy()
mm["esc"]=mm["cd_esc_matricula"]
# coords
cep=pd.read_stata(os.path.join(FILAdir,"cepcen.dta"))  # cep, longitude, latitude
cei=pd.read_stata(os.path.join(AUD,"cei_openings_novo.dta"),columns=["ceicode","ceilat","ceilon"])
ceiset=set(cei["ceicode"].unique())
mm["esc_int"]=mm["esc"].apply(lambda x:int(x) if pd.notna(x) else -1)
mm["esc_known"]=mm["esc_int"].isin(ceiset)
mm=mm.merge(cep.rename(columns={"latitude":"clat","longitude":"clon"})[["cep","clat","clon"]],
            left_on="cep_aluno",right_on="cep",how="left")
mm=mm.merge(cei.rename(columns={"ceicode":"esc_int","ceilat":"elat","ceilon":"elon"}),on="esc_int",how="left")
mm["dist_raw"]=hav(mm["clat"],mm["clon"],mm["elat"],mm["elon"])

tot=len(mm)
sem_coord=(~mm["esc_known"]) | mm["elat"].isna() | mm["clat"].isna()
geo=mm[~sem_coord].copy()
far=geo[geo["dist_raw"]>2.0]
print(f"### T4d: decomposicao dos {tot} matriculados ###")
print(f"  (i) escola sem coordenada valida: {int(sem_coord.sum())} ({100*sem_coord.mean():.1f}%)")
print(f"  (ii) escola geolocalizada: {len(geo)} ({100*len(geo)/tot:.1f}%); destas dist>2km: {len(far)} ({100*len(far)/tot:.1f}% do total)")
if len(far):
    q=far["dist_raw"].quantile([.5,.75,.9,.95,.99])
    print(f"      dist>2km (haversine): mediana={q[.5]:.2f} p75={q[.75]:.2f} p90={q[.9]:.2f} p95={q[.95]:.2f} p99={q[.99]:.2f} max={far['dist_raw'].max():.1f}")
    print(f"      dessas: <=3km={100*(far['dist_raw']<=3).mean():.1f}%  3-5km={100*((far['dist_raw']>3)&(far['dist_raw']<=5)).mean():.1f}%  >5km={100*(far['dist_raw']>5).mean():.1f}%  >10km={100*(far['dist_raw']>10).mean():.1f}%")
    far["dist_raw"].round(1).to_frame().to_csv(os.path.join(STG,"t4d_dist_far.csv"),index=False)
# distribuicao geral da distancia bruta das matriculas geolocalizadas
qg=geo["dist_raw"].quantile([.25,.5,.75,.9,.95])
print(f"  (geolocalizadas) dist bruta: p25={qg[.25]:.2f} p50={qg[.5]:.2f} p75={qg[.75]:.2f} p90={qg[.9]:.2f} p95={qg[.95]:.2f}")

# ---------- T4e ----------
sib=pd.read_stata(os.path.join(AUD,"sibmat.dta"))
sib["tem_irmao"]=sib["sib_mat"].notna().astype(int)
mm=mm.merge(sib[["cd_aluno_sme","tem_irmao"]],on="cd_aluno_sme",how="left")
mm["tem_irmao"]=mm["tem_irmao"].fillna(0)
mm["fora"]=(sem_coord | (mm["dist_raw"]>2)).astype(int)
print("\n### T4e: fora do conjunto <=2km vs dentro ###")
for v,lab,mult in [("renda","Renda CEP",1),("prio","% prioridade",100),
                   ("ano_sol","Ano solic.",1),("tem_irmao","% com irmao matriculado",100),
                   ("dist_nearest","Dist. ao CEI mais proximo (km)",1)]:
    x=mm.loc[mm["fora"]==1,v].astype(float); y=mm.loc[mm["fora"]==0,v].astype(float)
    dif=(x.mean()-y.mean())*mult; se=np.sqrt(x.var()/x.notna().sum()+y.var()/y.notna().sum())*mult
    print(f"  {lab}: fora={x.mean()*mult:.2f} dentro={y.mean()*mult:.2f} dif={dif:+.2f} (EP {se:.3f})")
print("\nOK diag12_t4d")
