from pathlib import Path
import xml.etree.ElementTree as ET
import re

document_folder = Path("documents")
ID_MAX_LENGTH = 14


def create_document(content: ET.ElementTree) -> str:
    check_folder()
    title = get_title(content)
    document_id = create_id(title)
    content.write(document_folder / document_id, encoding="utf-8")
    return document_id


def create_revision(new_content: ET.ElementTree, old_document_id: str) -> str:
    check_folder()
    new_document_id = create_revision_id(old_document_id)
    if (document_folder / old_document_id).exists():
        path = document_folder / new_document_id
    else:
        path = new_document_id
    new_content.write(path, encoding="utf-8")
    return new_document_id


def get_document(document_id: str) -> str:
    path = document_folder / document_id
    if not path.exists():
        path = document_id
    with path.open(encoding="utf-8") as f:
        return f.read()


def check_folder() -> None:
    if not document_folder.exists():
        document_folder.mkdir()


def get_title(xml: ET.ElementTree) -> str:
    return xml.find("title").text


def create_id(title: str) -> str:
    i = 1
    document_id = title[:ID_MAX_LENGTH] + ".xml"

    while (document_folder / document_id).exists():
        document_id = f"{title[:ID_MAX_LENGTH]}_{i}.xml"
        i += 1

    return document_id


def create_revision_id(old_id: str) -> str:
    match = re.findall(r"\.v(\d+)\.xml", old_id)
    if not match:
        id = old_id.removesuffix(".xml")
        return id + ".v2.xml"
    else:
        i = int(match[0])
        id = old_id.removesuffix(f".v{i}.xml")
        return id + f".v{i + 1}.xml"
