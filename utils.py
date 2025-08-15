import requests


def find_redirects(uri):
    try:
        response = requests.get(uri, allow_redirects=True)
        return response.history[0].headers["Location"]
    except:
        return uri
