# Analyse MHCLG Live Table 600 (households on LA housing registers), downloaded 2026-10-26 from
# https://assets.publishing.service.gov.uk/media/6a2be263e50716856ed4afc4/Live_Table_600.ods
# Outputs: table600_england_series.csv, table600_la_breaks.csv, printed summary.
import pandas as pd, numpy as np, os
D = os.path.dirname(os.path.abspath(__file__))
f = os.path.join(D, 'Live_Table_600.ods')
x = pd.read_excel(f, sheet_name=None, engine='odf', header=None)

def tidy(df):
    hdr_row = df.index[df.iloc[:, 0].astype(str).str.strip().isin(['Area code','Local authority code'])][0]
    df.columns = [str(c).replace('.0', '') if isinstance(c, float) else str(c) for c in df.iloc[hdr_row]]
    return df.iloc[hdr_row + 1:].reset_index(drop=True)

reg = tidy(x['Regional_Data'])
years = [c for c in reg.columns if c.isdigit()]
eng = reg[reg['Region'] == 'England'][years].astype(float).iloc[0]
s = pd.DataFrame({'year_ref_date': [('1 April ' if int(y) <= 2018 else '31 March ') + y for y in years],
                  'households': eng.values.astype(int)}, index=[int(y) for y in years])
s['pct_change_yoy'] = (s['households'].pct_change() * 100).round(1)
s.to_csv(os.path.join(D, 'table600_england_series.csv'), index_label='year')
print(s.to_string())

la = tidy(x['Local_Authority_Data'])
print('LA columns:', list(la.columns)[:8])
yrs = [c for c in la.columns if c.isdigit()]
namecol = ['Local authority']
print('name cols', namecol)
vals = la[yrs].apply(pd.to_numeric, errors='coerce')
ch = vals.pct_change(axis=1) * 100
rows = []
for i in range(len(la)):
    for j in range(1, len(yrs)):
        a, b = vals.iloc[i, j - 1], vals.iloc[i, j]
        if pd.notna(a) and pd.notna(b) and a >= 500:
            rows.append({'area_code': la.iloc[i, 0], 'name': la.iloc[i][namecol[0]] if namecol else '',
                         'from_year': int(yrs[j - 1]), 'to_year': int(yrs[j]), 'from': int(a), 'to': int(b),
                         'pct_change': round((b - a) / a * 100, 1)})
br = pd.DataFrame(rows)
br.to_csv(os.path.join(D, 'table600_la_breaks.csv'), index=False)
br['drop50'] = br['pct_change'] <= -50
br['drop30'] = br['pct_change'] <= -30
br['rise50'] = br['pct_change'] >= 50
summ = br.groupby('to_year').agg(n_LAs=('pct_change', 'size'), median_pct=('pct_change', 'median'),
                                 n_drop30=('drop30', 'sum'), n_drop50=('drop50', 'sum'), n_rise50=('rise50', 'sum'))
summ.to_csv(os.path.join(D, 'table600_la_breaks_summary.csv'))
print(summ.to_string())
print('All LA-year transitions (base>=500):', len(br), ' share drop>=30%:', round(br.drop30.mean() * 100, 1),
      ' share drop>=50%:', round(br.drop50.mean() * 100, 1))
print(br.sort_values('pct_change').head(15).to_string())
