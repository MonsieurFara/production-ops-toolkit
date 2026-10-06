#!/usr/bin/env python3
import argparse,csv,json,math
from pathlib import Path

def convert(rows,dataset_label='provided-csv'):
    features=[];seen=set()
    for r in rows:
        identity=r['id'].strip();lat=float(r['latitude']);lon=float(r['longitude'])
        if not identity or identity in seen:raise ValueError('ID vide ou dupliqué')
        if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('Coordonnées invalides')
        seen.add(identity);features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},
          'properties':{'id':identity,'status':r.get('status','unknown'),'dataset':dataset_label}})
    return {'type':'FeatureCollection','features':features}

def main():
    p=argparse.ArgumentParser(description='Conversion CSV vers GeoJSON ; exemple à coordonnées fictives.')
    p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--dataset-label',default='provided-csv');a=p.parse_args()
    with a.input.open(newline='',encoding='utf-8-sig') as f:result=convert(list(csv.DictReader(f)),a.dataset_label)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
