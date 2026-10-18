#!/usr/bin/env python3
"""Redact the code docs a diff changed, in place, and report what was redacted.

Usage:
    git diff <base> | redact_polyglot.py --output-file <report> [file ...]

This is the multi-language counterpart to the Python `redact_changed_code_docs.py`
tool in the parent directory. It parses Java, Bash, and TypeScript with tree-sitter
and applies the same contract: it edits each selected file in place, redacting every
doc comment and inline comment the diff touched, and writes a report describing what
it redacted so a writer can compose fresh docs without seeing the original text.

- a touched doc comment is removed, and its enclosing signature is reported (a
  file-level doc reports the language's file-level sentinel instead), and
- a touched inline comment becomes the language's inline marker, keeping its
  position, and is reported inside a three-line context window.

Every other byte is preserved. A doc deletion that adds no new lines is neither
redacted nor reported. Files whose extension is not bound to a supported language
are skipped.
"""

import argparse
from dataclasses import dataclass
import re
import sys

from tree_sitter_language_pack import get_parser

HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
NEW_FILE_HEADER = re.compile(r"^\+\+\+ b/(.+)$")
CONTEXT = 3


@dataclass(frozen=True)
class Language:
    """The per-language binding table the shared engine runs against."""

    name: str
    parser_key: str
    extensions: tuple[str, ...]
    comment_kinds: tuple[str, ...]
    declaration_kinds: tuple[str, ...]
    body_kinds: tuple[str, ...]
    doc_prefix: str | None
    inline_marker: str
    doc_sentinel: str
    file_sentinel: str
    # Node kinds that wrap a declaration and should be treated as the signature
    # owner when a doc comment precedes them (for example a TypeScript
    # `export_statement` wrapping a `class_declaration`).
    wrapper_kinds: tuple[str, ...] = ()
    # Set for languages whose doc comment is a string statement (a Python
    # docstring) rather than a comment. When set, the engine classifies docs by
    # finding the first statement of a body rather than by comment prefix or run.
    docstring_kinds: tuple[str, ...] = ()
    # The report signature used for a module-level docstring, in place of the
    # file_sentinel used by comment-doc languages.
    module_sentinel: str | None = None
    # The statement that replaces a sole-statement docstring so its block stays
    # valid (Python `pass`).
    sole_placeholder: str | None = None


LANGUAGES: tuple[Language, ...] = (
    Language(
        name="java",
        parser_key="java",
        extensions=(".java",),
        comment_kinds=("line_comment", "block_comment"),
        declaration_kinds=(
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "record_declaration",
            "method_declaration",
            "constructor_declaration",
            "field_declaration",
        ),
        body_kinds=(
            "class_body",
            "block",
            "constructor_body",
            "interface_body",
            "enum_body",
        ),
        doc_prefix="/**",
        inline_marker="// inline comment redacted marker",
        doc_sentinel="// doc comment redacted",
        file_sentinel="// redacted file level comment",
    ),
    Language(
        name="bash",
        parser_key="bash",
        extensions=(".sh", ".bash"),
        comment_kinds=("comment",),
        declaration_kinds=("function_definition",),
        body_kinds=("compound_statement",),
        doc_prefix=None,
        inline_marker="# inline comment redacted marker",
        doc_sentinel="# doc comment redacted",
        file_sentinel="# redacted file level comment",
    ),
    Language(
        name="typescript",
        parser_key="typescript",
        extensions=(".ts",),
        comment_kinds=("comment",),
        declaration_kinds=(
            "class_declaration",
            "interface_declaration",
            "type_alias_declaration",
            "enum_declaration",
            "function_declaration",
            "method_definition",
            "lexical_declaration",
        ),
        body_kinds=("class_body", "statement_block", "enum_body", "interface_body"),
        doc_prefix="/**",
        inline_marker="// inline comment redacted marker",
        doc_sentinel="// doc comment redacted",
        file_sentinel="// redacted file level comment",
        wrapper_kinds=("export_statement",),
    ),
    Language(
        name="python",
        parser_key="python",
        extensions=(".py",),
        comment_kinds=("comment",),
        declaration_kinds=("class_definition", "function_definition"),
        body_kinds=("block",),
        doc_prefix=None,
        inline_marker="# inline comment redacted marker",
        doc_sentinel="# docstring redacted",
        file_sentinel="# redacted module level comment",
        docstring_kinds=("string",),
        module_sentinel="# redacted module level comment",
        sole_placeholder="pass",
    ),
)


