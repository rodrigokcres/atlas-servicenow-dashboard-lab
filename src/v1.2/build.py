from pathlib import Path
import json
base=Path(__file__).resolve().parent
root=base.parents[1]
data=json.loads((root/'history/data/normalized_tickets.json').read_text())
# Embed source fields; all business calculations run through core.js.
payload={'records':[{'source_row':r['source_row'],'raw':r['raw']} for r in data['records']]}
html=(base/'template.html').read_text().replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')).replace('__CORE__',(base/'core.js').read_text()).replace('__UI__',(base/'ui.js').read_text())
(base/'dashboard.html').write_text(html)
print('Built',base/'dashboard.html')
