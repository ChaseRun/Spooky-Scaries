import collections

import format_text
import praw
import praw_utils


class Story:
    """Imports reddit submission data, so it can be saved in a DB

    Args
        sub: A Praw Submission representing a nosleep story
    """

    def __init__(self, sub: praw.models.Submission, series_id: int) -> None:
        print(f"Submission: {id}. Creating a Story object.")
        self.reddit_id = sub.id
        self.title = sub.title
        self.url = sub.shortlink
        self.created = sub.created
        self.created_text = format_text.time_diff(sub.created)
        self.author = format_text.author_name(sub.author)
        self.author_flair = format_text.author_flair(sub.author_flair_text)
        self.text_ids = format_text.extract_reddit_ids(sub.selftext)
        self.html_text, self.tts_text = format_text.text_segments(sub.selftext)
        self.title_flair = format_text.title_flair(sub.link_flair_text)
        self.awards = format_text.awards_flair(sub.all_awardings)
        self.series_id = series_id
        self.series_part = None

    def __lt__(self, other: "Story"):
        """Evaluate which Story is smaller"""
        if self.series_id != other.series_id:
            return self.series_id < other.series_id
        return self.created < other.created

    def get_series_dfs(self, visited: set["Story"] = set()) -> list["Story"]:
        """Run DFS on all the links in the text recursively to create a full
        series list

        Args:
            visited: A set of visited stories

        Returns: A sorted list of stories that make up a series
        """
        visited.add(self)
        different_series = self.series_id + 1
        for sub_id in self.text_ids:
            # check if it's been visited
            if any(sub_id == s.reddit_id for s in visited):
                continue

            # check if it's a nosleep story
            sub = praw_utils.check_nosleep(sub_id)
            if not sub:
                continue

            # determine if it's in the same series
            sub_story = Story(sub, self.series_id)
            if not sub_story.check_same_series(self):
                sub_story.series_id = different_series
                different_series += 1

            sub_story.get_series_dfs(visited)

        return sorted(list(visited))

    def get_series_bfs(self) -> list["Story"]:
        """Run BFS on all the links in the text recursively to create a full
        series list

        Returns: A sorted list of stories that make up a series
        """

        visited, queue = set([self]), collections.deque([self])
        while queue:
            submission = queue.popleft()
            different_series = submission.series_id + 1
            for sub_id in submission.text_ids:
                # check if it's been visited
                if any(sub_id == s.reddit_id for s in visited):
                    continue

                # check if it's a nosleep story
                sub = reddit.check_nosleep(sub_id)
                if not sub:
                    continue

                # determine if it's in the same series
                sub_story = Story(sub, self.series_id)
                if not sub_story.check_same_series(self):
                    sub_story.series_id = different_series
                    different_series += 1

                visited.add(sub_story)
                queue.append(sub_story)

        # assign series parts to stories
        series_list = sorted(list(visited))
        series_id, series_part = series_list[0].series_id, 1
        for s in series_list:
            if s.series_id != series_id:
                series_id = s.series_id
                series_part = 1
            s.series_part = series_part
            series_part += 1
        return series_list

    def check_same_series(self, prev):
        """
        Sometimes, links from different series are in the text. This is hard
        to detect and should be adjusted in the DB manually.
        """

        if prev.author != self.author:
            return False

        # Check if 2 out of the 3 conditions are true:
        # 1. They both link each other
        # 2. If they both contain the word "part" curr_part == prev_part + 1
        # 3. They contain 40% at least 40% of the same words in their titles

        # check if they link each other
        # TODO: Check if it is in all the prev series links?
        if prev.reddit_id in self.text_ids:
            return True

        # get individual words in both strings
        prev_title_words = [s for s in prev.title.lower().split()]
        curr_title_words = [s for s in self.title.lower().split()]

        # check if current_part = prev_part + 1
        prev_part, curr_part = "", ""
        for idx, word in enumerate(prev_title_words):
            if word == "part" and idx < len(prev_title_words):
                prev_part = prev_title_words[idx + 1]
                break
        for idx, word in enumerate(curr_title_words):
            if word == "part" and idx < len(curr_title_words):
                curr_part = curr_part_index[idx + 1]
                break

        if prev_part.isnumeric() and curr_part.isnumeric():
            if int(curr_part) == int(prev_part) + 1:
                return True

        # check if titles contain at least 40% of the same words
        avg_words = len(prev.title) + len(self.title) / 2
        num_common_words = len(set(a) & set(b))
        return num_common_words / avg_words > 0.4

        return False

    # TODO: Add voice to DB
    # TODO: Add Youtube Playlist to DB
    # TODO: Add currently processing to DB
    def db_object(self):
        return {
            "_id": story.reddit_id,
            "title": story.title,
            "author": story.author,
            "html_text": story.html_text,
            "tts_text": story.tts_text,
            "url": story.url,
            "created": story.created,
            "created_text": story.created_text,
            "author_flair": story.author_flair,
            "title_flair": story.title_flair,
            "awards": story.awards,
            "series_id": story.series_id,
            "series_part": story.series_part,
            "audio_generated": False,
            "processing_audio": False,
            "video_generated": False,
            "processing_video": False,
            "posted": False,
            "posted_date": None,
        }