def language_for(path: str) -> Language | None:
    """Return the Language bound to a file's extension, or None."""
    for language in LANGUAGES:
        if any(path.endswith(ext) for ext in language.extensions):
            return language
    return None


def split_diff_by_file(diff: str) -> dict[str, str]:
    """Return a map of new-side path to the slice of the diff for that path."""
    files: dict[str, list[str]] = {}
    current: list[str] | None = None

    for raw in diff.splitlines(keepends=True):
        if raw.startswith("diff --git "):
            current = None
        header = NEW_FILE_HEADER.match(raw.rstrip("\r\n"))
        if header:
            path = header.group(1)
            current = files.setdefault(path, [])
            continue
        if current is not None:
            current.append(raw)

    return {path: "".join(lines) for path, lines in files.items()}


def changed_new_lines(diff: str) -> set[int]:
    """Return the 1-based new-side line numbers that the diff adds or changes."""
    changed: set[int] = set()
    new_line = 0
    in_hunk = False

    for raw in diff.splitlines():
        header = HUNK_HEADER.match(raw)
        if header:
            new_line = int(header.group(1))
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if raw.startswith("+"):
            changed.add(new_line)
            new_line += 1
        elif raw.startswith("-"):
            continue
        elif raw.startswith(" "):
            new_line += 1
        else:
            in_hunk = False

    return changed


def resolve_paths(argv: list[str], per_file: dict[str, str]) -> list[str]:
    """Return the explicit file arguments, or every supported path the diff touched."""
    if argv:
        return argv
    return [path for path in per_file if language_for(path) is not None]


@dataclass(frozen=True)
class Comment:
    """A comment node reduced to the facts the engine needs."""

    start_row: int  # 1-based
    end_row: int  # 1-based, inclusive
    start_col: int  # 0-based column of the comment's first character
    text: str


@dataclass(frozen=True)
class DocComment:
    """A doc comment attached to a declaration or to the file."""

    start_row: int  # 1-based
    end_row: int  # 1-based, inclusive
    signature: str | None  # None for a file-level doc comment
    # True when the doc is the sole statement of its body, so deleting its rows
    # would leave an empty block. The redactor replaces it with a keep-valid
    # placeholder (Python `pass`) at the body's indentation instead of deleting.
    sole: bool = False
    # The 1-based row of the declaration this doc attaches to. For a docstring
    # this is the `def`/`class` line, which differs from `start_row` (the
    # docstring's own row); the report suppresses a signature already shown
    # inside a comment window, keyed on this row. Defaults to `start_row`.
    signature_row: int | None = None


def walk(node):
    """Yield every node in the tree, parents before children."""
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(reversed(current.children))


def is_shebang(comment_text: str, start_row: int) -> bool:
    """Return whether a comment is a shebang line, which is never a code doc."""
    return start_row == 1 and comment_text.startswith("#!")


def node_comment(node) -> Comment:
    """Return the Comment view of a tree-sitter comment node."""
    return Comment(
        start_row=node.start_point[0] + 1,
        end_row=node.end_point[0] + 1,
        start_col=node.start_point[1],
        text=node.text.decode("utf-8", "replace"),
    )


def body_child(node, body_kinds: tuple[str, ...]):
    """Return the node's body, searching descendants, or None when it has none.

    Searching descendants lets a wrapper node (a TypeScript `export_statement`)
    resolve the body of the declaration it wraps. The first body-kind node in
    document order wins.
    """
    stack = list(node.children)
    while stack:
        candidate = stack.pop(0)
        if candidate.type in body_kinds:
            return candidate
        stack[:0] = candidate.children
    return None


COMMENT_NODE_KINDS = ("comment", "line_comment", "block_comment")
REMOVED = b"\x00"  # placeholder for a removed comment while lines are rebuilt


def strip_comments(node, source_bytes: bytes, start: int, end: int) -> str:
    """Return source bytes `start..end` with every comment inside removed.

    A report must never copy a raw source span that can hold original comment
    text. A line left empty by removing a comment is dropped, and a trailing
    comment leaves no trailing whitespace.
    """
    spans = sorted(
        (n.start_byte, n.end_byte)
        for n in walk(node)
        if n.type in COMMENT_NODE_KINDS and n.start_byte >= start and n.end_byte <= end
    )
    pieces: list[bytes] = []
    cursor = start
    for comment_start, comment_end in spans:
        pieces.append(source_bytes[cursor:comment_start])
        pieces.append(REMOVED)
        cursor = comment_end
    pieces.append(source_bytes[cursor:end])
    lines = b"".join(pieces).decode("utf-8", "replace").split("\n")
    kept: list[str] = []
    for line in lines:
        text = line.replace(REMOVED.decode(), "").rstrip()
        if REMOVED.decode() in line and not text.strip():
            continue
        kept.append(text)
    return "\n".join(kept)


