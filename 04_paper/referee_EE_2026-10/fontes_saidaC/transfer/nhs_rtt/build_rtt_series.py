# Build a monthly series of "% of incomplete RTT pathways within 18 weeks" (England, incl. estimates
# for missing trusts) from Table 2 of NHS England RTT Statistical Press Notices (PDFs downloaded
# 2026-10-26 from england.nhs.uk/statistics/wp-content/...; text extracted with pypdf to *.txt).
# The RTT Overview Timeseries xlsx could not be downloaded (england.nhs.uk HTML pages sit behind an
# AWS WAF JavaScript challenge), so this series is assembled from the press notices instead.
# For each month the most recent vintage (latest notice) is kept. Output: rtt_pct18_monthly.csv,
# rtt_march_vs_other_months.csv, and printed summary.
import re, os
import pandas as pd

D = os.path.dirname(os.path.abspath(__file__))
# (file, publication order) - later = more recent vintage
FILES = ['Sep17_RTT-statistical-press-notice-PDF-295K-98673.txt',
         'Mar19-RTT-SPN-publication-version.txt',
         'Mar21-RTT-SPN-publication-version-1.txt',
         'Apr22-RTT-SPN-pre-release.txt',
         'Mar23-RTT-SPN-publication-version.txt',
         'Mar24-RTT-SPN-Pre-Publication-PDF-K.txt',
         'Mar25-RTT-SPN-Publication-PDF-384K-38145.txt',
         'Mar26-RTT-statistical-press-notice.txt',
         'Aug26-RTT-statistical-press-notice.txt']
MON = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10,
       'nov': 11, 'dec': 12}
pat = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[- ](\d{2}|\d{4})\*?\s+([\d.]+)\s+([\d.]+\+?)\s+([\d.]+)\s*%')
rows = []
for k, f in enumerate(FILES):
    for line in open(os.path.join(D, f), encoding='utf-8'):
        line = re.sub(r'\s+', ' ', line.strip())
        m = pat.match(line)
        if not m:
            continue
        y = int(m.group(2)); y = y + 2000 if y < 100 else y
        rows.append({'year': y, 'month': MON[m.group(1).lower()[:3]], 'median_wk': float(m.group(3)),
                     'p92_wk': m.group(4), 'pct_within_18wk': float(m.group(5)), 'source': f, 'vintage': k})
raw = pd.DataFrame(rows)
raw.to_csv(os.path.join(D, 'rtt_pct18_all_vintages.csv'), index=False)
s = raw.sort_values('vintage').groupby(['year', 'month']).last().reset_index()
s['date'] = pd.to_datetime(dict(year=s.year, month=s.month, day=1))
s = s.sort_values('date')
s.to_csv(os.path.join(D, 'rtt_pct18_monthly.csv'), index=False)

# Vintage revisions of March values
rev = raw[raw.month == 3].pivot_table(index='year', columns='vintage', values='pct_within_18wk')
print('March values by vintage (columns = notice order):'); print(rev.to_string())

# Continuous monthly coverage
mon = s[s.date >= '2016-04-01'].set_index('date')
full = pd.date_range('2016-04-01', mon.index.max(), freq='MS')
print('Months missing in continuous span:', [d.strftime('%Y-%m') for d in full if d not in mon.index])

# Financial years Apr(t-1)..Mar(t): is March the max/min? March vs mean of other 11 months.
out = []
for fy in range(2017, 2027):
    # use ONE vintage per FY: the earliest notice containing all 12 months (contemporaneous figures)
    raw['date'] = pd.to_datetime(dict(year=raw.year, month=raw.month, day=1))
    cand = None
    for v in sorted(raw.vintage.unique()):
        rv = raw[(raw.vintage == v) & (raw.date >= f'{fy-1}-04-01') & (raw.date <= f'{fy}-03-01')]
        if rv.date.nunique() == 12:
            cand = rv.drop_duplicates('date').set_index('date').sort_index(); break
    if cand is None:
        continue
    w = cand['pct_within_18wk']
    vint_src = cand['source'].iloc[0]
    mar = w.loc[f'{fy}-03-01']; oth = w.drop(pd.Timestamp(f'{fy}-03-01'))
    feb = w.loc[f'{fy}-02-01']
    out.append({'FY_ending_March': fy, 'March': mar, 'Feb': feb, 'March_minus_Feb_pp': round(mar - feb, 1),
                'mean_other11': round(oth.mean(), 2), 'min_other11': oth.min(), 'max_other11': oth.max(),
                'March_minus_mean_other_pp': round(mar - oth.mean(), 2),
                'rank_of_March_1=highest': int((w > mar).sum() + 1),
                'March_is_max': bool(mar >= w.max()), 'March_is_min': bool(mar <= w.min()),
                'range_within_FY_pp': round(w.max() - w.min(), 1), 'source_notice': vint_src})
fyd = pd.DataFrame(out)
# Year-on-year change of March value (Mar t vs Mar t-1), from the March series (latest vintage)
marser = s[s.month == 3].set_index('year')['pct_within_18wk']
fyd['March_yoy_change_pp_latest_vintage'] = fyd['FY_ending_March'].map(lambda y: round(marser.get(y) - marser.get(y - 1), 1))
fyd.to_csv(os.path.join(D, 'rtt_march_vs_other_months.csv'), index=False)
pd.set_option('display.width', 250)
print(fyd.to_string(index=False))
# Month-on-month changes: distribution, and the Feb->Mar change in 2026
mm = mon['pct_within_18wk'].diff().dropna()
print('Month-on-month change (pp), Apr2016-Aug2026 excl. Mar2020-Mar2021 Covid months:')
mmx = mm[~((mm.index >= '2020-03-01') & (mm.index <= '2021-03-01'))]
print(' n=', len(mmx), ' mean abs=', round(mmx.abs().mean(), 2), ' sd=', round(mmx.std(), 2), ' max=', mmx.max(),
      ' (', mmx.idxmax().strftime('%Y-%m'), ')', ' min=', mmx.min(), '(', mmx.idxmin().strftime('%Y-%m'), ')')
print(' Largest 5 increases:', [(d.strftime('%Y-%m'), round(v, 1)) for d, v in mmx.sort_values(ascending=False).head(5).items()])
print(' Feb->Mar changes by year:', [(d.year, round(v, 1)) for d, v in mm.items() if d.month == 3])
print(' Mar->Apr changes by year:', [(d.year, round(v, 1)) for d, v in mm.items() if d.month == 4])
