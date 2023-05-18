import mypyc.build
import setuptools


def main():
    setuptools.setup(
        ext_modules=mypyc.build.mypycify(
            [
                "src/doc_printer/_compat_itertools.py",
                "src/doc_printer/_compat_singledispatchmethod.py",
            ]
        )
    )


if __name__ == "__main__":
    main()
