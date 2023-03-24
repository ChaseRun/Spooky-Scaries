import story

import data_storage

if __name__ == "__main__":
    args = utils.praw_utils.get_args()
    print("Starting Reddit Submission import.")
    for sub in utils.praw_utils.get_submissions(args):
        if data_storage.db.get(sub.id):
            continue

        # Create Story model for submission and all submissions in series
        series_id = data_storage.db.get_series_id(args.add_to_front)
        current_story = story.Story(sub, series_id)
        series = current_story.get_series_bfs()

        # add series to DB
        [data_storage.db.insert(series_story) for series_story in series]