def signature_text(node, source_bytes: bytes, body_kinds: tuple[str, ...]) -> str:
    """Return a declaration's signature: from its line start up to the body.

    The signature keeps the declaration's own indentation and covers everything
    before the body, so a body opening on the declaration's last line is excluded.
    A declaration with no body kind falls back to its whole span; comments inside
    the signature span are always stripped, so no original comment can leak.
    """
    body = body_child(node, body_kinds)
    line_start = source_bytes.rfind(b"\n", 0, node.start_byte) + 1
    end_byte = body.start_byte if body is not None else node.end_byte
    scope = node
    if source_bytes[line_start : node.start_byte].strip():
        # Text precedes the declaration on its line (a same-line comment).
        while scope.parent is not None:
            scope = scope.parent
    return strip_comments(scope, source_bytes, line_start, end_byte).rstrip()


def declaration_owner(node, language: Language):
    """Return the node whose signature represents a declaration.

    A declaration wrapped by a wrapper node (a TypeScript `export_statement`) is
    represented by the wrapper, so the reported signature keeps the `export`.
    """
    parent = node.parent
    if parent is not None and parent.type in language.wrapper_kinds:
        return parent
    return node


def preceding_declaration(comment_node, language: Language):
    """Return the declaration a doc comment attaches to, or None.

    A doc comment attaches to the next sibling declaration (or a wrapper around
    one) that immediately follows the comment's run of doc comments.
    """
    sibling = comment_node.next_named_sibling
    while sibling is not None and sibling.type in language.comment_kinds:
        sibling = sibling.next_named_sibling
    if sibling is None:
        return None
    if sibling.type in language.declaration_kinds:
        return sibling
    if sibling.type in language.wrapper_kinds:
        for child in sibling.children:
            if child.type in language.declaration_kinds:
                return sibling
    return None


def classify_prefixed(
    root, source_bytes: bytes, language: Language
) -> tuple[list[Comment], list[DocComment]]:
    """Classify comments for a language whose doc comments open with a prefix.

    A comment whose text opens with the language's doc prefix and which precedes
    a declaration is a doc comment; every other comment is inline.
    """
    inline: list[Comment] = []
    docs: list[DocComment] = []

    for node in walk(root):
        if node.type not in language.comment_kinds:
            continue
        comment = node_comment(node)
        opens_doc = comment.text.startswith(language.doc_prefix)
        declaration = preceding_declaration(node, language) if opens_doc else None
        if opens_doc and declaration is not None:
            owner = declaration_owner_from(declaration, language)
            docs.append(
                DocComment(
                    start_row=comment.start_row,
                    end_row=comment.end_row,
                    signature=signature_text(
                        owner, source_bytes, language.body_kinds
                    ),
                )
            )
        elif opens_doc and is_file_level(node, language):
            docs.append(
                DocComment(
                    start_row=comment.start_row,
                    end_row=comment.end_row,
                    signature=None,
                )
            )
        else:
            inline.append(comment)

    return inline, docs


def declaration_owner_from(declaration, language: Language):
    """Return the signature owner for a resolved declaration node.

    `preceding_declaration` returns a wrapper node directly when the declaration
    is wrapped; otherwise it returns the declaration, which may still be wrapped.
    """
    if declaration.type in language.wrapper_kinds:
        return declaration
    return declaration_owner(declaration, language)


def is_file_level(comment_node, language: Language) -> bool:
    """Return whether a root-level doc comment precedes the first declaration."""
    if comment_node.parent is None or comment_node.parent.type != "program":
        return False
    for sibling in comment_node.parent.children:
        if sibling.type in language.declaration_kinds + language.wrapper_kinds:
            return comment_node.start_byte < sibling.start_byte
    return False


