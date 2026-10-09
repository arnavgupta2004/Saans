"""Deterministic school timetable planning."""
from __future__ import annotations
from datetime import datetime, date as Date
from typing import Any
from .aqi import naqi
from .models import DayPlan, HourPoint, Period, PeriodPlan, School, Sources, Swap
from zoneinfo import ZoneInfo
from .rules import INDOOR_ACTION, action_for
IST=ZoneInfo("Asia/Kolkata")

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
def _today_ist()->datetime: return datetime.now(IST)
def _pick_now(hours:list[HourPoint], now:datetime)->HourPoint|None:
 """The hour point for the current IST hour-of-day (same hour on a replayed date)."""
 return next((h for h in hours if _hour(h.time)==now.hour),None) or (min(hours,key=lambda h:abs(_hour(h.time)-now.hour)) if hours else None)
def _assign_swaps(plans:list[PeriodPlan], targets:list[Period], rows:list[dict[str,Any]])->None:
 """Swap = exchange a swappable outdoor period with an indoor swappable class period (08:00-15:00) the same day.
 Greedy: worst period first takes the lowest-AQI free target that improves its action level; each target used once.
 indoors -> target must give go/caution; caution -> target must give go (optional swap)."""
 slots=[(t,*_period_aqi(rows,t)) for t in targets if _points(rows,t)]
 used:set[str]=set()
 movers=[p for p in plans if p.period.outdoor and p.period.swappable and p.action.level in ("indoors","caution")]
 for pp in sorted(movers,key=lambda p:(-p.aqi,p.action.level!="indoors",p.period.start)):
  accept=("go","caution") if pp.action.level=="indoors" else ("go",)
  free=[(aqi,t.start,t,band) for t,aqi,band in slots if t.id not in used and t.id!=pp.period.id and action_for(pp.period.type,pp.period.intensity,band).level in accept]
  if not free: continue
  aqi,_,t,band=min(free,key=lambda x:(x[0],x[1])); used.add(t.id)
  pp.swap=Swap(to_start=t.start,to_end=t.end,to_aqi=aqi,to_band=band,gain_bands=_RANK[pp.band]-_RANK[band],optional=pp.action.level=="caution",with_period_id=t.id,with_label=t.label)
def plan_day(school:School,hourly_cal:list[dict[str,Any]], date:str|Date, sources:dict[str,Any]|None=None, mode:str|None=None, now:datetime|None=None, replay_date:str|None=None)->DayPlan:
 day=str(date); rows=[p for p in hourly_cal if p["time"].startswith(day)]
 hours=[_point(p) for p in rows]
 window=[h for h in hours if 7<=_hour(h.time)<=16] or hours
 worst=max(window,key=lambda x:x.aqi); best=min(window,key=lambda x:x.aqi)
 targets=[p for p in school.timetable if p.swappable and not p.outdoor and p.type=="class" and 8<=_hour(p.start)<15]
 plans=[]
 for period in school.timetable:
  aqi,band=_period_aqi(rows,period)
  if not period.outdoor:
   plans.append(PeriodPlan(period=period,aqi=aqi,band=band,action=INDOOR_ACTION,sensitive_action=INDOOR_ACTION)); continue
  action=action_for(period.type,period.intensity,band)
  plans.append(PeriodPlan(period=period,aqi=aqi,band=band,action=action,sensitive_action=action_for(period.type,period.intensity,band,True)))
 _assign_swaps(plans,targets,rows)
 source=sources or {}
 forecast=source.get("forecast","open-meteo")
 actual_mode=mode or (forecast if forecast in ("live","cached","fixture","replay") else ("fixture" if any(p.get("source")=="fixture" for p in rows) else "live"))
 now=now or _today_ist()
 point_time=now.replace(hour=8,minute=0) if replay_date else now  # a replayed day is shown from the start of school
 return DayPlan(school_id=school.id,date=day,now=_pick_now(hours,point_time),periods=plans,worst_hour=worst.time,best_hour=best.time,sources=Sources(forecast=forecast,observation=source.get("observation","none"),station=source.get("station"),distance_km=source.get("distance_km")),mode=actual_mode,generated_at=now.astimezone(IST).isoformat(timespec="seconds"),replay_date=replay_date)
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
