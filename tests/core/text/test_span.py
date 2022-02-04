from medkit.core.text.span import (
    Span,
    AdditionalSpan,
    replace,
    remove,
    extract,
    insert,
    move,
    _replace_in_spans,
    _remove_in_spans,
    _extract_in_spans,
    _insert_in_spans,
    _move_in_spans,
)


def test_replace():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = replace(text, spans, [(18, 22), (23, 26)], ["Jane", "Dean"])
    assert text == "Hello, my name is Jane Dean."
    assert spans == [
        Span(0, 18),
        AdditionalSpan(4, [Span(18, 22)]),
        Span(22, 23),
        AdditionalSpan(4, [Span(23, 26)]),
        Span(26, 27),
    ]


def test_remove():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = remove(text, spans, [(0, 7), (22, 27)])
    assert text == "my name is John"
    assert spans == [Span(7, 22)]


def test_extract():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = extract(text, spans, [(0, 7), (18, 22)])
    assert text == "Hello, John"
    assert spans == [Span(0, 7), Span(18, 22)]


def test_insert():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = insert(text, spans, [5], [" everybody"])
    assert text == "Hello everybody, my name is John Doe."
    assert spans == [Span(0, 5), AdditionalSpan(10, []), Span(5, 27)]


def test_move_before():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = move(text, spans, (17, 22), 5)
    assert text == "Hello John, my name is Doe."
    assert spans == [Span(0, 5), Span(17, 22), Span(5, 17), Span(22, 27)]


def test_move_after():
    text = "Hello, my name is John Doe."
    spans = [Span(0, 27)]
    text, spans = move(text, spans, (17, 22), 26)
    assert text == "Hello, my name is Doe John."
    assert spans == [Span(0, 17), Span(22, 26), Span(17, 22), Span(26, 27)]


