build:
	poetry build

build-doc:
	poetry install -E docs
	poetry run sphinx-build -M "html" "docs" "docs/_build"

serve:
	@(cd docs/_build/html && npx browser-sync -ss)

test:
	tox --skip-missing-interpreters

bump-patch:
	@poetry run bumpver update --patch

bump-minor:
	@poetry run bumpver update --minor

bump-major:
	@poetry run bumpver update --major

.PHONY: build build-doc serve test bump-patch bump-minor bump-major
