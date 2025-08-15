# Essay Agent

The essay agent writes essays and subsequently edits them based on feedback. It is built on top of Google's Gemini API. The writing part is based on Gemini's [Grounding with Google search](https://ai.google.dev/gemini-api/docs/google-search) native tool. Editing is enabled by a set of custom rewriting tools: rewrite paragraph, insert paragraph, delete paragraph, replace (text), and reply to comments. The documents are stored in an XML format that is meant as a mock Google Docs API. Example output documents can be found in /documents.


## How to run

1. Install `requirements.txt`
2. Create `tokens.py` in the root and insert your Gemini API key

```
GOOGLE_API_KEY = YOUR_KEY_HERE
```
3. Run one of the following commands:
```
python main.py --model gemini-2.5-pro --write "Your topic here"
```

```
python main.py --model gemini-2.0-flash-lite --review path/to/document.xml
```

While using the Free Tier Gemini API, one can easily encounter requests per minute (RPM) limits while using the `--review` command. 2.5 Pro [allows](https://ai.google.dev/gemini-api/docs/rate-limits#free-tier) 5 RPM, 2.5 Flash 10 RPM, 2.5 Flash-Lite 15 RPM, and 2.0 Flash-Lite 30 RPM. As the project uses the API's [automatic function calling](https://ai.google.dev/gemini-api/docs/function-calling?example=chart#automatic_function_calling_python_only), there is no straightforward way to limit the requests. (One very rudimentary way to circumvent this is to add breakpoints inside the tool functions and wait a while.)


## Document structure

The document structure is meant to mimic a structure of a Google Docs document. The top-level `document` tag has three subtags: `title`, `content`, and `comments`. The `title` tag is supposed to be the name of the Google Docs document. `content` contain the text separated into `p` paragraphs. Each paragraph has a `"n"` attribute with the number of the paragraph for editing by the model with tool calls. Inside paragraphs, there can `comment` tags, which serve as the comment highlight as in Google Docs. The actual remarks of the comments are stored in the tag `comments`, which is the final tag inside `document`. Inside the `comments` tag, there are individual `comment` tags. Those contain conversation exchanges between the `reviewer` and the `editor` (the model). The `comment` tags inside `content` and `comments` are paired using the `"n"` attribute.


## Future work

- actual Google Docs API
- testing and tuning prompts (costly)
- converting references to the required style, e.g. (Vaswani et al., 2017) (could be done with an existing services or using an LLM)
- custom tool for references that only uses academic sources
- use references while editing (Gemini API disallows custom tools combined with Grounding with Google search, however, they offer a more complex API that allows it; alternatively, create an agentic tool that uses the Gemini Grounding with Search to find information)
- more sophisticated writing, e.g., an agentic reviewer inside a loop with the writer and editor
- limit requests not to hit quotas
- potentially put less on the input to save costs
