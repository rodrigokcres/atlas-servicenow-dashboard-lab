import json,hashlib,re,datetime
from pathlib import Path
import openpyxl
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads((root/p).read_text())
def sha(p):return hashlib.sha256((root/p).read_bytes()).hexdigest()
checks=[]
def check(id,a,e):checks.append(dict(id=id,result='passed' if a==e else 'failed',actual=a,expected=e))
for p,h in read('changes/historical-sha256.json').items():check('historical:'+p,sha(p),h)
dev=read('reports/DEV_REPORT_v1.2.json')
for ref in dev['based_on']+dev['technical_summary']['input_contracts']+dev['files_created_or_modified']:check('handoff:'+ref['path'],sha(ref['path']),ref['sha256'])
for ref in read('specs/DATA_SPEC_v1.1.json')['based_on']:
 if 'sha256' in ref:check('nexus:'+ref['path'],sha(ref['path']),ref['sha256'])
for p,owner in [('specs/PROJECT_SPEC_v1.1.json','ATLAS'),('specs/DATA_SPEC_v1.1.json','NEXUS'),('reports/DEV_REPORT_v1.2.json','FORGE')]:
 j=read(p);check('owner:'+p,j['created_by'],owner);check('identity:'+p,j['project_id'],'servicenow-gestion-tickets')
html=(root/'src/v1.2/dashboard.html').read_text(); embedded=json.loads(re.search(r'<script id="source-data" type="application/json">(.*?)</script>',html,re.S).group(1))
wb=openpyxl.load_workbook(root/'history/source/nexus_servicenow_test_v1.xlsx',read_only=True,data_only=False);it=wb['Tickets_ServiceNow'].iter_rows(values_only=True);cols=next(it);original=[]
for i,values in enumerate(it,2):original.append({'source_row':i,'raw':{k:v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v,datetime.datetime) else v for k,v in zip(cols,values)}})
check('source-raw-102-rows',embedded['records'],original)
# Avoid unnecessary personal values in evidence: record equality and cryptographic digest only.
checks[-1]['actual']={'rows':len(embedded['records']),'digest':hashlib.sha256(json.dumps(embedded['records'],sort_keys=True).encode()).hexdigest()};checks[-1]['expected']={'rows':len(original),'digest':hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()}
old=read('history/contracts/DATA_SPEC_v1.0.json');new=read('specs/DATA_SPEC_v1.1.json');check('unchanged-kpis',new['kpi_definitions'],old['kpi_definitions']);check('unchanged-T1-T5',new['transformations_required'][:5],old['transformations_required'][:5])
output=dict(checks=checks,summary=dict(checks=len(checks),failed=sum(c['result']=='failed' for c in checks)),audited_revision='8132a4f12984cf03f7ec2175a5f83a81ae2cc113',audited_hashes={str(p.relative_to(root)):sha(p.relative_to(root)) for base in ['src/v1.2','specs','reports'] for p in (root/base).glob('*') if p.is_file()})
(root/'qa/integrity_v1.2.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');print(output['summary']);print([c['id'] for c in checks if c['result']=='failed'])