def test_replace_in_spans():
    # only one span, starting at 0
    spans = [Span(0, 10)]
    # replace begining
    assert _replace_in_spans(spans, [(0, 6)], [6]) == [
        AdditionalSpan(6, [Span(0, 6)]),
        Span(6, 10),
    ]
    # replace end
    assert _replace_in_spans(spans, [(4, 10)], [6]) == [
        Span(0, 4),
        AdditionalSpan(6, [Span(4, 10)]),
    ]
    # replace inside
    assert _replace_in_spans(spans, [(4, 7)], [3]) == [
        Span(0, 4),
        AdditionalSpan(3, [Span(4, 7)]),
        Span(7, 10),
    ]
    # replace whole span
    assert _replace_in_spans(spans, [(0, 10)], [10]) == [
        AdditionalSpan(10, [Span(0, 10)])
    ]
    # replace several ranges
    assert _replace_in_spans(spans, [(3, 5), (7, 8)], [10, 5]) == [
        Span(0, 3),
        AdditionalSpan(10, [Span(3, 5)]),
        Span(5, 7),
        AdditionalSpan(5, [Span(7, 8)]),
        Span(8, 10),
    ]

    # only one span with non-zero start
    spans = [Span(10, 20)]
    # replace begining (same length)
    assert _replace_in_spans(spans, [(0, 6)], [6]) == [
        AdditionalSpan(6, [Span(10, 16)]),
        Span(16, 20),
    ]
    # replace end
    assert _replace_in_spans(spans, [(4, 10)], [6]) == [
        Span(10, 14),
        AdditionalSpan(6, [Span(14, 20)]),
    ]
    # replace inside
    assert _replace_in_spans(spans, [(4, 7)], [3]) == [
        Span(10, 14),
        AdditionalSpan(3, [Span(14, 17)]),
        Span(17, 20),
    ]
    # replace whole span
    assert _replace_in_spans(spans, [(0, 10)], [10]) == [
        AdditionalSpan(10, [Span(10, 20)])
    ]
    # replace inside (longer replacement)
    assert _replace_in_spans(spans, [(4, 7)], [10]) == [
        Span(10, 14),
        AdditionalSpan(10, [Span(14, 17)]),
        Span(17, 20),
    ]
    # replace inside (shorter replacement)
    assert _replace_in_spans(spans, [(4, 7)], [1]) == [
        Span(10, 14),
        AdditionalSpan(1, [Span(14, 17)]),
        Span(17, 20),
    ]
    # replace several ranges
    assert _replace_in_spans(spans, [(3, 5), (7, 8)], [10, 5]) == [
        Span(10, 13),
        AdditionalSpan(10, [Span(13, 15)]),
        Span(15, 17),
        AdditionalSpan(5, [Span(17, 18)]),
        Span(18, 20),
    ]

    # several spans
    spans = [Span(10, 20), Span(30, 40), Span(50, 60)]
    # replace end of 1st span
    assert _replace_in_spans(spans, [(4, 10)], [10]) == [
        Span(10, 14),
        AdditionalSpan(10, [Span(14, 20)]),
        Span(30, 40),
        Span(50, 60),
    ]
    # replace across several spans (end of 1st span and begining of 2d span)
    assert _replace_in_spans(spans, [(4, 14)], [10]) == [
        Span(10, 14),
        AdditionalSpan(10, [Span(14, 20), Span(30, 34)]),
        Span(34, 40),
        Span(50, 60),
    ]
    # replace across several spans (end of 1st span, entire 2d span, begining of 3d span)
    assert _replace_in_spans(spans, [(4, 24)], [10]) == [
        Span(10, 14),
        AdditionalSpan(10, [Span(14, 20), Span(30, 40), Span(50, 54)]),
        Span(54, 60),
    ]
    # replace several ranges
    assert _replace_in_spans(spans, [(4, 14), (16, 24)], [10, 5]) == [
        Span(10, 14),
        AdditionalSpan(10, [Span(14, 20), Span(30, 34)]),
        Span(34, 36),
        AdditionalSpan(5, [Span(36, 40), Span(50, 54)]),
        Span(54, 60),
    ]

    # mix of additional spans and normal spans
    spans = [
        AdditionalSpan(length=5, replaced_spans=[Span(10, 30)]),
        Span(30, 40),
        Span(50, 60),
    ]
    # replace across several spans (end of 1st span and begining of 2d span)
    assert _replace_in_spans(spans, [(4, 14)], [5]) == [
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(5, [Span(10, 30), Span(30, 39)]),
        Span(39, 40),
        Span(50, 60),
    ]
    # replace accross several spans (remove end of 1st span, remove 2d span fully, remove begining of last span)
    assert _replace_in_spans(spans, [(4, 24)], [5]) == [
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(5, [Span(10, 30), Span(30, 40), Span(50, 59)]),
        Span(59, 60),
    ]
    # replace several ranges
    assert _replace_in_spans(spans, [(4, 14), (16, 24)], [5, 10]) == [
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(5, [Span(10, 30), Span(30, 39)]),
        Span(39, 40),
        Span(50, 51),
        AdditionalSpan(10, [Span(51, 59)]),
        Span(59, 60),
    ]


