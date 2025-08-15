import xml.etree.ElementTree as ET
from typing import List, Callable, Optional


def to_string(xml: ET.ElementTree) -> str:
    ET.indent(xml)
    return ET.tostring(xml, encoding="utf-8")


def get_paragraphs(xml: ET.ElementTree) -> List[ET.ElementTree]:
    return xml.findall("content/p")


def get_paragraph_with_number(xml: ET.ElementTree, paragraph_number: int=None) -> List[ET.Element]:
    if paragraph_number is None:
        selector = f"content/p"
    else:
        selector = f"content/p[@n='{paragraph_number}']"
    paragraphs = xml.findall(selector)
    if not paragraphs:
        raise ValueError(f"Invalid paragraph number: {paragraph_number}")
    return paragraphs


def find_index(parent: ET.Element, find: ET.Element) -> int:
    for i, elem in enumerate(parent):
        if elem is find:
            return i

    raise ValueError("index not found in XML element") 


def create_tools(xml: ET.Element) -> List[Callable]:
    def rewrite_paragraph(paragraph_number: int, new_text: str) -> str:
        """Rewrites the chosen paragraph with a new text.

        Args:
            paragraph_number: The number of the paragraph to rewrite.
            new_text: The new text of the paragraph.

        Returns:
            The new state of the entire document with chosen paragraph rewritten.
        """
        try:
            paragraph = get_paragraph_with_number(xml, paragraph_number)[0]
        except ValueError as e:
            return e.args[0]

        paragraph.text = new_text

        return to_string(xml)


    def insert_paragraph(insert_after_number: int, text: str) -> str:
        """Inserts a new paragraph after an existing paragraph.
        The new paragraph will assigned the number one higher than
        the largest paragraph number in the entire document.

        Args:
            insert_after_number: The number of the paragraph after
            which the new paragraph will be inserted.
            text: The text of the new paragraph.

        Returns:
            The new state of the entire document with the new paragraph inserted.
        """
        try:
            paragraph = get_paragraph_with_number(xml, insert_after_number)[0]
        except ValueError as e:
            return e.args[0]

        max_number = max(int(p.attrib["n"]) for p in get_paragraphs(xml))
        content_elem = xml.find("content")
        new_paragraph = ET.Element("p", {"n": str(max_number + 1)})
        new_paragraph.text = text
        content_elem.insert(find_index(content_elem, paragraph) + 1, new_paragraph)

        # We don't reorder the elements as not to confuse the model with changing paragraph numbers

        return to_string(xml)


    def delete_paragraph(paragraph_number: int) -> str:
        """Deletes the chosen paragraph. Following paragraph numbers won't be changed.

        Args:
            paragraph_number: The number of the paragraph to delete.

        Returns:
            The new state of the entire document with the chosen paragraph deleted.
        """
        try:
            paragraph = get_paragraph_with_number(xml, paragraph_number)[0]
        except ValueError as e:
            return e.args[0]

        content_elem = xml.find("content")
        content_elem.remove(paragraph)

        return to_string(xml)
    

    def replace(old: str, new: str, paragraph_number: Optional[int] = None) -> str:
        """String replace function. All occurrences of `old` are replaced with `new`.

        Args:
            old: The old string to be replaced.
            new: The new replacement string.
            paragraph_number: Optional parameter to limit the
            replacement to a chosen paragraph. If not provided,
            the replacement is applied over the entire document.

        Returns:
            The new state of the entire document with the string replace applied.
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
            The new state of the entire document with the reply added.
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
