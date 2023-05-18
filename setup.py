import mypyc.build
import setuptools


def main() -> None:
    setuptools.setup(
        ext_modules=mypyc.build.mypycify(
            [
                "src/doc_printer/_compat_itertools.py",
                "src/doc_printer/_compat_singledispatchmethod.py",
                # "src/doc_printer/doc.py",
                "src/doc_printer/doc_renderer/abc.py",
                # "src/doc_printer/doc_renderer/simple.py",
                # "src/doc_printer/doc_renderer/smart.py",
                # "src/doc_printer/doc_renderer/table.py",
            ]
        )
    )


if __name__ == "__main__":
    main()