def test_remove_in_spans():
    # only one span
    spans = [Span(10, 20)]
    # remove at begining
    assert _remove_in_spans(spans, [(0, 6)]) == [Span(16, 20)]
    # remove at end
    assert _remove_in_spans(spans, [(4, 10)]) == [Span(10, 14)]
    # remove inside
    assert _remove_in_spans(spans, [(4, 7)]) == [
        Span(10, 14),
        Span(17, 20),
    ]
    # remove fully
    assert _remove_in_spans(spans, [(0, 10)]) == []
    # remove several ranges
    assert _remove_in_spans(spans, [(3, 5), (7, 8)]) == [
        Span(10, 13),
        Span(15, 17),
        Span(18, 20),
    ]

    # several spans
    spans = [Span(10, 20), Span(30, 40), Span(50, 60)]
    # remove at end of 1st pan
    assert _remove_in_spans(spans, [(4, 10)]) == [
        Span(10, 14),
        Span(30, 40),
        Span(50, 60),
    ]
    # remove accross several spans (end of 1st span and begining of 2d span)
    assert _remove_in_spans(spans, [(4, 14)]) == [
        Span(10, 14),
        Span(34, 40),
        Span(50, 60),
    ]
    # remove accross several spans (remove end of 1st span, remove 2d span fully, remove begining of last span)
    assert _remove_in_spans(spans, [(4, 24)]) == [Span(10, 14), Span(54, 60)]
    # remove several ranges
    assert _remove_in_spans(spans, [(4, 14), (16, 24)]) == [
        Span(10, 14),
        Span(34, 36),
        Span(54, 60),
    ]

    # additional span
    spans = [AdditionalSpan(length=10, replaced_spans=[Span(10, 30)])]
    # remove at begining
    assert _remove_in_spans(spans, [(0, 6)]) == [AdditionalSpan(4, [Span(10, 30)])]
    # remove at end
    assert _remove_in_spans(spans, [(4, 10)]) == [AdditionalSpan(4, [Span(10, 30)])]
    # remove inside
    assert _remove_in_spans(spans, [(4, 7)]) == [
        # TODO should be this?
        # AdditionalSpan(7, [Span(10, 30)])
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(3, [Span(10, 30)]),
    ]
    # remove fully
    assert _remove_in_spans(spans, [(0, 10)]) == []
    # remove several ranges
    assert _remove_in_spans(spans, [(4, 6), (7, 9)]) == [
        # TODO should be this?
        # AdditionalSpan(6, [Span(10, 30)])
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(1, [Span(10, 30)]),
        AdditionalSpan(1, [Span(10, 30)]),
    ]

    # mix of additional spans and normal spans
    spans = [AdditionalSpan(length=10, replaced_spans=[Span(10, 30)]), Span(30, 40)]
    # remove accross both (end of 1st pan and begining of 2d span)
    assert _remove_in_spans(spans, [(4, 14)]) == [
        AdditionalSpan(4, [Span(10, 30)]),
        Span(34, 40),
    ]
    # remove several ranges
    assert _remove_in_spans(spans, [(4, 7), (9, 14)]) == [
        AdditionalSpan(4, [Span(10, 30)]),
        AdditionalSpan(2, [Span(10, 30)]),
        Span(34, 40),
    ]


def test_extract_in_spans():
    # only one span
    spans = [Span(10, 20)]
    # extract begining
    assert _extract_in_spans(spans, [(0, 6)]) == [Span(10, 16)]
    # extract end
    assert _extract_in_spans(spans, [(4, 10)]) == [Span(14, 20)]
    # extract whole span
    assert _extract_in_spans(spans, [(0, 10)]) == [Span(10, 20)]
    # remove several ranges
    assert _extract_in_spans(spans, [(3, 5), (7, 8)]) == [
        Span(13, 15),
        Span(17, 18),
    ]

    # several spans
    spans = [Span(10, 20), Span(30, 40), Span(50, 60)]
    # extract end of 1st span
    assert _extract_in_spans(spans, [(4, 10)]) == [Span(14, 20)]
    # extract in several spans (end of 1st span and begining of 2d span)
    assert _extract_in_spans(spans, [(4, 14)]) == [
        Span(14, 20),
        Span(30, 34),
    ]
    # extract in several spans (end of 1st span, entire 2d span, begining of 3d span)
    assert _extract_in_spans(spans, [(4, 24)]) == [
        Span(14, 20),
        Span(30, 40),
        Span(50, 54),
    ]
    # extract several ranges
    assert _extract_in_spans(spans, [(4, 14), (16, 24)]) == [
        Span(14, 20),
        Span(30, 34),
        Span(36, 40),
        Span(50, 54),
    ]

    # additional span
    spans = [AdditionalSpan(length=10, replaced_spans=[Span(10, 30)])]
    # extract begining
    assert _extract_in_spans(spans, [(0, 6)]) == [AdditionalSpan(6, [Span(10, 30)])]
    # extract end
    assert _extract_in_spans(spans, [(4, 10)]) == [AdditionalSpan(6, [Span(10, 30)])]
    # extract inside
    assert _extract_in_spans(spans, [(4, 7)]) == [AdditionalSpan(3, [Span(10, 30)])]
    # extract fully
    assert _extract_in_spans(spans, [(0, 10)]) == [AdditionalSpan(10, [Span(10, 30)])]

    # mix of additional spans and normal spans
    spans = [AdditionalSpan(length=10, replaced_spans=[Span(10, 30)]), Span(30, 40)]
    # extract in both (end of 1st pan and begining of 2d span)
    assert _extract_in_spans(spans, [(4, 14)]) == [
        AdditionalSpan(6, [Span(10, 30)]),
        Span(30, 34),
    ]


