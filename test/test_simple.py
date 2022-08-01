from doc_printer import *


def test_render_Nest_2():
    simple = SimpleDocRenderer()
    doc = Text("label:") // Nest(2, Text("a") / Line / Text("b"))
    out = "\n".join(
        [
            "label: a",
            "  b",
        ]
    )
    assert simple.to_str(doc) == out


def test_render_Nest_10():
    simple = SimpleDocRenderer()
    doc = Text("label:") // Nest(10, Text("a") / Line / Text("b"))
    out = "\n".join(
        [
            "label: a",
            "          b",
        ]
    )
    assert simple.to_str(doc) == out


def test_render_Nest_with_overlap_2():
    simple = SimpleDocRenderer()
    doc = Text("label:") // Nest(2, Text("a") / Line / Text("b"), overlap=True)
    exp = "\n".join(
        [
            "label: a",
            "  b",
        ]
    )
    act = simple.to_str(doc)
    print(exp)
    print(act)
    assert act == exp


def test_render_Nest_with_overlap_10():
    simple = SimpleDocRenderer()
    doc = Text("label:") // Nest(10, Text("a") / Line / Text("b"), overlap=True)
    exp = "\n".join(
        [
            "label:    a",
            "          b",
        ]
    )
    assert simple.to_str(doc) == exp


def test_render_Nest_Space():
    simple = SimpleDocRenderer()
    doc = Text("label:") // Nest(
        10, Space / Text("a") / Line / Space / Text("b"), overlap=True
    )
    exp = "\n".join(
        [
            "label:     a",
            "           b",
        ]
    )
    assert simple.to_str(doc) == exp
