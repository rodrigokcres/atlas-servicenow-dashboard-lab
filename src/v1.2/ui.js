(function(){
'use strict';
const api=DashboardCore,data=JSON.parse(document.getElementById('source-data').textContent),tickets=api.normalize(data.records),$=id=>document.getElementById(id),esc=x=>String(x??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),fmt=x=>x===null?'—':new Intl.NumberFormat('es-ES',{maximumFractionDigits:2}).format(x);
for(const [id,values]of [['type',[...new Set(tickets.map(r=>r.ticket_type||'Sin tipo'))].sort()],['group',[...new Set(tickets.map(r=>r.group_label))].sort()]])$(id).innerHTML+=values.map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
function bars(entries){const max=Math.max(1,...entries.map(x=>x[1]));return entries.length?entries.map(([label,count])=>`<div class="barrow"><span>${esc(label)}</span><div class="track" aria-hidden="true"><div class="bar" style="width:${100*count/max}%"></div></div><strong>${count}</strong></div>`).join(''):'<p class="empty">Sin tickets en esta selección</p>';}
function render(){const filters={ticket_type:$('type').value||null,group_label:$('group').value||null,priority:$('priority').value||null},m=api.metrics(tickets,filters);
 $('scope').textContent=`${m.ticket_count} de ${tickets.length} tickets canónicos · ${data.records.length} filas fuente`;
 const cards=[['Backlog',m.backlog,'Nuevo · En progreso · En espera','Calculable'],['Sin actualización >48h',m.stale_48h,`${m.stale_evaluable} evaluables · ${m.stale_not_evaluable} no evaluables`,'Parcialmente calculable'],['Sin responsable',m.unassigned,`${m.no_group} sin grupo · indicador separado`,'Calculable'],['Antigüedad media',fmt(m.age_mean_days),`Días · ${m.age_evaluable} evaluables · ${m.age_not_evaluable} no evaluables`,'Parcialmente calculable']];
 $('cards').innerHTML=cards.map(([title,value,sub,status])=>`<article class="card"><h2>${title}</h2><div class="value">${value}</div><p>${sub}</p><span class="badge">${status}</span></article>`).join('');
 $('groups').innerHTML=bars(Object.entries(m.by_group).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])));
 $('states').innerHTML=bars(['Nuevo','En progreso','En espera'].map(s=>[s,m.rows.filter(r=>r.state===s).length]));
 $('ages').innerHTML=[['Mediana (días)',fmt(m.age_median_days)],['Máximo (días)',fmt(m.age_max_days)]].map(([k,v])=>`<div class="statline"><span>${k}</span><strong>${v}</strong></div>`).join('');
 $('detailScope').textContent=`${m.backlog} tickets · ${filters.ticket_type||'Todos los tipos'} / ${filters.group_label||'Todos los grupos'} / ${filters.priority||'Todas las prioridades'}`;
 $('tickets').innerHTML=m.rows.length?m.rows.map(r=>`<tr data-row="${r.source_row}"><td class="number">${esc(r.number)} <small>· ${r.source_row}</small></td><td>${esc(r.ticket_type)}</td><td>${esc(r.state)}</td><td>${esc(r.group_label)}</td><td>${r.assigned_to?'Asignado':'Sin responsable'}</td><td>${esc(r.opened_at)}</td><td>${esc(r.updated_at)}</td><td>${r.age_days===null?'<span class="warn">No evaluable</span>':fmt(r.age_days)}</td><td>${r.stale_48h===null?`<span class="warn">${esc(r.stale_reasons.join('; '))}</span>`:r.stale_48h?'<span class="warn">Sin actualización >48h</span>':'<span class="good">48h o menos</span>'}</td></tr>`).join(''):'<tr><td colspan="9" class="empty">No hay tickets en backlog para esta selección.</td></tr>';
 const anomalies=m.rows.filter(r=>r.stale_reasons.length||r.age_reasons.length);
 $('anomalies').innerHTML=anomalies.length?`<div class="tablewrap"><table><thead><tr><th>Ticket / fila</th><th>Seguimiento</th><th>Antigüedad</th></tr></thead><tbody>${anomalies.map(r=>`<tr><td>${esc(r.number)} · ${r.source_row}</td><td>${esc(r.stale_reasons.join('; ')||'Evaluable')}</td><td>${esc(r.age_reasons.join('; ')||'Evaluable')}</td></tr>`).join('')}</tbody></table></div>`:'<p class="empty">No hay registros no evaluables en el backlog seleccionado.</p>';
 return m;
}
$('type').addEventListener('change',render);$('group').addEventListener('change',render);$('priority').addEventListener('change',render);$('reset').addEventListener('click',()=>{$('type').value='';$('group').value='';$('priority').value='';render();});
globalThis.DashboardApp={render,tickets};render();
})();
