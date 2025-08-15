from resources import writer_system_prompt, reviewer_system_prompt
from gemini_api import with_search, with_tools
from google_docs_api_dummy import create_document, create_revision, get_document
import tools_review
import xml.etree.ElementTree as ET
from typing import Tuple


def write(model: str, prompt: str) -> str:
    document = with_search(model, prompt, writer_system_prompt)
    xml = encode_content(document)
    document_id = create_document(xml)
    return document_id


def review(model: str, document_id: str) -> str:
    document = get_document(document_id)
    xml = ET.fromstring(document)
    tools = tools_review.create_tools(xml)
    with_tools(model, document, reviewer_system_prompt, tools)
    new_document_id = create_revision(ET.ElementTree(xml), document_id)
    return new_document_id


def encode_content(content: str) -> Tuple[str, ET.ElementTree]:
    paragraphs = content.split("\n\n")
    title = paragraphs[0].replace("#", "").strip()

    document_elem = ET.Element("document")
    ET.SubElement(document_elem, "title").text = title
    content_elem = ET.SubElement(document_elem, "content")
    ET.SubElement(document_elem, "comments")

    for i, paragraph in enumerate(paragraphs):
        ET.SubElement(content_elem, "p", {"n": str(i + 1)}).text = paragraph

    document = ET.ElementTree(document_elem)
    ET.indent(document)
    return document
