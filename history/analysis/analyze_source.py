"""NEXUS reproducible full-source inspection; never saves or edits workbook."""
import json, hashlib, collections, statistics
from datetime import datetime
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'input/nexus_servicenow_test_v1(3).xlsx'
OUT=ROOT/'deliverables'
CUT=datetime(2026,10,1,18)
def ser(v):
 return v.isoformat(sep=' ') if isinstance(v,datetime) else v
def dump(path,obj):
 path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=ser)+'\n')
w=openpyxl.load_workbook(SRC,read_only=True,data_only=False)
sheets={s.title:list(s.values) for s in w}
rows=sheets['Tickets_ServiceNow'];headers=rows[0]; records=[]
state_map={x.casefold():x for x in ['Nuevo','En progreso','En espera','Resuelto','Cerrado']}
for rownum,values in enumerate(rows[1:],2):
 raw={h:ser(v) for h,v in zip(headers,values)}
 n={k:(v.strip() or None if isinstance(v,str) else v) for k,v in raw.items()}
 n['ticket_type']=n['ticket_type'].upper() if n['ticket_type'] else None
 n['state']=state_map.get((n['state'] or '').casefold(),n['state'])
 rec={'source_sheet':'Tickets_ServiceNow','source_row':rownum,'raw':raw,**n}
 records.append(rec)
def dt(v):
 try:return datetime.fromisoformat(v) if v else None
 except (TypeError,ValueError):return None
byid=collections.defaultdict(list)
for r in records:byid[r['number'] or f"__row_{r['source_row']}"] .append(r)
for group in byid.values():
 def key(r):
  d=dt(r['updated_at']);return (d if d and d<=CUT else datetime.min,-r['source_row'])
 chosen=max(group,key=key)
 for r in group:
  r['canonical_row']=chosen['source_row'];r['included']=r is chosen
for r in records:
 o,u=dt(r['opened_at']),dt(r['updated_at'])
 r['backlog']=r['state'] in ['Nuevo','En progreso','En espera']
 r['unassigned']=r['assigned_to'] is None;r['no_group']=r['assignment_group'] is None
 r['group_label']=r['assignment_group'] or 'Sin grupo'
 reason=[]
 for f,d in [('opened_at',o),('updated_at',u)]:
  if not d:reason.append(f+('_missing' if r[f] is None else '_invalid'))
  elif d>CUT:reason.append(f+'_future')
 if o and u and u<o:reason.append('updated_before_opened')
 r['stale_reasons']=reason;r['stale_evaluable']=not reason
 r['stale_hours']=(CUT-u).total_seconds()/3600 if not reason else None
 r['stale_48h']=r['stale_hours']>48 if not reason else None
 r['age_reasons']=['opened_at_missing' if r['opened_at'] is None else 'opened_at_invalid'] if not o else (['opened_at_future'] if o>CUT else [])
 r['age_hours']=(CUT-o).total_seconds()/3600 if not r['age_reasons'] else None
 r['age_days']=r['age_hours']/24 if r['age_hours'] is not None else None
canonical=[r for r in records if r['included']]
def summary(rs):
 b=[r for r in rs if r['backlog']]; ages=[r['age_days'] for r in b if r['age_days'] is not None]
 return {'ticket_count':len(rs),'backlog':len(b),'stale_48h':sum(r['stale_48h'] is True for r in b),'stale_evaluable':sum(r['stale_evaluable'] for r in b),'stale_not_evaluable':sum(not r['stale_evaluable'] for r in b),'unassigned':sum(r['unassigned'] for r in b),'no_group':sum(r['no_group'] for r in b),'age_evaluable':len(ages),'age_not_evaluable':len(b)-len(ages),'age_mean_days':statistics.mean(ages) if ages else None,'age_median_days':statistics.median(ages) if ages else None,'age_max_days':max(ages) if ages else None,'by_group':dict(sorted(collections.Counter(r['group_label'] for r in b).items())),'backlog_source_rows':[r['source_row'] for r in b]}
types=sorted(set(r['ticket_type'] for r in canonical));groups=sorted(set(r['group_label'] for r in canonical))
expected=[]
for typ in [None]+types:
 for group in [None]+groups:
  subset=[r for r in canonical if (typ is None or r['ticket_type']==typ) and (group is None or r['group_label']==group)]
  expected.append({'filters':{'ticket_type':typ,'group_label':group},**summary(subset)})
profiles=[]
for j,h in enumerate(headers):
 vals=[r[j] if j<len(r) else None for r in rows[1:]]
 profile={'name':h,'source_type_counts':dict(collections.Counter(type(v).__name__ for v in vals)),'null_count':sum(v is None for v in vals),'distinct_non_null':len(set(v for v in vals if v is not None))}
 if h in ['ticket_type','state','priority','assignment_group','category']:
  profile['value_counts']={str(k):v for k,v in collections.Counter(vals).items()}
 if h in ['opened_at','updated_at','sla_due']:
  ds=[v for v in vals if isinstance(v,datetime)];profile.update(min=min(ds),max=max(ds),future_rows=[i+2 for i,v in enumerate(vals) if isinstance(v,datetime) and v>CUT],invalid_non_null_rows=[i+2 for i,v in enumerate(vals) if v is not None and not isinstance(v,datetime)])
 profiles.append(profile)
profile={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'sheets':[{'name':name,'physical_rows':len(vals),'max_columns':max(map(len,vals))} for name,vals in sheets.items()],'readme':[list(r) for r in sheets['README']],'fields':profiles,'source_rows':len(records),'unique_ticket_ids':len(byid),'canonical_tickets':len(canonical),'duplicates':[{'number':k,'source_rows':[r['source_row'] for r in g],'canonical_row':g[0]['canonical_row'],'exact':len({json.dumps(r['raw'],sort_keys=True) for r in g})==1} for k,g in byid.items() if len(g)>1],'normalizations':[{'source_row':r['source_row'],'field':k,'raw':r['raw'][k],'normalized':r[k]} for r in records for k in headers if r['raw'][k]!=r[k]],'date_anomalies':[{'source_row':r['source_row'],'number':r['number'],'included':r['included'],'backlog':r['backlog'],'stale_reasons':r['stale_reasons'],'age_reasons':r['age_reasons']} for r in records if r['stale_reasons'] or r['age_reasons']],'formula_count':sum(isinstance(v,str) and v.startswith('=') for rr in sheets.values() for row in rr for v in row),'expected_global':summary(canonical)}
for folder in ['analysis','data']: (OUT/folder).mkdir(exist_ok=True)
dump(OUT/'analysis/source_profile.json',profile)
dump(OUT/'data/normalized_tickets.json',{'project_id':'ATLAS-SN-QA-20261002','data_spec_version':'1.0','cutoff':'2026-10-01 18:00:00','timezone':'naive, same as Excel; no conversion','source_sha256':profile['source_sha256'],'records':records})
dump(OUT/'analysis/expected_results.json',{'data_spec_version':'1.0','rounding':'Do not round before aggregation; presentation may use 2 decimal places','filter_cases':expected})
print(json.dumps(profile['expected_global'],ensure_ascii=False,indent=2));print('date anomalies',len(profile['date_anomalies']))
