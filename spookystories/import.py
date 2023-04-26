from utils.runtime import print_runtime
from utils.reddit import get_submissions, get_reddit_client, check_nosleep
from utils.parsers import import_story_args
from utils.databse import MongoDB
from utils.story import Story

@print_runtime
def import_stories():
    print("Starting Reddit Submission import.")
    args = import_story_args()
    praw_client, mongo_db = get_reddit_client(), MongoDB("story")
    for sub in get_submissions(praw_client, mongo_db, args):
        # Create Story model for submission and all submissions in series
        series_id = mongo_db.get_series_id(args.add_to_front)
        story = Story(sub, series_id)
        series = story.get_series_bfs(praw_client)

        # add series to DB
        [mongo_db.insert(s.db_object()) for s in series]


if __name__ == "__main__":
    import_stories()