import praw
import collections
from .format_text import (
    time_diff, author_name, author_flair,
    extract_reddit_ids, title_flair, awards_flair, text_segments
)

from .reddit import check_nosleep


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
        self.created_text = time_diff(sub.created)
        self.author = author_name(sub.author)
        self.author_flair = author_flair(sub.author_flair_text)
        self.text_ids = extract_reddit_ids(sub.selftext)
        self.title_flair = title_flair(sub.link_flair_text)
        self.awards = awards_flair(sub.all_awardings)
        self.is_series = False
        self.series_id = series_id
        self.series_part = None
        self.voice = "geralt"

        self.html_text, self.tts_text = text_segments(sub.selftext)
        self.add_title_and_outro()

    def __lt__(self, other: "Story"):
        """Evaluate which Story is smaller"""
        if self.series_id != other.series_id:
            return self.series_id < other.series_id
        return self.created < other.created

    def add_title_and_outro(self):
        # add title audio to first bg image
        _, title_tts = text_segments(self.title)
        self.tts_text.insert(0, title_tts[0])
        self.html_text.insert(0, self.html_text[0])

        # add outro audio to last bg image
        self.tts_text.append(
            "<speak><emphasis level=\"moderate\">Thanks for listening to this story. Stay tuned for more!</emphasis></speak>")
        self.html_text.append(self.html_text[-1])

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
            else:
                self.is_series = True
                sub_story.is_series = True

            sub_story.get_series_dfs(visited)

        return sorted(list(visited))

    def get_series_bfs(self, praw_client) -> list["Story"]:
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
                sub = check_nosleep(praw_client, sub_id)
                if not sub:
                    continue

                # determine if it's in the same series
                sub_story = Story(sub, self.series_id)
                if sub_story.check_same_series(self):
                    self.is_series = True
                    sub_story.is_series = True
                else:
                    sub_story.series_id = different_series
                    different_series += 1
                    self.is_series = True
                    sub_story.is_series = True

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

        if prev.title == self.title:
            return True

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
        num_common_words = len(set(prev_title_words) & set(curr_title_words))
        return num_common_words / avg_words > 0.4

        return False

    def db_object(self):
        return {
            "_id": self.reddit_id,
            "title": self.title,
            "author": self.author,
            "html_text": self.html_text,
            "tts_text": self.tts_text,
            "url": self.url,
            "created": self.created,
            "created_text": self.created_text,
            "author_flair": self.author_flair,
            "title_flair": self.title_flair,
            "awards": self.awards,
            "voice": self.voice,
            "is_series": self.is_series,
            "series_id": self.series_id,
            "series_part": self.series_part,
            "playlist_id": None,
            "upload_date": None,
        }
