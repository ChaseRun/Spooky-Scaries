import argparse


def main_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        prog="spookystories",
        usage="%(prog)s [options]",
        description="A package that automatically generated YouTube videos "
                    "based on Reddit r/nosleep stories.",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Make the output more verbose",
    )
    parser.add_argument(
        "-V",
        "--version",
        help="Show version number and quit",
    )
    subparsers = parser.add_subparsers(title='subcommands',
                                       help='additional help')

    add_import_parser(parser)
    add_generate_parser(parser)

    return validate_args(parser)

def add_import_parser(main_parser):
    import_parser = main_parser.add_parser(
        prog="import",
        usage="%(prog)s [options]",
        description="Import Reddit r/nosleep stories into the database",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    # add single story
    import_parser.add_argument(
        "-r",
        "--reddit-ids",
        nargs="+",
        type=str,
        help="Import a single story or a list of stories using their Reddit ID",
    )
    import_parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Import a single story based on using it's url"
    )
    import_parser.add_argument(
        "-p",
        "--prioritize",
        default=False,
        type=bool,
        help="Prioritize the stories being imported by adding them to the "
             "\"front\" of the database."
    )
    # add multiple stories based on subreddit filters
    import_parser.add_argument(
        "-n",
        "--num-stories",
        default=0,
        type=int,
        help="Import X number of stories based on the sorting filters\nIf "
             "used, must also include --sort-filter and --time-filter"
    )
    import_parser.add_argument(
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
        help="Search for stories using a filter\nIf used, must also "
             "include --num-stories and --time-filter",
    )
    import_parser.add_argument(
        "-t",
        "--time-filter",
        choices=["all", "day", "hour", "month", "week", "year"],
        type=str,
        help="Specify the time period to search for stories.\nIf used, "
             "must also include --num-stories and --sort-filter",
    )
    # add stories from a specific author
    import_parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="Search for stories by their author.\nIf used, must also include "
             "--num-stories, --sort-filter, and --time-filter",
    )



# - specific: reddit_id (List)
    #  - if not in DB, run import
    # top X most relevant stories
    # generate videos for series, schedule posts
    # date to upload
    # all other story's will
def add_generate_parser(main_parser):
    generate_parser = main_parser.add_parser(
        prog="generate",
        usage="%(prog)s [options]",
        description="Generates and uploads story video(s) to YouTube.\n",
        epilog="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        argument_default=argparse.SUPPRESS,
    )
    # add single story
    import_parser.add_argument(
        "-r",
        "--reddit-ids",
        nargs="+",
        type=str,
        help="Generate single story or a list of stories using their Reddit ID",
    )


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
