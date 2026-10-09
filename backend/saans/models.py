from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal
from .rules import Action

class Period(BaseModel):
 id:str; label:str; start:str; end:str; type:Literal['assembly','pe','recess','sports','class']; intensity:Literal['high','low']; outdoor:bool; swappable:bool; grade:str|None=None
class School(BaseModel):
 id:str; name:str; city:str; lat:float; lon:float; timetable:list[Period]; sensitive_count:int=0; languages:list[str]=Field(default_factory=lambda:['en','hi'])
class HourPoint(BaseModel):
 time:str; pm25:float; pm10:float; pm25_cal:float; pm10_cal:float; aqi:int; band:str; calibrated:bool
class Swap(BaseModel):
 to_start:str; to_end:str; to_aqi:int; to_band:str; gain_bands:int; optional:bool=False; with_period_id:str|None=None; with_label:str|None=None
class PeriodPlan(BaseModel):
 period:Period; aqi:int; band:str; action:Action; sensitive_action:Action; swap:Swap|None=None
class Sources(BaseModel):
 forecast:str; observation:str; station:str|None=None; distance_km:float|None=None; note:str|None=None
class DayPlan(BaseModel):
 school_id:str; date:str; now:HourPoint|None=None; periods:list[PeriodPlan]; worst_hour:str; best_hour:str; sources:Sources; mode:Literal['live','cached','fixture','replay']; generated_at:str; replay_date:str|None=None
class WeekPlan(BaseModel):
 days:list[dict]; hourly:list[HourPoint]
