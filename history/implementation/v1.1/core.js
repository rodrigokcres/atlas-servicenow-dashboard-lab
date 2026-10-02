(function(root){
'use strict';
const CUTOFF='2026-10-01 18:00:00', STATES=['Nuevo','En progreso','En espera','Resuelto','Cerrado'];
function clock(value){
 if(typeof value!=='string')return null;
 const m=/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})$/.exec(value);if(!m)return null;
 const n=m.slice(1).map(Number), t=Date.UTC(n[0],n[1]-1,n[2],n[3],n[4],n[5]),d=new Date(t);
 return d.getUTCFullYear()===n[0]&&d.getUTCMonth()===n[1]-1&&d.getUTCDate()===n[2]&&d.getUTCHours()===n[3]&&d.getUTCMinutes()===n[4]&&d.getUTCSeconds()===n[5]?t:null;
}
const cutoff=clock(CUTOFF);
function normalize(records){
 const rows=records.map((r,i)=>{const x={};for(const [k,v]of Object.entries(r.raw||r))x[k]=typeof v==='string'?(v.trim()||null):v;
 x.source_row=r.source_row??i+2;x.ticket_type=x.ticket_type?.toUpperCase()||null;x.state=STATES.find(s=>s.toLowerCase()===x.state?.toLowerCase())||x.state;x.group_label=x.assignment_group||'Sin grupo';return x;});
 const chosen=new Map();for(const r of rows){const key=r.number||`row:${r.source_row}`,old=chosen.get(key);const rank=x=>{const t=clock(x.updated_at);return t!==null&&t<=cutoff?t:-Infinity;};if(!old||rank(r)>rank(old)||(rank(r)===rank(old)&&r.source_row<old.source_row))chosen.set(key,r);}
 return [...chosen.values()].sort((a,b)=>a.source_row-b.source_row);
}
function filterTickets(tickets,filters={}){
 const type=filters.ticket_type;
 return tickets.filter(r=>(!type||r.ticket_type===type)&&(!filters.group_label||r.group_label===filters.group_label));
}
function evaluate(r){
 const opened=clock(r.opened_at),updated=clock(r.updated_at),age_reasons=[],stale_reasons=[];
 if(opened===null)age_reasons.push(r.opened_at?'Apertura inválida':'Falta apertura');else if(opened>cutoff)age_reasons.push('Apertura posterior al corte');
 stale_reasons.push(...age_reasons);
 if(updated===null)stale_reasons.push(r.updated_at?'Actualización inválida':'Falta actualización');else if(updated>cutoff)stale_reasons.push('Actualización posterior al corte');
 if(opened!==null&&updated!==null&&updated<opened)stale_reasons.push('Actualización anterior a apertura');
 return {...r,backlog:STATES.slice(0,3).includes(r.state),age_reasons,stale_reasons,age_days:age_reasons.length?null:(cutoff-opened)/86400000,stale_48h:stale_reasons.length?null:cutoff-updated>172800000};
}
function metrics(tickets,filters={}){
 const filtered=filterTickets(tickets,filters),rows=filtered.map(evaluate).filter(r=>r.backlog),ages=rows.map(r=>r.age_days).filter(x=>x!==null).sort((a,b)=>a-b),stale=rows.filter(r=>r.stale_48h!==null),n=ages.length,by_group={};
 for(const r of rows)by_group[r.group_label]=(by_group[r.group_label]||0)+1;
 return {ticket_count:filtered.length,backlog:rows.length,stale_48h:stale.filter(r=>r.stale_48h).length,stale_evaluable:stale.length,stale_not_evaluable:rows.length-stale.length,unassigned:rows.filter(r=>!r.assigned_to).length,no_group:rows.filter(r=>!r.assignment_group).length,age_evaluable:n,age_not_evaluable:rows.length-n,age_mean_days:n?ages.reduce((a,b)=>a+b,0)/n:null,age_median_days:n?(ages[Math.floor((n-1)/2)]+ages[Math.floor(n/2)])/2:null,age_max_days:n?ages[n-1]:null,by_group,backlog_source_rows:rows.map(r=>r.source_row),rows};
}
const API={CUTOFF,clock,normalize,filterTickets,evaluate,metrics};if(typeof module!=='undefined'&&module.exports)module.exports=API;root.DashboardCore=API;
})(typeof globalThis!=='undefined'?globalThis:this);
