"""Main entrypoint."""
import argparse
from article_editor import write, review


def create_parser() -> argparse.ArgumentParser:
    """Creates an argparse parser for the `main` function.

    Returns:
        The parser for `main`.
    """
    parser = argparse.ArgumentParser(
        description="Essay agent that can write articles and address " +
        "proposed edits in them."
    )
    subparsers = parser.add_subparsers(
        dest="command"
    )
    subparsers.required = True

    model_argument_help_string = "The name of the main model to use. " + \
        "Current Google models are:\n" + \
        "gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite"

    write_parser = subparsers.add_parser(
        "write",
        help="Writes an article about the given topic."
    )
    write_parser.add_argument(
        "--prompt", type=str, required=True,
        help="Prompt to the model that should include the topic and " +
        "optionally additional instructions like the desired word count."
    )
    write_parser.add_argument(
        "--model", type=str, default="gemini-2.5-pro",
        help=model_argument_help_string
    )

    review_parser = subparsers.add_parser(
        "review",
        help="Review and address the comments in the given document."
    )
    review_parser.add_argument(
        "--document_id", type=str, required=True,
        help="ID of the document to review."
    )
    review_parser.add_argument(
        "--prompt", type=str,
        help="Optional prompt with additional instructions, like to only " +
        "address a specific single comment."
    )
    review_parser.add_argument(
        "--model", type=str, default="gemini-2.5-flash",
        help=model_argument_help_string + "\n" +
        "gemini-2.0-flash-lite has the highest requests per minute quota in " +
        "the Gemini free tier and is thus most likely to complete the task " +
        "without exceeding the limit."
    )

    return parser


def main(args: argparse.Namespace) -> None:
    """The main entrypoint of the project.

    Args:
        args: Arguments parsed by argparse.
    """
    if args.command == "write":
        document_id = write(args.model, args.prompt)
        print(f"Document saved as {document_id}")
    elif args.command == "review":
        new_document_id, response = \
            review(args.model, args.document_id, args.prompt)
        print(response)
        print(f"Revision saved as {new_document_id}")
    else:
        assert False, "Unreachable path reached. Bad command selection. " + \
                      "Should have been handled by argparse."


if __name__ == "__main__":
    main(
        create_parser()
        .parse_args()
    )
