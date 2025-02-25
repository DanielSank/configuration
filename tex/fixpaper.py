r"""
Tools to convert files in a LaTeX project into a single compilable file.

The project is assumed to have the following file tree:
    main.tex
    content.tex

content.tex may have any number of \subimportlevel macro calls.
main.tex is assumed to \input content.tex.
"""
import contextlib
import os
import re
import pathlib
import shutil


RE_SECTIONLIKE = re.compile(r"\\(leveldown|levelstay){(.*)}(.*)")
RE_SUBIMPORTLEVEL = re.compile(r"\\subimportlevel{(.*)}{(.*)}{(.*)}")
RE_INPUT = re.compile(r"\\input{(.*)}")
RE_BIBLIOGRAPHY = re.compile(r"\\bibliography\{references\}.*")


@contextlib.contextmanager
def cd(x):
    d = os.getcwd()
    os.chdir(x)
    try:
        yield
    finally:
        os.chdir(d)


class DepthCounter:
    levels = ["section", "subsection", "subsubsection"]

    def __init__(self, level: int) -> None:
        self.level = level

    def leveldown(self) -> str:
        self.level += 1
        return self.levels[self.level]

    def levelstay(self) -> str:
        return self.levels[self.level]

    def levelup(self) -> str:
        self.level -= 1
        return self.levels[self.level]

    def handle(self, text: str) -> str:
        return getattr(self, text)()


def handle_line_section(line: str, depth_counter: DepthCounter) -> str:
    maybe_result = RE_SECTIONLIKE.match(line)
    if maybe_result is None:
        return line
    groups = maybe_result.groups()
    levelupdownetc = groups[0]
    name = groups[1]
    if len(groups) == 3:
        suffix = groups[2]
    else:
        suffix = ""
    section_type = depth_counter.handle(levelupdownetc)
    return "\\" + section_type + "{" + name + "}" + suffix + "\n"


def handle_file(filename: str, level: int) -> str:
    lines_in: list[str]
    lines_out: list[str] = []
    counter = DepthCounter(level)
    with open(filename, "r") as f:
        lines_in = f.readlines()
    for line in lines_in:
        lines_out.append(handle_line_section(line, counter))
    return "".join(lines_out)


def handle_line_subimportlevel(line: str) -> None | tuple[str, int]:
    maybe_result = RE_SUBIMPORTLEVEL.match(line)
    if maybe_result is None:
        return
    _, filename, level = maybe_result.groups()
    return filename, int(level)


def handle_content(filename: str) -> tuple[str, dict[str, int]]:
    lines_in: list[str]
    lines_out: list[str] = []
    levels: dict[str, int] = {}
    with open(filename, "r") as f:
        lines_in = f.readlines()
    for line in lines_in:
        maybe_result = handle_line_subimportlevel(line)
        if maybe_result is None:
            lines_out.append(line)
            continue
        filename, level = maybe_result
        levels[filename] = level
        lines_out.append("\\input" + "{" + filename + "}" + "\n")
    return "".join(lines_out), levels


def replace_subimports_with_input(root_file: str):
    """Files are written to build/"""
    content_out, levels = handle_content(root_file)
    files_out: dict[str, str] = {}
    for filename, level in levels.items():
        files_out[filename] = handle_file(filename, level)
    durr = pathlib.Path("build/")
    durr.mkdir(parents=True, exist_ok=True)
    files_out[root_file] = content_out

    # Write out all of the modified files.
    for filename, text in files_out.items():
        with (durr / filename).open("w", encoding="utf-8") as f:
            f.write(text)

    # Copy pdf, bib, and some other unmodified files.
    filenames = [
            "main.tex",
            "abstract.tex",
            "macros.tex",
            "packages.tex",
            "references.bib",
            "main.bbl",
    ]
    for filename in os.listdir("."):
        if filename.endswith("pdf"):
            filenames.append(filename)
    for filename in filenames:
        try:
            shutil.copyfile(filename, durr / filename)
        except Exception as e:
            print(e)


def _recurse(filename: str, outlines: list[str]) -> None:
    with open(filename, "r") as file:
        lines = file.readlines()
    for line in lines:
        maybe_match = RE_INPUT.match(line)
        if not maybe_match is None:
            input_filename = maybe_match.groups()[0]
            _recurse(input_filename, outlines)
            continue
        outlines.append(line)


def replace_input_with_inline_text(filename_in: str, filename_out: str) -> None:
    outlines: list[str] = []
    _recurse(filename_in, outlines)
    with open(filename_out, "w", encoding="utf-8") as file:
        file.write("".join(outlines))


def fix_bibliography(filename_in: str, filename_out: str, filename_bbl: str) -> None:
    lines_in: list[str]
    lines_out: list[str] = []

    with open(filename_bbl, "r") as file:
        lines_bbl = file.read()
    with open(filename_in, "r") as file:
        lines_in = file.readlines()
    for line in lines_in:
        if RE_BIBLIOGRAPHY.match(line):
            for line_bbl in lines_bbl:
                lines_out.append(line_bbl)
        else:
            lines_out.append(line)
    with open(filename_out, "w", encoding="utf-8") as file:
        file.write("".join(lines_out))


def main():
    # Make the bibliography file
    os.system("pdflatex main.tex")
    os.system("pdflatex main.tex")
    os.system("bibtex main.aux")

    replace_subimports_with_input("content.tex")
    with cd("build"):
        replace_input_with_inline_text(filename_in="main.tex", filename_out="main.tex")
        fix_bibliography("main.tex", "main.tex", "main.bbl")
        os.system("pdflatex main.tex")
        os.system("pdflatex main.tex")
        os.system("pdflatex main.tex")


if __name__ == "__main__":
    main()
