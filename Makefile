SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = doc-source
BUILDDIR      = _build

html: Makefile
	@$(SPHINXBUILD) -M "html" "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# Publish to PyPi

CURRENT_VERSION = $(shell eval $$(bumpver show --no-fetch --env) && echo "$$CURRENT_VERSION")

CURRENT_WHEEL = dist/doc_printer-$(CURRENT_VERSION)-py3-none-any.whl
CURRENT_TARGZ = dist/doc-printer-$(CURRENT_VERSION).tar.gz

SOURCES = $(shell find doc_printer -name "*.py")

$(CURRENT_WHEEL) $(CURRENT_TARGZ): $(SOURCES)
	python -m build

testpublish: $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	twine check $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	twine upload -r testpypi $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	touch testpublish

publish: $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	twine check $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	twine upload -r pypi $(CURRENT_WHEEL) $(CURRENT_TARGZ)
	touch publish
