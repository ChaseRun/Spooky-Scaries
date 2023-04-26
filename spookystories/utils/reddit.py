import os
from praw import Reddit
from praw.exceptions import InvalidURL
from dotenv import load_dotenv

load_dotenv()

def get_reddit_client() -> Reddit:
    """Use stored config params to create and return a praw.Reddit instance"""
    print("Creating Reddit Client")
    return Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
    )

def check_nosleep(praw_client, reddit_id):
    print(f"Validating submission with id: {reddit_id}")
    try:
        submission = praw_client.submission(id=reddit_id)
    except InvalidURL:
        print(f"id: {reddit_id} is not associated with a " f"reddit submission")
        return None
    else:
        if submission.subreddit.display_name == "nosleep":
            print(f"submission with id: {reddit_id} is valid")
            return submission
        else:
            print(
                f"submission with id: {reddit_id} is not a "
                f"r/nosleep submission"
            )
            return None
    return submission


# TODO: Need to test all of these edge cases
def get_submissions(praw_client, mongo_client, args):
    if args.reddit_ids:
        return submissions_from_ids(praw_client, mongo_client, args.reddit_ids)
    elif args.author:
        return submissions_from_author(args)
    else:
        return submissions_from_filters(args)


def submissions_from_ids(praw_client, mongo_db, reddit_ids):
    submissions = []
    for reddit_id in reddit_ids:
        if mongo_db.get(reddit_id):
            continue
        sub = check_nosleep(praw_client, reddit_id)
        if sub:
            submissions.append(sub)
    return submissions


def submissions_from_author(args):
    submissions = []
    redditor = get_reddit_client().redditor(args.author).submissions

    if args.sort_filter == "controversial":
        posts = redditor.controversial(time_filter=args.time_filter)
    elif args.sort_filter == "gilded":
        posts = redditor.gilded(time_filter=args.time_filter)
    elif args.sort_filter == "hot":
        posts = redditor.hot(time_filter=args.time_filter)
    elif args.sort_filter == "top":
        posts = redditor.top(time_filter=args.time_filter)
    elif args.sort_filter == "new":
        posts = redditor.new(time_filter=args.time_filter)

    for s in posts:
        if s.subreddit.display_name == "nosleep":
            submissions.append(s)
        if len(submissions) == args.num_stories:
            break
    return submissions


def submissions_from_filters(args):
    submissions = []
    sub_reddit = get_reddit_client().subreddit("nosleep")

    if args.sort_filter == "controversial":
        posts = sub_reddit.controversial(time_filter=args.time_filter)
    elif args.sort_filter == "gilded":
        posts = sub_reddit.gilded(time_filter=args.time_filter)
    elif args.sort_filter == "hot":
        posts = sub_reddit.hot(time_filter=args.time_filter)
    elif args.sort_filter == "top":
        posts = sub_reddit.top(time_filter=args.time_filter)
    elif args.sort_filter == "new":
        posts = sub_reddit.new(time_filter=args.time_filter)
    elif args.sort_filter == "rising":
        posts = sub_reddit.rising()

    for s in posts:
        submissions.append(s)
        if len(submissions) == args.num_stories:
            break
    return submissions
