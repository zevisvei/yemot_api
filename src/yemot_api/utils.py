def split_content(content: str) -> list[str]:
    all_parts = []
    start = 0
    chunk_size = 2000
    while len(content) - start > chunk_size:
        part = content[start:content.rfind("\n", start, start + chunk_size)]
        all_parts.append(part.strip())
        start += len(part)
    all_parts.append(content[start:].strip())
    return all_parts
