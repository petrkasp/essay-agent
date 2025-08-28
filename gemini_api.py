"""Gemini API functions."""
from typing import List, Tuple, Callable
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import utils


load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)


class APIError(Exception):
    """Error for when the API gives unexpected results."""


# https://ai.google.dev/gemini-api/docs/google-search#attributing_sources_with_inline_citations
def add_citations(response) -> Tuple[str, List[str]]:
    """Generates a text with citations from a response from Gemini API if
    Grounding with Google search was used.

    Args:
        response: The response from Gemini API.

    Returns:
        1. Text with citations.
        2. List of uris used.
    """
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # Sort supports by end_index in descending order
    # to avoid shifting issues when inserting.
    sorted_supports = sorted(supports,
                             key=lambda s: s.segment.end_index,
                             reverse=True)

    for support in sorted_supports:
        # Note: There is an end_index field in the API response,
        # but is inconsistent with the text. This method seems robust.
        segment_text = support.segment.text
        end_index = text.index(segment_text) + len(segment_text)

        if support.grounding_chunk_indices:
            # Create citation string like [1](link1)[2](link2)
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    citation_links.append(f"[{i + 1}]")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    uris = [utils.find_redirects(chunk.web.uri) for chunk in chunks]
    text += "\n\n##Sources\n\n" + \
        "\n".join(f"[{i + 1}] {uri}" for i, uri in enumerate(uris))

    return text, uris


def with_search(model: str, prompt: str, system_prompt: str) -> str:
    """Makes a request to the given `model` with the
    `prompt` and `system_prompt`.

    Args:
        model: The Gemini model to request.
        prompt: The prompt to the model.
        system_prompt: The system prompt.

    Returns:
        The text of the response with citations added.
    """
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        system_instruction=system_prompt
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    if not response.text:
        raise APIError("Empty response from Gemini API. API likely down.")

    result, _ = add_citations(response)
    return result


def with_tools(model: str,
               prompt: str,
               system_prompt: str,
               tools: List[Callable]):
    """Makes a request to the given `model` with the
    `prompt`, `system_prompt`, and a list of `tools`.

    Args:
        model: The Gemini model to request.
        prompt: The prompt to the model.
        system_prompt: The system prompt.
        tools: List of tool functions.

    Returns:
        The `response` object from the API.
    """
    config = types.GenerateContentConfig(
        tools=[*tools],
        system_instruction=system_prompt
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    return response
