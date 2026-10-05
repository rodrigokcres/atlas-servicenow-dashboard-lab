import json, hashlib, statistics
from pathlib import Path
from datetime import datetime
from collections import Counter
import openpyxl
P=Path('deliverables'); Q=P/'qa'; cutoff=datetime(2026,10,1,18)
w=openpyxl.load_workbook(P/'source/nexus_servicenow_test_v1.xlsx',read_only=True,data_only=False)
s=w['Tickets_ServiceNow']; values=list(s.values); headers=values[0]; rows=[]
for i,vals in enumerate(values[1:],2):
 r=dict(zip(headers,vals)); r={k:(v.strip() or None) if isinstance(v,str) else v for k,v in r.items()};r['source_row']=i
 r['ticket_type']=(r['ticket_type'] or '').upper() or None
 r['state']={x.casefold():x for x in ['Nuevo','En progreso','En espera','Resuelto','Cerrado']}.get((r['state'] or '').casefold(),r['state'])
 r['group_label']=r['assignment_group'] or 'Sin grupo'; rows.append(r)
chosen={}
for r in rows:
 key=r['number'] or ('row',r['source_row']); old=chosen.get(key)
 def rank(x):
  d=x['updated_at'];return (d if isinstance(d,datetime) and d<=cutoff else datetime.min,-x['source_row'])
 if old is None or rank(r)>rank(old): chosen[key]=r
canonical=sorted(chosen.values(),key=lambda r:r['source_row'])
def evaluate(r):
 a,u=r['opened_at'],r['updated_at']; age=isinstance(a,datetime) and a<=cutoff; stale=age and isinstance(u,datetime) and u<=cutoff and u>=a
 return dict(source_row=r['source_row'],number=r['number'],ticket_type=r['ticket_type'],state=r['state'],group_label=r['group_label'],age_days=(cutoff-a).total_seconds()/86400 if age else None,stale_48h=(cutoff-u).total_seconds()>172800 if stale else None)
def calc(t,g):
 pop=[r for r in canonical if (not t or r['ticket_type']==t) and (not g or r['group_label']==g)];back=[r for r in pop if r['state'] in ['Nuevo','En progreso','En espera']];ev=[evaluate(r) for r in back];ages=[r['age_days'] for r in ev if r['age_days'] is not None];stale=[r['stale_48h'] for r in ev if r['stale_48h'] is not None]
 return dict(ticket_count=len(pop),backlog=len(back),stale_48h=sum(stale),stale_evaluable=len(stale),stale_not_evaluable=len(back)-len(stale),unassigned=sum(r['assigned_to'] is None for r in back),no_group=sum(r['assignment_group'] is None for r in back),age_evaluable=len(ages),age_not_evaluable=len(back)-len(ages),age_mean_days=sum(ages)/len(ages) if ages else None,age_median_days=statistics.median(ages) if ages else None,age_max_days=max(ages) if ages else None,by_group=dict(Counter(r['group_label'] for r in back)),by_state=dict(Counter(r['state'] for r in back)),backlog_source_rows=[r['source_row'] for r in back],rows=ev)
types=sorted(set(r['ticket_type'] for r in canonical));groups=sorted(set(r['group_label'] for r in canonical));cases=[dict(filters=dict(ticket_type=t,group_label=g),expected=calc(t,g)) for t in [None]+types for g in [None]+groups]
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
handoff=json.loads((P/'contract_hashes_at_handoff.json').read_text()); hashes={k:dict(expected=v,actual=hashfile(P/'contracts'/k)) for k,v in handoff.items()}
out=dict(source_sha256=hashfile(P/'source/nexus_servicenow_test_v1.xlsx'),sheet='Tickets_ServiceNow',range='A1:K103',physical_rows=len(rows),canonical_rows=len(canonical),cutoff=str(cutoff),timezone='naive Excel clock',contract_hashes=hashes,canonical_selection=[dict(number=r['number'],source_row=r['source_row']) for r in canonical],types=types,groups=groups,cases=cases)
(Q/'independent_expected.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(dict(source_rows=len(rows),canonical=len(canonical),cases=len(cases),baseline={k:v for k,v in cases[0]['expected'].items() if k not in ['rows','backlog_source_rows']},contract_hashes=hashes),ensure_ascii=False))
