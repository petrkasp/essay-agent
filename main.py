from article_editor import write, review

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--model", type=str, default="gemini-2.5-flash",
    help="The name of the main model the use. Current Google models are: " + \
         "gemini-2.5-pro, gemini-2.5-flash, and gemini-2.5-flash-lite \n" + \
         "gemini-2.0-flash-lite has the highest requests per minute quota " + \
         "in the Gemini free tier and is thus most likely to complete the " + \
         "task without exceeding the limit.")
parser.add_argument("--write", type=str, help="Writes an article about the given topic.")
parser.add_argument("--review", type=str,
    help="Review and address the comments in the given document. Give the document id.")


def main(args):
    if args.write and args.review:
        raise ValueError(
            "Can't --write and --review at the same time. " + \
            "Use only one at a time. Use --help for more information."
        )

    if args.write:
        document_id = write(args.model, args.write)
        print(f"Document saved as {document_id}")
    elif args.review:
        review(args.model, args.review)
    else:
        raise ValueError(
            "No action was selected. Use either --write or --review. Use --help for more information."
        )


if __name__ == "__main__":
    main(parser.parse_args())
