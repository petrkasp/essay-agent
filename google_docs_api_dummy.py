"""A mock Google Docs API."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re

document_folder = Path("documents")
ID_MAX_LENGTH = 14


def create_document(content: ET.ElementTree) -> str:
    """Creates a new document.

    Args:
        content: The content of the document in XML format.

    Returns:
        ID (path in the mock API) of the new document.
    """
    check_folder()
    title = get_title(content)
    document_id = create_id(title)
    content.write(document_folder / document_id, encoding="utf-8")
    return document_id


def create_revision(new_content: ET.ElementTree, old_document_id: str) -> str:
    """Creates a new document, which is a revision of an existing document.

    Args:
        new_content: The content of the new document in XML format.
        old_document_id: The ID of the revised document.

    Returns:
        ID of the new revision of a document.
    """
    check_folder()
    new_document_id = create_revision_id(old_document_id)
    if (document_folder / old_document_id).exists():
        path = document_folder / new_document_id
    else:
        path = new_document_id
    new_content.write(path, encoding="utf-8")
    return new_document_id


def get_document(document_id: str) -> str:
    """Loads a document from ID.

    Args:
        document_id: ID of the document to load.

    Returns:
        String representation of the document.
    """
    path = document_folder / document_id
    if not path.exists():
        path = document_id
    with path.open(encoding="utf-8") as f:
        return f.read()


def check_folder() -> None:
    """Makes sure the folder to store the documents exists.
    If not, creates it.
    """
    if not document_folder.exists():
        document_folder.mkdir()


def get_title(xml: ET.ElementTree) -> str:
    """Extracts the title from a document.

    Args:
        xml: XML representation of the document.

    Returns:
        The title of the document.
    """
    return xml.find("title").text


def create_id(title: str) -> str:
    """Generates a document ID based on a the title.
    Makes sure that it is unique and doesn't overwrite
    existing documents.

    Args:
        title: Title of the document. The ID is based on the title.

    Returns:
        The new unique ID of a document.
    """
    i = 1
    document_id = title[:ID_MAX_LENGTH] + ".xml"

    while (document_folder / document_id).exists():
        document_id = f"{title[:ID_MAX_LENGTH]}_{i}.xml"
        i += 1

    return document_id


def create_revision_id(old_id: str) -> str:
    """Generates a new ID for a revision based on an old ID.
    Doesn't guarantee uniqueness if the same document has been revised before.

    Args:
        old_id: The ID of the on which the revision is based.

    Returns:
        A new ID of a revision.
    """
    match = re.findall(r"\.v(\d+)\.xml", old_id)
    if not match:
        new_id = old_id.removesuffix(".xml")
        return new_id + ".v2.xml"
    else:
        i = int(match[0])
        new_id = old_id.removesuffix(f".v{i}.xml")
        return new_id + f".v{i + 1}.xml"
