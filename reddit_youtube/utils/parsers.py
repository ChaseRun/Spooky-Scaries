import argparse


def import_story_args():
    parser = argparse.ArgumentParser(
        prog="import-stories",
        usage="%(prog)s [options]",
        description="",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default="",
    )
    # add single story
    parser.add_argument(
        "-r",
        "--reddit-ids",
        nargs="+",
        type=str,
        help="",
    )
    parser.add_argument(  # maybe add metavar='True / False'
        "-f", "--add-to-front", default=False, type=bool, help=""
    )
    # add multiple stories based on subreddit filters
    parser.add_argument(
        "-n", "--num-stories", default=0, type=int, help="asdasd"
    )
    parser.add_argument(
        "-s",
        "--sort-filter",
        choices=[
            "rising",
            "hot",
            "top",
            "new",
            "gilded",
            "controversial",
        ],
        type=str,
        help="",
    )
    parser.add_argument(
        "-t",
        "--time-filter",
        choices=["all", "day", "hour", "month", "week", "year"],
        type=str,
        help="",
    )
    # add stories from a specific author
    parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="",
    )
    # Misc
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_false",
        help="Enable output logs to " "the console",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")

    return validate_args(parser)


def validate_args(parser):
    filter_conflict = (
        "ERROR: Exactly one of the following sets must be provided:\n"
        "         --reddit-ids\n"
        "         --num-stories, --sort-filter, --time-filter, --author ("
        "optional)\n"
    )
    args = parser.parse_args()

    # Check for errors
    reddit_id_check = args.reddit_ids != ""
    num_check = args.num_stories != 0
    sort_check = args.sort_filter != ""
    time_check = args.time_filter != ""
    author_check = args.author != ""

    # Exactly one of reddit_id or filters
    if reddit_id_check:
        if num_check or sort_check or time_check or author_check:
            print(FILTER_CONFLICT_ERROR)
            exit(1)
    else:
        if not (num_check and sort_check and time_check):
            print(FILTER_CONFLICT_ERROR)
            exit(1)

    return args
