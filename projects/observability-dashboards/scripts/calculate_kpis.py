#!/usr/bin/env python3
import argparse,csv,json,math
from pathlib import Path
from datetime import datetime
from statistics import mean

def rows(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def traffic_kpis(data,threshold=500):
    if not math.isfinite(threshold) or threshold<=0:raise ValueError('Seuil Apdex positif et fini requis')
    total=len(data);satisfied=0;tolerated=0;errors=0;latencies=[]
    for r in data:
        latency=float(r['latency_ms']);status=int(r['status_code'])
        if not math.isfinite(latency) or latency<0 or not 100<=status<=599:raise ValueError('Mesure de trafic invalide')
        latencies.append(latency);errors+=status>=500
        if status>=400:continue
        if latency<=threshold:satisfied+=1
        elif latency<=4*threshold:tolerated+=1
    ordered=sorted(latencies)
    def percentile(q):
        if not ordered:return None
        position=(len(ordered)-1)*q;low=int(position);fraction=position-low
        return ordered[low]*(1-fraction)+ordered[min(low+1,len(ordered)-1)]*fraction
    return {'requests':total,'server_errors':errors,'server_error_pct':100*errors/total if total else None,
      'apdex_threshold_ms':threshold,'apdex':(satisfied+0.5*tolerated)/total if total else None,
      'latency_p50_ms':percentile(.5),'latency_p95_ms':percentile(.95)}

def incident_kpis(data):
    detection=[];restoration=[];open_incidents=0
    for r in data:
        start=datetime.fromisoformat(r['opened_at']);detected=datetime.fromisoformat(r['detected_at'])
        if start.tzinfo is None or detected.tzinfo is None:raise ValueError('Timezone requise pour les incidents')
        delay=(detected-start).total_seconds()/60
        if delay<0:raise ValueError('Détection antérieure au début')
        detection.append(delay)
        if r.get('closed_at'):
            closed=datetime.fromisoformat(r['closed_at'])
            if closed.tzinfo is None:raise ValueError('Timezone requise')
            elapsed=(closed-detected).total_seconds()/60
            if elapsed<0:raise ValueError('Clôture antérieure à la détection')
            restoration.append(elapsed)
        else:open_incidents+=1
    return {'incidents':len(data),'open_incidents':open_incidents,'closed_incidents':len(restoration),
      'mttd_minutes':mean(detection) if detection else None,'mttr_minutes':mean(restoration) if restoration else None}

def workflow_kpis(data):
    seen=set();counts={'active':0,'completed':0,'anomaly':0};processes={}
    for r in data:
        if not r['id'] or r['id'] in seen:raise ValueError('Identifiant de workflow vide ou dupliqué')
        seen.add(r['id']);status=r['status']
        if status not in counts:raise ValueError('Statut de workflow inconnu')
        counts[status]+=1
        processes.setdefault(r['process'],dict.fromkeys(counts,0))[status]+=1
    return {'total':len(data),**counts,'closure_pct':100*counts['completed']/len(data) if data else None,'by_process':processes}

def main():
    p=argparse.ArgumentParser();p.add_argument('--traffic',required=True);p.add_argument('--incidents',required=True)
    p.add_argument('--workflows',required=True);p.add_argument('--threshold-ms',type=float,default=500);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dataset-label',default='provided-csv');a=p.parse_args()
    result={'dataset':a.dataset_label,'traffic':traffic_kpis(rows(a.traffic),a.threshold_ms),
      'incidents':incident_kpis(rows(a.incidents)),'workflows':workflow_kpis(rows(a.workflows))}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'KPI écrits : {a.output}')

if __name__=='__main__':main()
