# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, unicodedata, re, os, pyreadstat
IN=os.path.join(os.path.dirname(__file__),"in")
def _detok(s): return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin1'), str(s))
def norm(s):
    if pd.isna(s): return np.nan
    s=_detok(s).strip().upper()
    s=''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c))
    s=re.sub(r"[^A-Z0-9 ]","",s); s=re.sub(r'\s+',' ',s).strip()
    return s if s else np.nan
def rd(f,**k): return pyreadstat.read_dta(os.path.join(IN,f),**k)[0]
