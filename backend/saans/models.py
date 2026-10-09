from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal
from .rules import Action

class Period(BaseModel):
 id:str; label:str; start:str; end:str; type:Literal['assembly','pe','recess','sports','class']; intensity:Literal['high','low']; outdoor:bool; swappable:bool; grade:str|None=None
class School(BaseModel):
 id:str; name:str; city:str; lat:float; lon:float; timetable:list[Period]; sensitive_count:int=0; students_per_class:int=40; languages:list[str]=Field(default_factory=lambda:['en','hi'])
class HourPoint(BaseModel):
 time:str; pm25:float; pm10:float; pm25_cal:float; pm10_cal:float; aqi:int; band:str; calibrated:bool
class SwapImpact(BaseModel):
 """Estimated outdoor PM2.5 exposure avoided if this swap is applied (indoor infiltration not modelled)."""
 pm25_before:float; pm25_after:float; reduction_pct:int; minutes:int; students:int; exposure_avoided:float; band_from:str; band_to:str
class Swap(BaseModel):
 to_start:str; to_end:str; to_aqi:int; to_band:str; gain_bands:int; optional:bool=False; with_period_id:str|None=None; with_label:str|None=None; impact:SwapImpact|None=None
class PeriodPlan(BaseModel):
 period:Period; aqi:int; band:str; action:Action; sensitive_action:Action; swap:Swap|None=None
class Sources(BaseModel):
 forecast:str; observation:str; station:str|None=None; distance_km:float|None=None; note:str|None=None
class DayImpact(BaseModel):
 """Totals over suggested (non-optional) swaps for one day. An estimate, not a measurement."""
 swaps:int=0; students_moved:int=0; minutes:int=0; student_hours_out_of_poor:float=0; exposure_avoided:float=0; reduction_pct:int=0; worst_band_from:str|None=None
class DayPlan(BaseModel):
 school_id:str; date:str; now:HourPoint|None=None; periods:list[PeriodPlan]; worst_hour:str; best_hour:str; sources:Sources; mode:Literal['live','cached','fixture','replay']; generated_at:str; replay_date:str|None=None; impact:DayImpact=Field(default_factory=DayImpact)
class WeekPlan(BaseModel):
 days:list[dict]; hourly:list[HourPoint]
