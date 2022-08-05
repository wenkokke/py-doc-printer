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
    act = simple.to_str(doc)
    exp = "\n".join(
        [
            "label:     a",
            "           b",
        ]
    )
    assert act == exp


def test_single_quote():
    simple = SimpleDocRenderer()
    doc = single_quote("'hello'", Space, '"world"')
    act = simple.to_str(doc)
    exp = "'\\'hello\\' \"world\"'"
    assert act == exp


def test_double_quote():
    simple = SimpleDocRenderer()
    doc = double_quote("'hello'", Space, '"world"')
    act = simple.to_str(doc)
    exp = '"\'hello\' \\"world\\""'
    assert act == exp


def test_single_quote_auto_unescape():
    simple = SimpleDocRenderer()
    doc = single_quote("\\'hello\\'", Space, '\\"world\\"')
    act = simple.to_str(doc)
    exp = "'\\'hello\\' \"world\"'"
    assert act == exp


def test_double_quote_auto_unescape():
    simple = SimpleDocRenderer()
    doc = double_quote("\\'hello\\'", Space, '\\"world\\"')
    act = simple.to_str(doc)
    exp = '"\'hello\' \\"world\\""'
    assert act == exp


def test_single_quote_no_auto_unescape():
    simple = SimpleDocRenderer()
    doc = single_quote("\\'hello\\'", Space, '\\"world\\"', auto_unescape=False)
    act = simple.to_str(doc)
    exp = "'\\'hello\\' \\\"world\\\"'"
    assert act == exp


def test_double_quote_no_auto_unescape():
    simple = SimpleDocRenderer()
    doc = double_quote("\\'hello\\'", Space, '\\"world\\"', auto_unescape=False)
    act = simple.to_str(doc)
    exp = '"\\\'hello\\\' \\"world\\""'
    assert act == exp


def test_smart_quote():
    simple = SimpleDocRenderer()
    doc = smart_quote("\\'hello\\'", Space, '\\"world\\"')
    act = simple.to_str(doc)
    exp = '"\'hello\' \\"world\\""'
    assert act == exp
