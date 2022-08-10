import pytest

from doc_printer import *


@pytest.mark.golden_test("data/golden/**/*.yml")
def test_golden(benchmark, golden):
    doc_renderer: DocRenderer
    if golden["input"]["renderer"] == "simple":
        simple_layout = SimpleLayout[golden["input"]["simple_layout"]]
        doc_renderer = SimpleDocRenderer(simple_layout=simple_layout)
    else:
        max_line_width = int(golden["input"]["max_line_width"])
        doc_renderer = SmartDocRenderer(max_line_width=max_line_width)

    doc = Doc.from_dict(golden["input"]["doc"])

    assert benchmark(doc_renderer.to_str, doc) == golden.out["output"]
