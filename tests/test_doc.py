from doc_printer import (
    Alt,
    Empty,
    Fail,
    Line,
    SoftLine,
    Space,
    Text,
    Unknown,
    WidthHint,
    cat,
    nest,
)


def test_WidthHint_intern_Unknown() -> None:
    assert Unknown is WidthHint(0, False)
    assert Unknown is WidthHint.intern_Unknown()
    assert Unknown.is_Unknown()
    assert repr(Unknown) == "Unknown"


def test_Text_intern_Empty() -> None:
    assert Empty is Text("")
    assert Empty is Text.intern_Empty()
    assert Empty.is_Empty()
    assert repr(Empty) == "Empty"


def test_Text_intern_Space() -> None:
    assert Space is Text(" ")
    assert Space is Text.intern_Space()
    assert Space.is_Space()
    assert repr(Space) == "Space"


def test_Text_intern_Line() -> None:
    assert Line is Text("\n")
    assert Line is Text.intern_Line()
    assert Line.is_Line()
    assert repr(Line) == "Line"


def test_Alt_intern_Fail() -> None:
    assert Fail is Alt(alts=())
    assert Fail is Alt.intern_Fail()
    assert Fail.is_Fail()
    assert repr(Fail) == "Fail"


def test_Alt_intern_SoftLine() -> None:
    assert SoftLine is Alt(alts=(Line, Space))
    assert SoftLine is Alt.intern_SoftLine()
    assert SoftLine.is_SoftLine()
    assert repr(SoftLine) == "SoftLine"


def test_DocLike_Line() -> None:
    assert cat("hello\nworld") == cat("hello", Line, "world")


def test_DocLike_Space() -> None:
    assert cat("hello world") == cat("hello", Space, "world")


def test_DocLike_Line_and_Space() -> None:
    cat1 = cat("hello world\nwello horld")
    cat2 = cat("hello", Space, "world", Line, "wello", Space, "horld")
    assert cat1 == cat2


def test_Cat_Empty() -> None:
    hello = Text("hello")
    assert cat() is Empty
    assert Empty / hello == hello
    assert hello / Empty == hello
    assert Empty // hello == hello
    assert hello // Empty == hello


def test_Nest_Empty() -> None:
    assert nest(4, Empty) is Empty


def test_Cat_with_auto_Space() -> None:
    hello = Text("hello")
    world = Text("world")
    assert Empty // world == world
    assert Space // world == world
    assert hello // Empty == hello
    assert hello // Space == hello
    assert hello // world == cat(hello, Space, world)
    assert cat(hello, Space) // world == cat(hello, Space, world)
    assert hello // cat(Space, world) == cat(hello, Space, world)
    assert hello // world != world // hello


def test_None_DocLike() -> None:
    assert cat(None, None, None) is Empty
