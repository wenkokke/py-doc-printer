from doc_printer import *


def test_render_Alt_failing():
    smart = SmartDocRenderer(max_line_width=10)
    doc = SoftLine.join("01 02 03 04 05 06 07 08 09".split())
    act = smart.to_str(doc)
    exp = "\n".join(
        [
            "01 02 03",
            "04 05 06",
            "07 08 09",
        ]
    )
    assert act == exp


def test_render_Alt_Cat_failing():
    smart = SmartDocRenderer(max_line_width=5)
    doc = Cat(SoftLine.join("1 2 3 4 5 6 7 8 9".split()))
    act = smart.to_str(doc)
    exp = "\n".join(
        [
            "1 2 3",
            "4 5 6",
            "7 8 9",
        ]
    )
    assert act == exp


def test_render_Alt_Nest_failing():
    smart = SmartDocRenderer(max_line_width=7)
    doc = Space / Space / nest(2, SoftLine.join("1 2 3 4 5 6 7 8 9".split()))
    act = smart.to_str(doc)
    exp = "\n".join(
        [
            "  1 2 3",
            "  4 5 6",
            "  7 8 9",
        ]
    )
    assert act == exp
