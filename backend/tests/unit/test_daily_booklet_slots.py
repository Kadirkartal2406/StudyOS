from app.core.exam_identity import daily_booklet_slots


def test_yks_gets_tyt_and_ayt_slots():
    slots = daily_booklet_slots("yks", "sayisal")
    assert [(s.exam, s.branch, s.label) for s in slots] == [
        ("tyt", None, "TYT"),
        ("ayt", "sayisal", "AYT"),
    ]


def test_yks_ea_and_sozel_ayt_branch():
    assert daily_booklet_slots("yks", "ea")[1].branch == "ea"
    assert daily_booklet_slots("yks", "sozel")[1].branch == "sozel"


def test_yks_without_branch_defaults_ayt_sayisal():
    slots = daily_booklet_slots("yks", None)
    assert slots[0].exam == "tyt"
    assert slots[1] == daily_booklet_slots("yks", "sayisal")[1]


def test_yks_dil_gets_tyt_and_ydt():
    slots = daily_booklet_slots("yks", "dil")
    assert [(s.exam, s.branch) for s in slots] == [("tyt", None), ("ydt", "en")]


def test_tyt_only_one_slot():
    slots = daily_booklet_slots("tyt", None)
    assert len(slots) == 1
    assert slots[0].exam == "tyt"


def test_ayt_only_one_slot():
    slots = daily_booklet_slots("ayt", "ea")
    assert len(slots) == 1
    assert slots[0].exam == "ayt"
    assert slots[0].branch == "ea"
    named = daily_booklet_slots("ayt_ea", None)
    assert named[0].exam == "ayt"
    assert named[0].branch == "ea"


def test_kpss_maps_to_scheduler_parent_and_branch():
    slots = daily_booklet_slots("kpss", None)
    assert [(s.exam, s.branch) for s in slots] == [("kpss", "lisans")]
    slots2 = daily_booklet_slots("kpss_onlisans", None)
    assert slots2[0].branch == "onlisans"