def classify_run_based(
    root, source_bytes: bytes, language: Language
) -> tuple[list[Comment], list[DocComment]]:
    """Classify comments for a language whose doc comments are runs of comments.

    A contiguous run of comment lines immediately above a function is that
    function's doc comment; the leading run below any shebang is the file's doc
    comment; every other comment is inline.
    """
    comment_nodes = [
        node for node in root.children if node.type in language.comment_kinds
    ]
    shebang = {
        node.start_byte
        for node in comment_nodes
        if is_shebang(node.text.decode("utf-8", "replace"), node.start_point[0] + 1)
    }

    doc_bytes: set[int] = set()
    docs: list[DocComment] = []

    for declaration in root.children:
        if declaration.type not in language.declaration_kinds:
            continue
        run = leading_comment_run(declaration, language, shebang)
        if run:
            doc_bytes.update(node.start_byte for node in run)
            docs.append(
                DocComment(
                    start_row=run[0].start_point[0] + 1,
                    end_row=run[-1].end_point[0] + 1,
                    signature=signature_text(
                        declaration, source_bytes, language.body_kinds
                    ),
                )
            )

    file_run = file_comment_run(root, language, shebang, doc_bytes)
    if file_run:
        doc_bytes.update(node.start_byte for node in file_run)
        docs.append(
            DocComment(
                start_row=file_run[0].start_point[0] + 1,
                end_row=file_run[-1].end_point[0] + 1,
                signature=None,
            )
        )

    inline = [
        node_comment(node)
        for node in walk(root)
        if node.type in language.comment_kinds
        and node.start_byte not in doc_bytes
        and node.start_byte not in shebang
    ]
    return inline, docs


def first_statement(body, docstring_kinds: tuple[str, ...]):
    """Return `(node, is_string_doc)` for a body's first statement.

    A docstring is the first named child that carries code, ignoring comments.
    `is_string_doc` is True when that statement is a docstring string node.
    """
    for child in body.named_children:
        if child.type == "comment":
            continue
        return child, child.type in docstring_kinds
    return None, False


def statement_count(body) -> int:
    """Return the number of code statements in a body, ignoring comments."""
    return sum(1 for child in body.named_children if child.type != "comment")


def docstring_node(container, language: Language):
    """Return a container's docstring string node, or None.

    The container is the module root or a declaration. Its body is the module
    itself or the declaration's `block`; the docstring is that body's first
    statement when the statement is a string.
    """
    if container.type == "module":
        body = container
    else:
        body = body_child(container, language.body_kinds)
    if body is None:
        return None
    statement, is_doc = first_statement(body, language.docstring_kinds)
    if statement is None or not is_doc:
        return None
    return statement


def classify_python(
    root, source_bytes: bytes, language: Language
) -> tuple[list[Comment], list[DocComment]]:
    """Classify docs for Python, whose docs are docstring string statements.

    A module, class, or function whose body opens with a string statement has a
    docstring. A docstring that is its body's only statement is `sole`, so the
    redactor keeps the block valid. Every `#` comment is inline.
    """
    docs: list[DocComment] = []

    module_doc = docstring_node(root, language)
    if module_doc is not None:
        docs.append(
            DocComment(
                start_row=module_doc.start_point[0] + 1,
                end_row=module_doc.end_point[0] + 1,
                signature=None,
                sole=False,
            )
        )

    for node in walk(root):
        if node.type not in language.declaration_kinds:
            continue
        doc = docstring_node(node, language)
        if doc is None:
            continue
        body = body_child(node, language.body_kinds)
        docs.append(
            DocComment(
                start_row=doc.start_point[0] + 1,
                end_row=doc.end_point[0] + 1,
                signature=signature_text(node, source_bytes, language.body_kinds),
                sole=statement_count(body) == 1,
                signature_row=node.start_point[0] + 1,
            )
        )

    inline = [
        node_comment(node)
        for node in walk(root)
        if node.type in language.comment_kinds
        and not is_shebang(node.text.decode("utf-8", "replace"), node.start_point[0] + 1)
    ]
    return inline, docs


def leading_comment_run(declaration, language: Language, shebang: set[int]) -> list:
    """Return the contiguous comment nodes immediately above a declaration."""
    run: list = []
    sibling = declaration.prev_named_sibling
    expected_row = declaration.start_point[0]
    while (
        sibling is not None
        and sibling.type in language.comment_kinds
        and sibling.start_byte not in shebang
        and sibling.end_point[0] == expected_row - 1
    ):
        run.insert(0, sibling)
        expected_row = sibling.start_point[0]
        sibling = sibling.prev_named_sibling
    return run


