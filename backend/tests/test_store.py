from saans.store import JsonStore,SEED_SCHOOLS
def test_json_store_seeds_three_schools(tmp_path):
 s=JsonStore(tmp_path/'schools.json'); assert len(s.list())==3 and s.get('delhi-anand-vihar').timetable[1].label=='Class 7B PE'
