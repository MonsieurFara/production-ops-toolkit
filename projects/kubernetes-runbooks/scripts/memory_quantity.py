#!/usr/bin/env python3
"""Conversion des quantités mémoire usuelles ; le suffixe m signifie milli-octet."""
import re
from decimal import Decimal
UNITS={'':1,'m':Decimal('0.001'),'k':1000,'K':1000,'M':1000**2,'G':1000**3,'T':1000**4,'P':1000**5,'E':1000**6,
       'Ki':1024,'Mi':1024**2,'Gi':1024**3,'Ti':1024**4,'Pi':1024**5,'Ei':1024**6}
def memory_bytes(value):
    m=re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)([A-Za-z]*)',value)
    if not m or m.group(2) not in UNITS: raise ValueError('Quantité mémoire non prise en charge')
    return Decimal(m.group(1))*UNITS[m.group(2)]
