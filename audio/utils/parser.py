import argparse


def get_args():
    parser = argparse.ArgumentParser(
        prog="generate-audio",
        usage="%(prog)s [options]",
        description="",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default="",
    )
    parser.add_argument(
        "-v",
        "--voice",
        default="geralt",
        type=str,
        help="",
    )
    parser.add_argument(
        "-p",
        "--preset",
        default="standard",
        type=str,
        help="",
    )
    parser.add_argument(
        "-r",
        "--reddit-id",
        type=str,
        help="",
    )

    parser.add_argument(
        "--verbose",
        action="store_false",
        help="Enable output logs to " "the console",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")

    args = parser.parse_args()
    return args.voice, args.preset, args.reddit_id, args.verbose
