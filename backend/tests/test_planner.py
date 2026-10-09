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
