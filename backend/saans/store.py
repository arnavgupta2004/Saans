from __future__ import annotations
import json, os
from decimal import Decimal
from pathlib import Path
from typing import Protocol
import boto3
from .models import School, Period
class SchoolStore(Protocol):
 def list(self)->list[School]: ...
 def get(self, school_id:str)->School|None: ...
 def save(self, school:School)->School: ...
def _periods(grades:tuple[str,str])->list[Period]:
 g1,g2=grades
 rows=[('assembly','Assembly','08:00','08:20','low',True,False,None),('pe',f'Class {g1} PE','08:40','09:20','high',True,True,g1),('class','Period 2','09:20','10:00','low',False,True,None),('class','Period 3','10:00','10:40','low',False,True,None),('recess','Recess','10:40','11:00','low',True,False,None),('class','Period 4','11:00','11:40','low',False,True,None),('class','Period 5','11:40','12:20','low',False,True,None),('class','Period 6','12:20','13:00','low',False,True,None),('pe',f'Class {g2} PE','13:00','13:40','high',True,True,g2),('class','Period 8','13:40','14:20','low',False,True,None)]
 return [Period(id=f'p{i}',label=n,start=s,end=e,type=t,intensity=x,outdoor=o,swappable=w,grade=g) for i,(t,n,s,e,x,o,w,g) in enumerate(rows)]
SEED_SCHOOLS=[School(id='delhi-anand-vihar',name='Saans Delhi Anand Vihar School',city='Delhi',lat=28.647,lon=77.316,timetable=_periods(('7B','8A')),sensitive_count=38),School(id='delhi-dwarka',name='Saans Delhi Dwarka School',city='Delhi',lat=28.582,lon=77.050,timetable=_periods(('6A','9B')),sensitive_count=19),School(id='bengaluru-indiranagar',name='Saans Bengaluru Indiranagar School',city='Bengaluru',lat=12.971,lon=77.641,timetable=_periods(('5A','7C')),sensitive_count=12)]
class JsonStore:
 def __init__(self,path:str|Path='data/schools.json'):
  self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
  if not self.path.exists(): self.path.write_text(json.dumps([x.model_dump() for x in SEED_SCHOOLS]))
 def list(self): return [School.model_validate(x) for x in json.loads(self.path.read_text())]
 def get(self,school_id): return next((x for x in self.list() if x.id==school_id),None)
 def save(self,school):
  rows=[x for x in self.list() if x.id!=school.id]+[school]; self.path.write_text(json.dumps([x.model_dump() for x in rows])); return school
class DynamoStore:
 def __init__(self,table_name:str='saans-schools',resource=None): self.table=(resource or boto3.resource('dynamodb')).Table(table_name)
 def list(self): return [School.model_validate(x) for x in self.table.scan().get('Items',[])]
 def get(self,school_id):
  item=self.table.get_item(Key={'id':school_id}).get('Item'); return School.model_validate(item) if item else None
 def save(self,school): self.table.put_item(Item=json.loads(school.model_dump_json(),parse_float=Decimal)); return school
def get_store(): return DynamoStore() if os.getenv('STORE','json')=='dynamo' else JsonStore(os.getenv('SCHOOLS_PATH') or Path(__file__).resolve().parents[1]/'data'/'schools.json')


class PlanCache(Protocol):
 def get(self, key:str)->dict|None: ...
 def put(self, key:str, item:dict)->None: ...
class JsonPlanCache:
 """Local-dev plan cache (same interface as DynamoPlanCache)."""
 def __init__(self,path:str|Path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
 def _all(self)->dict: return json.loads(self.path.read_text()) if self.path.exists() else {}
 def get(self,key): return self._all().get(key)
 def put(self,key,item):
  rows=self._all(); rows[key]=item; self.path.write_text(json.dumps(rows))
class DynamoPlanCache:
 """saans-cache table: {key: "<school_id>#<date>", body: JSON string, stored_at: epoch seconds}."""
 def __init__(self,table_name:str|None=None,resource=None): self.table=(resource or boto3.resource('dynamodb')).Table(table_name or os.getenv('CACHE_TABLE','saans-cache'))
 def get(self,key):
  item=self.table.get_item(Key={'key':key}).get('Item')
  return {**json.loads(item['body']),'stored_at':float(item['stored_at'])} if item else None
 def put(self,key,item):
  body={k:v for k,v in item.items() if k!='stored_at'}
  self.table.put_item(Item={'key':key,'body':json.dumps(body),'stored_at':int(item['stored_at'])})
def get_plan_cache()->PlanCache:
 if os.getenv('STORE','json')=='dynamo': return DynamoPlanCache()
 return JsonPlanCache(os.getenv('PLAN_CACHE_PATH',str(Path(__file__).resolve().parents[1]/'data'/'plan_cache.json')))
