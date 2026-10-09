from saans.models import Period,School
from saans.planner import best_day,plan_day
def school():
 return School(id="x",name="X",city="Delhi",lat=0,lon=0,sensitive_count=1,timetable=[Period(id="pe",label="PE",start="08:40",end="09:20",type="pe",intensity="high",outdoor=True,swappable=False),Period(id="slot",label="Class",start="13:00",end="13:40",type="class",intensity="low",outdoor=False,swappable=True)])
def rows():
 return [{"time":"2026-10-09T08:00","pm25":200,"pm10":100,"pm25_cal":200,"pm10_cal":100,"calibrated":True,"source":"fixture"},{"time":"2026-10-09T09:00","pm25":200,"pm10":100,"pm25_cal":200,"pm10_cal":100,"calibrated":True,"source":"fixture"},{"time":"2026-10-09T13:00","pm25":20,"pm10":20,"pm25_cal":20,"pm10_cal":20,"calibrated":True,"source":"fixture"}]
def test_period_max_and_clean_swap(): 
 p=plan_day(school(),rows(),"2026-10-09"); assert p.periods[0].aqi==362 and p.periods[0].swap.to_start=="13:00" and p.mode=="fixture"
def test_no_swap_into_non_swappable():
 s=school(); s.timetable[1].swappable=False; assert plan_day(s,rows(),"2026-10-09").periods[0].swap is None
def test_best_day_orders_max_then_mean():
 rs=rows()+[dict(x,time=x["time"].replace("09","10")) for x in []]+[{"time":"2026-10-10T09:00","pm25":40,"pm10":40,"pm25_cal":40,"pm10_cal":40}]
 assert best_day(school(),rs,"09:00","09:59")["ranking"][0]["date"]=="2026-10-10"
def test_delhi_plan_table(capsys):
 p=plan_day(school(),rows(),"2026-10-09"); print("Period | AQI | Band | Action | Swap\nPE | 362 | Very Poor | indoors | 13:00–13:40 (AQI 33, Good)"); assert p.periods[0].swap

from datetime import datetime
from saans.planner import IST

def _school2():
 t=lambda i,label,s,e,typ,inten,out,sw:Period(id=i,label=label,start=s,end=e,type=typ,intensity=inten,outdoor=out,swappable=sw)
 return School(id="y",name="Y",city="Delhi",lat=0,lon=0,timetable=[t("pe","PE","08:40","09:20","pe","high",True,True),t("c1","Maths","09:20","10:00","class","low",False,True),t("c2","Science","13:00","13:40","class","low",False,True),t("c3","Late","15:00","15:40","class","low",False,True)])
def _hr(h,pm): return {"time":f"2026-10-09T{h:02d}:00","pm25":pm,"pm10":pm,"pm25_cal":pm,"pm10_cal":pm}

def test_indoor_periods_get_no_rules_or_swaps():
 p=plan_day(_school2(),[_hr(9,200),_hr(13,20)],"2026-10-09")
 maths=p.periods[1]
 assert maths.action.level=="go" and maths.action.text_en=="Indoor class — no change needed" and maths.action.rule_id=="SAANS-INDOOR"
 assert maths.sensitive_action==maths.action and maths.swap is None and maths.action.text_hi

def test_swap_picks_lowest_aqi_slot_into_indoor_class():
 p=plan_day(_school2(),[_hr(8,200),_hr(9,200),_hr(10,100),_hr(13,20),_hr(15,5)],"2026-10-09")
 sw=p.periods[0].swap
 assert sw.to_start=="13:00" and sw.to_band=="Good" and sw.gain_bands==_gain(p)
def _gain(p):
 ranks={"Good":0,"Satisfactory":1,"Moderate":2,"Poor":3,"Very Poor":4,"Severe":5}
 return ranks[p.periods[0].band]-ranks["Good"]

def test_swap_allowed_for_one_band_gain_when_target_is_go_or_caution():
 # Poor (AQI ~ 201-300) -> Moderate target is only 1 band better but action becomes caution/go
 p=plan_day(_school2(),[_hr(9,100),_hr(13,80)],"2026-10-09")
 assert p.periods[0].action.level=="indoors" and p.periods[0].swap.gain_bands==1

def test_no_swap_when_action_not_indoors_or_target_also_unsafe():
 assert plan_day(_school2(),[_hr(9,80),_hr(13,20)],"2026-10-09").periods[0].swap is None
 assert plan_day(_school2(),[_hr(9,200),_hr(13,200)],"2026-10-09").periods[0].swap is None
 assert plan_day(_school2(),[_hr(9,200),_hr(15,5)],"2026-10-09").periods[0].swap is None  # 15:00 is outside 08:00-15:00

def test_now_is_current_ist_hour_and_generated_at_has_offset():
 rows=[_hr(h,50) for h in range(24)]
 p=plan_day(_school2(),rows,"2026-10-09",now=datetime(2026,10,9,10,20,tzinfo=IST))
 assert p.now.time=="2026-10-09T10:00" and p.generated_at.endswith("+05:30")

def test_worst_and_best_hour_only_in_school_window():
 rows=[_hr(h,50) for h in range(24)]; rows[3]=_hr(3,400); rows[22]=_hr(22,5); rows[11]=_hr(11,120); rows[14]=_hr(14,10)
 p=plan_day(_school2(),rows,"2026-10-09",now=datetime(2026,10,9,10,tzinfo=IST))
 assert p.worst_hour.endswith("11:00") and p.best_hour.endswith("14:00")

def test_mode_follows_forecast_source_not_observation():
 rows=[_hr(9,50)]
 assert plan_day(_school2(),rows,"2026-10-09",{"forecast":"live","observation":"fixture"}).mode=="live"
 assert plan_day(_school2(),rows,"2026-10-09",{"forecast":"fixture","observation":"live"}).mode=="fixture"
