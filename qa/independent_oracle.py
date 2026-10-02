import json,datetime,statistics,collections,itertools,hashlib
from pathlib import Path
import openpyxl
root=Path(__file__).resolve().parents[1]
source_path=root/'history/source/nexus_servicenow_test_v1.xlsx'
wb=openpyxl.load_workbook(source_path,data_only=False,read_only=True)
s=wb['Tickets_ServiceNow']; it=s.iter_rows(values_only=True); header=next(it)
cut=datetime.datetime(2026,10,1,18)
rows=[]
for ix, vals in enumerate(it,2):
 r=dict(zip(header,vals));r={k:(v.strip() or None) if isinstance(v,str) else v for k,v in r.items()};r['source_row']=ix
 r['ticket_type']=(r['ticket_type'] or '').upper();r['state']=next((s for s in ['Nuevo','En progreso','En espera','Resuelto','Cerrado'] if s.casefold()==(r['state'] or '').casefold()),r['state']);r['group_label']=r['assignment_group'] or 'Sin grupo';rows.append(r)
buckets=collections.defaultdict(list)
for r in rows:buckets[r['number'] or ('row',r['source_row'])].append(r)
canonical=sorted([max(v,key=lambda r:(r['updated_at'] if isinstance(r['updated_at'],datetime.datetime) and r['updated_at']<=cut else datetime.datetime.min,-r['source_row'])) for v in buckets.values()],key=lambda r:r['source_row'])
for r in canonical:
 o,u=r['opened_at'],r['updated_at'];ar=[];sr=[]
 if o is None:ar=['Falta apertura']
 elif not isinstance(o,datetime.datetime):ar=['Apertura inválida']
 elif o>cut:ar=['Apertura posterior al corte']
 sr=ar.copy()
 if u is None:sr+=['Falta actualización']
 elif not isinstance(u,datetime.datetime):sr+=['Actualización inválida']
 elif u>cut:sr+=['Actualización posterior al corte']
 if isinstance(o,datetime.datetime) and isinstance(u,datetime.datetime) and u<o:sr+=['Actualización anterior a apertura']
 r['age_reasons']=ar;r['stale_reasons']=sr;r['age_days']=None if ar else (cut-o).total_seconds()/86400;r['stale_48h']=None if sr else (cut-u).total_seconds()>48*3600
cases=[]
for t,g,p in itertools.product(['']+sorted(set(r['ticket_type'] for r in canonical)),['']+sorted(set(r['group_label'] for r in canonical)),['','P1','P2','P3','P4']):
 f=[r for r in canonical if (not t or r['ticket_type']==t) and (not g or r['group_label']==g) and (not p or r['priority']==p)];b=[r for r in f if r['state'] in ['Nuevo','En progreso','En espera']];a=[r['age_days'] for r in b if r['age_days'] is not None]
 m=dict(ticket_count=len(f),backlog=len(b),stale_48h=sum(r['stale_48h'] is True for r in b),stale_evaluable=sum(r['stale_48h'] is not None for r in b),stale_not_evaluable=sum(r['stale_48h'] is None for r in b),unassigned=sum(r['assigned_to'] is None for r in b),no_group=sum(r['assignment_group'] is None for r in b),age_evaluable=len(a),age_not_evaluable=len(b)-len(a),age_mean_days=statistics.mean(a) if a else None,age_median_days=statistics.median(a) if a else None,age_max_days=max(a) if a else None,by_group=dict(collections.Counter(r['group_label'] for r in b)),by_state={s:sum(r['state']==s for r in b) for s in ['Nuevo','En progreso','En espera']},backlog_source_rows=[r['source_row'] for r in b],rows=[{**{k:r[k] for k in ['number','source_row','ticket_type','state','group_label','priority','opened_at','updated_at','age_days','stale_48h','age_reasons','stale_reasons']},'assigned':bool(r['assigned_to'])} for r in b])
 cases.append(dict(filters=dict(ticket_type=t,group_label=g,priority=p),expected=m))
def default(x):return x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x,datetime.datetime) else str(x)
output=dict(source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),source_rows=len(rows),canonical_rows=len(canonical),selected_duplicates={k:[r['source_row'] for r in canonical if r['number']==k] for k,v in buckets.items() if len(v)>1},cases=cases)
(root/'qa/independent_expected_v1.2.json').write_text(json.dumps(output,ensure_ascii=False,indent=2,default=default)+'\n')
print(json.dumps(dict(cases=len(cases),source_rows=len(rows),canonical=len(canonical),baseline={k:v for k,v in cases[0]['expected'].items() if k!='rows'})))
