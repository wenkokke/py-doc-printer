from doc_printer import *


def test_Text_intern_Empty():
    assert Empty is Text("")
    assert Empty is Text.intern_Empty()
    assert Empty.is_Empty()
    assert repr(Empty) == "Empty"


def test_Text_intern_Space():
    assert Space is Text(" ")
    assert Space is Text.intern_Space()
    assert Space.is_Space()
    assert repr(Space) == "Space"


def test_Text_intern_Line():
    assert Line is Text("\n")
    assert Line is Text.intern_Line()
    assert Line.is_Line()
    assert repr(Line) == "Line"


def test_Alt_intern_Fail():
    assert Fail is Alt(alts=())
    assert Fail is Alt.intern_Fail()
    assert Fail.is_Fail()
    assert repr(Fail) == "Fail"


def test_Alt_intern_SoftLine():
    assert SoftLine is Alt(alts=(Line, Empty))
    assert SoftLine is Alt.intern_SoftLine()
    assert SoftLine.is_SoftLine()
    assert repr(SoftLine) == "SoftLine"


def test_DocLike_Line():
    assert cat("hello\nworld") == cat("hello", Line, "world")


def test_DocLike_Space():
    assert cat("hello world") == cat("hello", Space, "world")


def test_DocLike_Line_and_Space():
    cat1 = cat("hello world\nwello horld")
    cat2 = cat("hello", Space, "world", Line, "wello", Space, "horld")
    assert cat1 == cat2


def test_Cat_Empty():
    hello = Text("hello")
    assert cat() is Empty
    assert Empty / hello == hello
    assert hello / Empty == hello
    assert Empty // hello == hello
    assert hello // Empty == hello


def test_Nest_Empty():
    assert nest(4, Empty) is Empty


def test_Cat_with_auto_Space():
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


def test_None_DocLike():
    assert cat(None, None, None) is Empty