def file_comment_run(
    root, language: Language, shebang: set[int], claimed: set[int]
) -> list:
    """Return the leading comment run at the top of the file below any shebang."""
    run: list = []
    expected_row = 1 if not shebang else None
    for node in root.children:
        if node.type not in language.comment_kinds:
            break
        if node.start_byte in shebang:
            expected_row = node.end_point[0] + 1
            continue
        if node.start_byte in claimed:
            break
        if expected_row is not None and node.start_point[0] != expected_row:
            break
        run.append(node)
        expected_row = node.end_point[0] + 1
    return run


def classify(
    root, source_bytes: bytes, language: Language
) -> tuple[list[Comment], list[DocComment]]:
    """Split a file's comments into inline comments and doc comments."""
    if language.docstring_kinds:
        return classify_python(root, source_bytes, language)
    if language.doc_prefix is not None:
        return classify_prefixed(root, source_bytes, language)
    return classify_run_based(root, source_bytes, language)


def indentation(line: str) -> str:
    """Return the leading whitespace of a line."""
    return line[: len(line) - len(line.lstrip())]


def redact_line(line: str, column: int, marker: str) -> str:
    """Replace the comment starting at column with the marker, keeping position."""
    newline = line[len(line.rstrip("\r\n")) :]
    prefix = line[:column]
    if prefix.strip() == "":
        return f"{prefix}{marker}{newline}"
    return f"{prefix.rstrip()} {marker}{newline}"


def widen_block_comments(inline: list[Comment], changed: set[int]) -> set[int]:
    """Return `changed` plus every row of a touched multi-line `/* */` comment.

    Redacting only some lines of a block comment would leave a dangling
    delimiter (for example a bare `*/`), so a touched block comment is redacted
    whole, one inline marker per physical line.
    """
    widened = set(changed)
    for comment in inline:
        if (
            comment.text.startswith("/*")
            and comment.end_row > comment.start_row
            and touched(comment.start_row, comment.end_row, changed)
        ):
            widened.update(range(comment.start_row, comment.end_row + 1))
    return widened


def touched(start_row: int, end_row: int, changed: set[int]) -> bool:
    """Return whether any row in an inclusive range is a changed line."""
    return any(row in changed for row in range(start_row, end_row + 1))


def redact_source(
    source_lines: list[str],
    docs: list[DocComment],
    changed_comments: list[Comment],
    changed: set[int],
    language: Language,
) -> str:
    """Return the source with touched docs removed and touched comments redacted.

    A comment is redacted line by line: only the physical lines the diff changed
    become the marker, so an untouched line of a multi-line block comment stays
    verbatim. The first line uses the comment's start column; a continuation line
    uses its own indentation.
    """
    lines = list(source_lines)

    for comment in changed_comments:
        for row in range(comment.start_row, comment.end_row + 1):
            if row not in changed:
                continue
            column = (
                comment.start_col
                if row == comment.start_row
                else len(indentation(lines[row - 1]))
            )
            lines[row - 1] = redact_line(lines[row - 1], column, language.inline_marker)

    for doc in sorted(docs, key=lambda d: d.start_row, reverse=True):
        if doc.sole and language.sole_placeholder is not None:
            indent = indentation(lines[doc.start_row - 1])
            newline = lines[doc.end_row - 1][
                len(lines[doc.end_row - 1].rstrip("\r\n")) :
            ] or "\n"
            lines[doc.start_row - 1 : doc.end_row] = [
                f"{indent}{language.sole_placeholder}{newline}"
            ]
        else:
            del lines[doc.start_row - 1 : doc.end_row]

    return "".join(lines)


def comment_blocks(comments: list[Comment]) -> list[list[Comment]]:
    """Group comments into blocks whose lines are consecutive."""
    ordered = sorted(comments, key=lambda c: c.start_row)
    blocks: list[list[Comment]] = []
    for comment in ordered:
        if blocks and comment.start_row == blocks[-1][-1].end_row + 1:
            blocks[-1].append(comment)
        else:
            blocks.append([comment])
    return blocks


