"""Utility functions."""
import requests


def find_redirects(uri: str) -> str:
    """Given an uri, jumps through redirects and finds the target uri.
    This function is used because Gemini API returns all links redirected
    through their domains. The function sometimes fails to find the target uri.

    Args:
        uri: The uri for which to find the target site after redirects.

    Returns:
        The final destination of the uri.
    """
    try:
        response = requests.get(uri, allow_redirects=True, timeout=2.5)
        return response.history[0].headers["Location"]
    except requests.exceptions.RequestException:
        return uri
