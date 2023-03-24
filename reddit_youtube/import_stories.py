from utils.runtime import print_runtime
from utils.reddit import get_submissions
from utils.parsers import import_story_args
from utils.mongodb import MongoDB
from utils.story import Story

@print_runtime
def import_stories():
    print("Starting Reddit Submission import.")
    args = import_story_args()
    mongo_db = MongoDB("storys")
    for sub in get_submissions(args):
        if mongo_db.get(sub.id):
            continue

        # Create Story model for submission and all submissions in series
        series_id = mongo_db.get_series_id(args.add_to_front)
        story = Story(sub, series_id)
        series = story.get_series_bfs()

        # add series to DB
        [mongo_db.insert(s) for s in series]


if __name__ == "__main__":
    import_stories()