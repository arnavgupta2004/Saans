from saans.store import JsonStore,SEED_SCHOOLS
def test_json_store_seeds_three_schools(tmp_path):
 s=JsonStore(tmp_path/'schools.json'); assert len(s.list())==3 and s.get('delhi-anand-vihar').timetable[1].label=='Class 7B PE'


def test_seed_pe_labels_match_grades_and_two_grades_per_school() -> None:
    from saans.store import SEED_SCHOOLS
    for s in SEED_SCHOOLS:
        pe = [p for p in s.timetable if p.type == "pe"]
        assert len({p.grade for p in pe}) == 2 and all(p.label == f"Class {p.grade} PE" for p in pe)
