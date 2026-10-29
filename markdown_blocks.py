import re

HEADING_RE = re.compile(r"^(#{1,6})\s+(\S.*)$")
SEPARATOR_CELL_RE = re.compile(r":?-{3,}:?")


def is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|")


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(line: str) -> bool:
    if not is_table_row(line):
        return False
    cells = split_cells(line)
    return bool(cells) and all(SEPARATOR_CELL_RE.fullmatch(cell) for cell in cells)


def parse_tables(text: str) -> list[dict]:
    lines = text.splitlines()
    title = ""
    tables = []
    index = 0
    while index < len(lines):
        heading = HEADING_RE.match(lines[index])
        if heading:
            title = heading.group(2).strip()
            index += 1
            continue
        if is_table_row(lines[index]) and index + 1 < len(lines) and is_separator_row(lines[index + 1]):
            raw = []
            while index < len(lines) and is_table_row(lines[index]):
                raw.append(lines[index])
                index += 1
            tables.append({
                "title": title,
                "headers": split_cells(raw[0]),
                "rows": [split_cells(line) for line in raw[2:]],
            })
            continue
        index += 1
    return tables


def chunk_markdown(text: str, max_chars: int = 1200) -> list[dict]:
    lines = text.splitlines()
    chunks = []
    heading_lines: dict[int, str] = {}
    prose: list[str] = []

    def heading_prefix() -> str:
        return "\n".join(heading_lines[level] for level in sorted(heading_lines))

    def emit(body: str, kind: str) -> None:
        prefix = heading_prefix()
        chunk = f"{prefix}\n\n{body}" if prefix else body
        chunks.append({"text": chunk.strip(), "kind": kind})

    def flush_prose() -> None:
        nonlocal prose
        body = "\n".join(prose).strip()
        prose = []
        if not body:
            return
        prefix = heading_prefix()
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
        current = ""
        for paragraph in paragraphs:
            pieces = [paragraph[start:start + max_chars] for start in range(0, len(paragraph), max_chars)] if len(paragraph) > max_chars else [paragraph]
            for piece in pieces:
                candidate = piece if not current else f"{current}\n\n{piece}"
                prefixed_len = len(candidate) + (len(prefix) + 2 if prefix else 0)
                if current and prefixed_len > max_chars:
                    emit(current, "text")
                    current = piece
                else:
                    current = candidate
        if current:
            emit(current, "text")

    index = 0
    while index < len(lines):
        heading = HEADING_RE.match(lines[index])
        if heading:
            flush_prose()
            level = len(heading.group(1))
            heading_lines[level] = lines[index].strip()
            heading_lines = {key: value for key, value in heading_lines.items() if key <= level}
            index += 1
            continue
        if is_table_row(lines[index]) and index + 1 < len(lines) and is_separator_row(lines[index + 1]):
            table_lines = []
            while index < len(lines) and is_table_row(lines[index]):
                table_lines.append(lines[index])
                index += 1
            table_body = "\n".join(table_lines)
            pending = "\n".join(prose).strip()
            prefix = heading_prefix()
            combined = f"{pending}\n\n{table_body}" if pending else table_body
            prefixed_len = len(combined) + (len(prefix) + 2 if prefix else 0)
            if pending and prefixed_len <= max_chars:
                prose = []
                emit(combined, "table")
            else:
                paragraphs = [part.strip() for part in re.split(r"\n\s*\n", pending) if part.strip()] if pending else []
                lead = paragraphs[-1] if paragraphs else ""
                flush_prose()
                emit(f"{lead}\n\n{table_body}" if lead else table_body, "table")
            continue
        prose.append(lines[index])
        index += 1
    flush_prose()
    return [chunk for chunk in chunks if chunk["text"]]
