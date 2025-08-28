"""Tools to be used by the model."""
import xml.etree.ElementTree as ET
from typing import List, Callable, Optional


def to_string(xml: ET.Element) -> str:
    """Converts the `xml` into a pretty string.

    Args:
        xml: The XML to convert to string.

    Returns:
        A string representation of the XML.
    """
    ET.indent(xml)
    return ET.tostring(xml, encoding="utf-8")


def get_paragraphs(xml: ET.Element) -> List[ET.Element]:
    """Gets all paragraph in `xml`.
    The `xml` is expected to have the Google Docs format described
    in README.md and showcased in `/documents`.

    Args:
        xml: The XML in which to get the paragraphs.

    Returns:
        A list of all paragraphs.
    """
    return xml.findall("content/p")


def get_paragraph_with_number(xml: ET.Element,
                              paragraph_number: int = None
                              ) -> List[ET.Element]:
    """Finds the paragraph with the given paragraph number.
    If no paragraph number is given, returns all paragraphs.
    If no paragraph matches the number, raises a ValueError.
    The `xml` is expected to have the Google Docs format described
    in README.md and showcased in `/documents`.

    Args:
        xml: The XML in which to get the paragraphs.
        paragraph_number: The number of the paragraph.

    Returns:
        Either a list of all paragraphs, or a list containing the
        paragraph with the requested number.
    """
    if paragraph_number is None:
        selector = "content/p"
    else:
        selector = f"content/p[@n='{paragraph_number}']"
    paragraphs = xml.findall(selector)
    if not paragraphs:
        raise ValueError(f"Invalid paragraph number: {paragraph_number}")
    return paragraphs


def find_index(parent: ET.Element, target: ET.Element) -> int:
    """Find the 0-starting index of the given element in the parent element.
    If not found, raises a `ValueError`.

    Args:
        parent: The element in which to search.
        target: The element to look for.

    Returns:
        The index of the `target` element inside the `parent` element.
    """
    for i, elem in enumerate(parent):
        if elem is target:
            return i

    raise ValueError("index not found in XML element")


#                                                                       #
# NOTE: The docstrings as they are typed here for the functions created #
#       by `create_tools` are part of the system prompt for the LLM     #
#                                                                       #
def create_tools(xml: ET.Element) -> List[Callable]:
    """Creates a closure with the document context for tools used by the model
    to edit documents.

    Note that the docstring for the below functions are passed to the model
    as they are written in this `.py`.

    Args:
        xml: The document to be edited by the model.

    Returns:
        List of functions to be passed to the model.
    """
    def rewrite_paragraph(paragraph_number: int, new_text: str) -> str:
        """Rewrites the chosen paragraph with a new text.

        Args:
            paragraph_number: The number of the paragraph to rewrite.
            new_text: The new text of the paragraph.

        Returns:
            The text of the entire document
            with the chosen paragraph rewritten.
        """
        try:
            paragraph = get_paragraph_with_number(xml, paragraph_number)[0]
        except ValueError as e:
            return e.args[0]

        paragraph.text = new_text

        return to_string(xml)

    def insert_paragraph(prev_para_index: int, text: str) -> str:
        """Inserts a new paragraph after an existing paragraph.
        The new paragraph will assigned the number one higher than
        the largest paragraph number in the entire document.

        Args:
            prev_para_index: The number of the paragraph after
            which the new paragraph will be inserted.
            text: The text of the new paragraph.

        Returns:
            The text of the entire document with the new paragraph inserted.
        """
        try:
            paragraph = get_paragraph_with_number(xml, prev_para_index)[0]
        except ValueError as e:
            return e.args[0]

        max_number = max(int(p.attrib["n"]) for p in get_paragraphs(xml))
        content_elem = xml.find("content")
        new_paragraph = ET.Element("p", {"n": str(max_number + 1)})
        new_paragraph.text = text
        content_elem.insert(
            find_index(content_elem, paragraph) + 1, new_paragraph
            )

        # We don't reorder the elements as not to confuse the model
        # with changing paragraph numbers.

        return to_string(xml)

    def delete_paragraph(paragraph_number: int) -> str:
        """Deletes the chosen paragraph.
        Following paragraph numbers won't be changed.

        Args:
            paragraph_number: The number of the paragraph to delete.

        Returns:
            The text of the entire document with the chosen paragraph deleted.
        """
        try:
            paragraph = get_paragraph_with_number(xml, paragraph_number)[0]
        except ValueError as e:
            return e.args[0]

        content_elem = xml.find("content")
        content_elem.remove(paragraph)

        return to_string(xml)

    def replace(old: str,
                new: str,
                paragraph_number: Optional[int] = None
                ) -> str:
        """String replace function.
        All occurrences of `old` are replaced with `new`.

        Args:
            old: The old string to be replaced.
            new: The new replacement string.
            paragraph_number: Optional parameter to limit the
            replacement to a chosen paragraph. If not provided,
            the replacement is applied over the entire document.

        Returns:
            The text of the entire document with the string replaced.
        """
        try:
            paragraphs = get_paragraph_with_number(xml, paragraph_number)
        except ValueError as e:
            return e.args[0]

        change_made = False
        for paragraph in paragraphs:
            new_text = paragraph.text.replace(old, new)
            if new_text != paragraph.text:
                change_made = True
            paragraph.text = new_text

        if not change_made:
            return "Replace made no changes."

        return to_string(xml)

    def reply(comment_number: int, text: str) -> str:
        """Adds a reply to the chosen comment. Use either to comment
        the completion of the task or ask a clarifying question.

        Args:
            comment_number: The number of the comment to reply to.
            text: The text of the reply.

        Returns:
            The comments with the reply added.
        """
        comment = xml.find(f"comments/comment[@n='{comment_number}']")
        new_remark = ET.SubElement(comment, "editor")
        new_remark.text = text

        return to_string(xml)

    return [rewrite_paragraph,
            insert_paragraph,
            delete_paragraph,
            replace,
            reply
            ]