def test_insert_in_spans():
    # only one span
    spans = [Span(10, 20)]
    # insert at begining
    assert _insert_in_spans(spans, [0], [5]) == [AdditionalSpan(5, []), Span(10, 20)]
    # insert at end
    assert _insert_in_spans(spans, [10], [5]) == [Span(10, 20), AdditionalSpan(5, [])]
    # insert inside
    assert _insert_in_spans(spans, [4], [5]) == [
        Span(10, 14),
        AdditionalSpan(5, []),
        Span(14, 20),
    ]
    # insert several
    assert _insert_in_spans(spans, [4, 7], [5, 10]) == [
        Span(10, 14),
        AdditionalSpan(5, []),
        Span(14, 17),
        AdditionalSpan(10, []),
        Span(17, 20),
    ]

    # additional span
    spans = [AdditionalSpan(length=10, replaced_spans=[Span(20, 40)])]
    # insert at begining
    assert _insert_in_spans(spans, [0], [5]) == [
        AdditionalSpan(5, []),
        AdditionalSpan(10, [Span(20, 40)]),
    ]
    # insert at end
    assert _insert_in_spans(spans, [10], [5]) == [
        AdditionalSpan(10, [Span(20, 40)]),
        AdditionalSpan(5, []),
    ]
    # insert inside
    assert _insert_in_spans(spans, [4], [5]) == [
        AdditionalSpan(4, [Span(20, 40)]),
        AdditionalSpan(5, []),
        AdditionalSpan(6, [Span(20, 40)]),
    ]


def test_move_in_spans():
    # only one span
    spans = [Span(10, 30)]
    # move from begining to end
    assert _move_in_spans(spans, (0, 5), 20) == [Span(15, 30), Span(10, 15)]
    # move from end to begining
    assert _move_in_spans(spans, (15, 20), 0) == [Span(25, 30), Span(10, 25)]
    # move from inside to end
    assert _move_in_spans(spans, (5, 10), 20) == [
        Span(10, 15),
        Span(20, 30),
        Span(15, 20),
    ]
    # move from inside to begining
    assert _move_in_spans(spans, (5, 10), 0) == [
        Span(15, 20),
        Span(10, 15),
        Span(20, 30),
    ]
    # move from inside to inside
    assert _move_in_spans(spans, (5, 10), 12) == [
        Span(10, 15),
        Span(20, 22),
        Span(15, 20),
        Span(22, 30),
    ]

    # several spans
    spans = [Span(10, 30), Span(40, 60), Span(70, 90)]
    # move from accross several spans
    assert _move_in_spans(spans, (5, 45), 50) == [
        Span(10, 15),
        Span(75, 80),
        Span(15, 30),
        Span(40, 60),
        Span(70, 75),
        Span(80, 90),
    ]
