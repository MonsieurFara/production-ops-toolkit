#!/usr/bin/env python3
import argparse,html,json
from pathlib import Path

def render(d):
    t=d['traffic'];i=d['incidents'];w=d['workflows']
    def number(value,suffix=''):
        return 'Non mesuré' if value is None else f'{value:.2f}{suffix}'
    cards=[('Requêtes analysées',str(t['requests'])),('Erreurs serveur',number(t['server_error_pct'],' %')),
      ('Apdex · T='+str(t['apdex_threshold_ms'])+' ms',number(t['apdex'])),('Latence p95',number(t['latency_p95_ms'],' ms')),
      ('MTTD',number(i['mttd_minutes'],' min')),('MTTR · incidents clôturés',number(i['mttr_minutes'],' min'))]
    cards_html=''.join('<article><span>'+html.escape(k)+'</span><strong>'+html.escape(v)+'</strong></article>' for k,v in cards)
    process_rows=''.join('<tr><td>'+html.escape(k)+'</td>'+''.join('<td>'+str(v[s])+'</td>' for s in ['active','completed','anomaly'])+'</tr>' for k,v in sorted(w['by_process'].items()))
    bars=''
    for label,key,color in [('En cours','active','#5a90f5'),('Terminés','completed','#42d4b1'),('Anomalies','anomaly','#f0ad58')]:
        pct=100*w[key]/w['total'] if w['total'] else 0
        bars+=f'<div class="bar-row"><span>{label}</span><div class="track"><div style="width:{pct:.3f}%;background:{color}"></div></div><b>{w[key]}</b></div>'
    page = '''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Production — démonstration de KPI</title><style>
*{box-sizing:border-box}body{margin:0;background:#0c1524;color:#ecf3fb;font-family:system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:40px 24px}header{display:flex;justify-content:space-between;align-items:start;gap:20px}h1{font-size:32px;margin:12px 0}p{color:#a0b3ca;line-height:1.6}.tag{border:1px solid #2c665d;border-radius:20px;padding:6px 14px;color:#5de2c1;font-size:12px;white-space:nowrap}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:28px 0}article,.panel{background:#142238;border:1px solid #233750;border-radius:14px;padding:23px}article span{color:#93abc7;font-size:13px}strong{display:block;font-size:30px;margin-top:12px}.panels{display:grid;grid-template-columns:1fr 1.2fr;gap:18px}h2{font-size:18px;margin:0 0 22px}.bar-row{display:grid;grid-template-columns:90px 1fr 35px;gap:10px;align-items:center;margin:22px 0;font-size:13px}.track{background:#21364e;height:12px;border-radius:8px;overflow:hidden}.track div{height:100%}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:12px 8px;border-bottom:1px solid #2b3c52}th{color:#a6bfdc}.note{font-size:13px;margin-top:22px}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}.panels{grid-template-columns:1fr}header{display:block}.tag{display:inline-block}}@media(max-width:480px){.grid{grid-template-columns:1fr}main{padding:25px 16px}}
</style><main><header><div><p>ROBERT DE LELLI BEIDI · OBSERVABILITÉ</p><h1>Indicateurs de production</h1><p>Un aperçu reproductible des services, incidents et workflows.</p></div><span class="tag">DONNÉES SYNTHÉTIQUES</span></header><section class="grid">'''+cards_html+'''</section><section class="panels"><div class="panel"><h2>État des workflows</h2>'''+bars+'''<p class="note">Clôture de la cohorte : '''+number(w['closure_pct'],' %')+'''</p></div><div class="panel"><h2>Répartition par processus</h2><table><thead><tr><th>Processus</th><th>En cours</th><th>Terminés</th><th>Anomalies</th></tr></thead><tbody>'''+process_rows+'''</tbody></table></div></section><p class="note">Le MTTR porte sur les incidents clôturés, de la détection au rétablissement. Ces mesures de démonstration ne représentent aucun système réel. Les périodes et les volumes doivent être précisés pour toute comparaison.</p></main></html>'''
    if d.get('dataset') != 'synthetic-demo':
        page=page.replace('DONNÉES SYNTHÉTIQUES','CSV FOURNIS').replace('Ces mesures de démonstration ne représentent aucun système réel.','Ces mesures proviennent des fichiers CSV fournis.')
    return page

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(render(json.loads(a.input.read_text())),encoding='utf-8');print(f'Rapport écrit : {a.output}')
if __name__=='__main__':main()
