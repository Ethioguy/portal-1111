import pytest
from portal_ai import health_import as hi


def test_shortcut_json_is_the_happy_path():
    p = hi.parse('{"workouts":[{"date":"2026-11-27","type":"Running","distanceMi":3.12,'
                 '"durationMin":28.4,"avgHR":146,"kcal":312}]}')
    w = p["workouts"][0]
    assert (w["date"], w["mode"], w["miles"], w["minutes"], w["hr"]) == ("2026-11-27", "run", 3.12, 28.4, 146)


def test_kilometres_become_miles():
    w = hi.parse('[{"date":"2026-11-27","type":"Running","distanceKm":5.0,"durationMin":30}]')["workouts"][0]
    assert w["miles"] == 3.107


def test_clock_and_second_durations():
    assert hi.to_minutes("00:28:24") == 28.4
    assert hi.to_minutes("1704", "durationSec") == 28.4
    assert hi.to_minutes("28.4") == 28.4


def test_csv_from_an_export_app():
    csv = ("Date,Activity Type,Distance (km),Duration,Avg HR,Calories\n"
           "2026-11-25,Running,5.00,00:27:30,151,330\n"
           "2026-11-26,Cycling,20.1,01:02:00,128,540\n"
           "2026-11-27,Pool Swim,1.2,00:35:00,120,300\n")
    p = hi.parse(csv)
    assert [w["mode"] for w in p["workouts"]] == ["run", "bike"]      # the swim is not a run
    assert p["skipped"] == 1
    assert p["workouts"][0]["miles"] == 3.107


def test_activities_that_are_not_runs_are_left_alone():
    assert hi.classify("Traditional Strength Training") is None
    assert hi.classify("Indoor Cycling") == "bike"
    assert hi.classify("Trail Running") == "run"


def test_two_runs_in_a_day_add_up_and_a_run_beats_a_ride():
    p = hi.parse('[{"date":"2026-11-27","type":"Running","distanceMi":3,"durationMin":30},'
                 '{"date":"2026-11-27","type":"Running","distanceMi":2,"durationMin":18},'
                 '{"date":"2026-11-26","type":"Cycling","distanceMi":12,"durationMin":40},'
                 '{"date":"2026-11-26","type":"Running","distanceMi":4,"durationMin":36}]')
    days = hi.to_day_records(p)
    assert days["2026-11-27"] == {"miles": 5, "min": 48, "mode": "run", "done": True}
    assert days["2026-11-26"]["mode"] == "run" and days["2026-11-26"]["miles"] == 4


def test_unreadable_payloads_say_why():
    for bad, word in [("", "nothing"), ("{oops", "JSON"), ("a,b\n1,2\n", "date")]:
        with pytest.raises(hi.ImportError_) as e:
            hi.parse(bad)
        assert word.lower() in str(e.value).lower()


def test_nothing_in_this_module_touches_the_network():
    src = (__import__("pathlib").Path(hi.__file__)).read_text()
    for banned in ("requests", "urllib", "http", "socket"):
        assert banned not in src
