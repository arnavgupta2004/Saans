"""Deterministic school timetable planning."""
from __future__ import annotations
from datetime import datetime, date as Date
from typing import Any
from .aqi import naqi
from .models import DayPlan, HourPoint, Period, PeriodPlan, School, Sources, Swap
from .rules import action_for

_RANK={"Good":0,"Satisfactory":1,"Moderate":2,"Poor":3,"Very Poor":4,"Severe":5}
def _hour(value:str)->int: return int(value[11:13] if "T" in value else value[:2])
def _in_period(point:dict[str,Any], period:Period)->bool:
 h=_hour(point["time"]); start=_hour(period.start); end=_hour(period.end)
 return start <= h <= end if period.end.endswith(":00") else start <= h <= end
def _points(hourly:list[dict[str,Any]], period:Period)->list[dict[str,Any]]:
 return [p for p in hourly if _in_period(p,period)]
def _point(row:dict[str,Any])->HourPoint:
 aqi,band,_=naqi(row.get("pm25_cal",row["pm25"]),row.get("pm10_cal",row["pm10"]))
 return HourPoint(time=row["time"],pm25=row["pm25"],pm10=row["pm10"],pm25_cal=row.get("pm25_cal",row["pm25"]),pm10_cal=row.get("pm10_cal",row["pm10"]),aqi=aqi or 0,band=band or "Good",calibrated=bool(row.get("calibrated",False)))
def _period_aqi(hourly:list[dict[str,Any]], period:Period)->tuple[int,str]:
 points=_points(hourly,period)
 if not points: return 0,"Good"
 hp=max((_point(p) for p in points),key=lambda x:x.aqi); return hp.aqi,hp.band
def plan_day(school:School,hourly_cal:list[dict[str,Any]], date:str|Date, sources:dict[str,Any]|None=None, mode:str|None=None)->DayPlan:
 day=str(date); rows=[p for p in hourly_cal if p["time"].startswith(day)]
 hours=[_point(p) for p in rows]; worst=max(hours,key=lambda x:x.aqi); best=min(hours,key=lambda x:x.aqi)
 candidates=[p for p in school.timetable if p.swappable and 8<=_hour(p.start)<15]
 plans=[]
 for period in school.timetable:
  aqi,band=_period_aqi(rows,period); swap=None
  if period.outdoor and period.intensity=="high":
   choices=[]
   for target in candidates:
    if target.id==period.id: continue
    target_aqi,target_band=_period_aqi(rows,target); gain=_RANK[band]-_RANK[target_band]
    if gain>=2: choices.append((target_aqi,target,target_band,gain))
   if choices:
    target_aqi,target,target_band,gain=min(choices,key=lambda x:x[0])
    swap=Swap(to_start=target.start,to_end=target.end,to_aqi=target_aqi,to_band=target_band,gain_bands=gain)
  plans.append(PeriodPlan(period=period,aqi=aqi,band=band,action=action_for(period.type,period.intensity,band),sensitive_action=action_for(period.type,period.intensity,band,True),swap=swap))
 source=sources or {}; actual_mode=mode or ("fixture" if any(p.get("source")=="fixture" for p in rows) else "live")
 return DayPlan(school_id=school.id,date=day,now=hours[0] if hours else None,periods=plans,worst_hour=worst.time,best_hour=best.time,sources=Sources(forecast=source.get("forecast","open-meteo"),observation=source.get("observation","none"),station=source.get("station"),distance_km=source.get("distance_km")),mode=actual_mode,generated_at=datetime.now().isoformat())
def plan_week(school:School,hourly_cal:list[dict[str,Any]], sources:dict[str,Any]|None=None, mode:str|None=None)->dict[str,Any]:
 dates=sorted({p["time"][:10] for p in hourly_cal})[:5]; plans=[plan_day(school,hourly_cal,d,sources,mode) for d in dates]
 return {"days":[{"date":p.date,"worst_aqi":max(x.aqi for x in p.periods),"worst_band":max(p.periods,key=lambda x:x.aqi).band,"best_hour":p.best_hour,"worst_hour":p.worst_hour} for p in plans],"hourly":[_point(p) for p in hourly_cal]}
def best_day(school:School,hourly_cal:list[dict[str,Any]], window_start:str, window_end:str, days:int=5)->dict[str,Any]:
 ranking=[]
 for day in sorted({p["time"][:10] for p in hourly_cal})[:days]:
  values=[_point(p).aqi for p in hourly_cal if p["time"].startswith(day) and _hour(window_start)<=_hour(p["time"])<=_hour(window_end)]
  if values: ranking.append({"date":day,"max_aqi":max(values),"mean_aqi":round(sum(values)/len(values),1),"band":naqi(max(p.get("pm25_cal",p["pm25"]) for p in hourly_cal if p["time"].startswith(day)),0)[1]})
 ranking.sort(key=lambda x:(x["max_aqi"],x["mean_aqi"]))
 return {"ranking":ranking,"reason":f"{ranking[0]['date']} has the lowest maximum AQI ({ranking[0]['max_aqi']}) in the selected window." if ranking else "No forecast data in the selected window."}