def comment_window(
    start: int,
    end: int,
    touched_comments: list[Comment],
    changed: set[int],
    source_lines: list[str],
    docs: list[DocComment],
    language: Language,
) -> str:
    """Return the report text for rows `start..end` of the source.

    Every touched comment inside the window renders as the marker, whichever
    comment block it belongs to, and a doc comment inside the window collapses
    to a single sentinel line, so the window never reveals original comment or
    doc text.
    """
    changed_starts = {
        row: (
            comment.start_col
            if row == comment.start_row
            else len(indentation(source_lines[row - 1]))
        )
        for comment in touched_comments
        for row in range(comment.start_row, comment.end_row + 1)
        if row in changed
    }
    doc_starts = {doc.start_row for doc in docs}
    doc_continuations = {
        row for doc in docs for row in range(doc.start_row + 1, doc.end_row + 1)
    }

    rendered: list[str] = []
    for row in range(start, end + 1):
        line = source_lines[row - 1]
        if row in doc_continuations:
            continue
        if row in doc_starts:
            rendered.append(f"{indentation(line)}{language.doc_sentinel}\n")
        elif row in changed_starts:
            column = changed_starts[row]
            rendered.append(redact_line(line, column, language.inline_marker))
        else:
            rendered.append(line)

    return "".join(rendered).rstrip("\n")


def merge_windows(blocks: list[list[Comment]], line_count: int) -> list[tuple[int, int]]:
    """Return the `(start, end)` context range of each touched block, merged.

    Ranges that overlap or touch merge into one, so no source row is printed
    twice and a row is always rendered with every touched comment known.
    """
    merged: list[tuple[int, int]] = []
    for block in blocks:
        start = max(1, block[0].start_row - CONTEXT)
        end = min(line_count, block[-1].end_row + CONTEXT)
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def build_report(
    source_lines: list[str],
    docs: list[DocComment],
    inline: list[Comment],
    changed: set[int],
    language: Language,
) -> list[str]:
    """Return report blocks: comment windows, then signatures outside any window.

    Consecutive inline comments form one block, which sets the window bounds; a
    block is reported when any of its comments is touched. Untouched neighbor
    comments widen the window and render verbatim, but every touched comment in
    a window renders as the marker, even one from a different block.
    """
    touched_blocks = [
        block
        for block in comment_blocks(inline)
        if any(touched(c.start_row, c.end_row, changed) for c in block)
    ]
    touched_comments = [
        c for c in inline if touched(c.start_row, c.end_row, changed)
    ]
    ranges = merge_windows(touched_blocks, len(source_lines))
    report = [
        comment_window(
            start, end, touched_comments, changed, source_lines, docs, language
        )
        for start, end in ranges
    ]

    for doc in docs:
        if not touched(doc.start_row, doc.end_row, changed):
            continue
        anchor = doc.signature_row if doc.signature_row is not None else doc.start_row
        if any(start <= anchor <= end for start, end in ranges):
            continue
        report.append(
            doc.signature if doc.signature is not None else language.file_sentinel
        )

    return report


def process_file(path: str, file_diff: str, language: Language) -> list[str]:
    """Redact the file in place and return its report blocks."""
    changed = changed_new_lines(file_diff)
    if not changed:
        return []

    with open(path, encoding="utf-8") as handle:
        source = handle.read()

    source_lines = source.splitlines(keepends=True)
    source_bytes = source.encode("utf-8")
    parser = get_parser(language.parser_key)
    root = parser.parse(source_bytes).root_node

    inline, docs = classify(root, source_bytes, language)
    changed = widen_block_comments(inline, changed)

    changed_comments = [
        comment
        for comment in inline
        if touched(comment.start_row, comment.end_row, changed)
    ]
    changed_docs = [doc for doc in docs if touched(doc.start_row, doc.end_row, changed)]

    report = build_report(source_lines, docs, inline, changed, language)

    redacted = redact_source(
        source_lines, changed_docs, changed_comments, changed, language
    )
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(redacted)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Redact the code docs a diff changed and report what was redacted."
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="path to write the redaction report to",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="files to redact; omit to redact every supported file the diff touches",
    )
    args = parser.parse_args()

    diff = sys.stdin.read()
    per_file = split_diff_by_file(diff)
    paths = resolve_paths(args.files, per_file)

    status = 0
    file_sections: list[str] = []
    for path in paths:
        language = language_for(path)
        if language is None:
            continue
        try:
            blocks = process_file(path, per_file.get(path, ""), language)
        except OSError as error:
            print(f"error: could not access {path}: {error}", file=sys.stderr)
            status = 1
            continue
        if blocks:
            file_sections.append("\n\n".join([f"# {path}", *blocks]))

    with open(args.output_file, "w", encoding="utf-8") as handle:
        handle.write("\n\n".join(file_sections))
        if file_sections:
            handle.write("\n")

    return status


if __name__ == "__main__":
    sys.exit(main())
