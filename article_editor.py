"""Main functionalities."""
from typing import Tuple
import xml.etree.ElementTree as ET
from resources import WRITER_SYSTEM_PROMPT, create_reviewer_system_prompt
from gemini_api import with_search, with_tools
from google_docs_api_dummy import \
    create_document, create_revision, get_document
import tools_review


def write(model: str, prompt: str) -> str:
    """Writes an article using the given `model` and `prompt` and stores the
    article. Uses the `writer_system_prompt` from `resources.py`

    Args:
        model: The Gemini model to use.
        prompt: The prompt to the model.

    Returns:
        The ID of the new article.
    """
    document = with_search(model, prompt, WRITER_SYSTEM_PROMPT)
    xml = encode_content(document)
    document_id = create_document(xml)
    return document_id


def review(model: str, document_id: str, additional_user_request: str = None
           ) -> Tuple[str, str]:
    """Reviews and executes the edit requests in the given document.

    Args:
        model: The Gemini model to use.
        document_id: The ID of the document to revise.

    Returns:
        1. The ID of the newly generated revision.
        2. Text of the response.
    """
    document = get_document(document_id)
    xml = ET.fromstring(document)
    tools = tools_review.create_tools(xml)
    reviewer_system_prompt = \
        create_reviewer_system_prompt(additional_user_request)
    response = with_tools(model, document, reviewer_system_prompt, tools)
    new_document_id = create_revision(ET.ElementTree(xml), document_id)
    return new_document_id, response.text


def encode_content(content: str) -> ET.ElementTree:
    """Encodes the string document into an XML format.

    Args:
        content: The content of the document to encode.

    Returns:
        XML representation of the `content`.
    """
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
