import re
from datetime import datetime

SECTION_CHAR = "\n\n&#x200B;\n\n"
PARAGRAPH_CHAR = "\n\n"
P_TAGS = "</p><p>"
MAX_HTML_CHARS = 1850



# TODO: Remove profanity
def text_segments(input_text: str) -> tuple[list[str], list[list[str]]]:
    # Cannot use '|' character in the text. This is what tts engine uses to
    # split text

    text = remove_urls(input_text)

    # TODO: clean markdown characters, but still have for html

    # Split text into sections and paragraphs.
    # At the end each loop remove the extra section and paragraph tag.
    tts_segments = []
    for section in text.split(SECTION_CHAR):
        for paragraph in section.split(PARAGRAPH_CHAR):
            # format paragraph text for tts
            split_text = split_tts_text(paragraph)
            tts_segments.extend(split_text)
            tts_segments.append(P_TAGS)
        tts_segments.pop()
        tts_segments.append(P_TAGS * 2)
    tts_segments.pop()

    # Associate HTML text with specific audio files
    # Makes it easier to add audio to screenshot backgrounds
    html_template, html_template_size, html_templates = "", 0, []
    audio_clips = [[]]
    for idx, segment in enumerate(tts_segments):
        # if section or paragraph just add to HTML template
        if "<p>" in segment:
            html_template = f"{html_template}{segment}"
        # add HTML to template and add tts to audio clip
        elif html_template_size + len(segment) < MAX_HTML_CHARS:
            html_template_size += len(segment)
            html_template = (
                f"{html_template}<p>{format_reddit_markdown(segment)}"
            )
            segment = re.sub(r"\*", "", segment)
            audio_clips[-1].append(segment)
        # create new HTML template and add to list of templates
        else:
            html_templates.append(f"{html_template}</p>")
            html_template = f"<p>{format_reddit_markdown(segment)}"
            html_template_size = len(segment)
            segment = re.sub(r"\*", "", segment)
            audio_clips.append([segment])

    html_templates.append(f"{html_template}</p>")
    return html_templates, audio_clips


def format_reddit_markdown(text):
    # TODO: Handle tables later
    # **italics**
    clean_text = re.sub(r"\*\*(.*?)\*\*", r"<em>\1</em>", text)
    # *bold*
    clean_text = re.sub(r"\*(.*?)\*", r"<strong>\1</strong>", clean_text)

    clean_text = re.sub(r"~~(.*?)~~", r"<strike>\1</strike>", clean_text)

    return clean_text


def split_tts_text(text, desired_length=200, max_length=300):
    """Split text it into chunks of a desired length trying to keep sentences intact."""
    # normalize text, remove redundant whitespace and convert non-ascii quotes to ascii
    text = re.sub(r"\n\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[“”]", '"', text)

    # reddit markdown
    text = re.sub(r">", "", text)  # "> quoted text"
    text = re.sub(r"\^", " ", text)  # "super^script"

    rv = []
    in_quote = False
    current = ""
    split_pos = []
    pos = -1
    end_pos = len(text) - 1

    def seek(delta):
        nonlocal pos, in_quote, current
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                pos -= 1
                current = current[:-1]
            else:
                pos += 1
                current += text[pos]
            if text[pos] == '"':
                in_quote = not in_quote
        return text[pos]

    def peek(delta):
        p = pos + delta
        return text[p] if p < end_pos and p >= 0 else ""

    def commit():
        nonlocal rv, current, split_pos
        rv.append(current)
        current = ""
        split_pos = []

    while pos < end_pos:
        c = seek(1)
        # do we need to force a split?
        if len(current) >= max_length:
            if len(split_pos) > 0 and len(current) > (desired_length / 2):
                # we have at least one sentence and we are over half the desired length, seek back to the last split
                d = pos - split_pos[-1]
                seek(-d)
            else:
                # no full sentences, seek back until we are not in the middle of a word and split there
                while (
                    c not in "!?.\n "
                    and pos > 0
                    and len(current) > desired_length
                ):
                    c = seek(-1)
            commit()
        # check for sentence boundaries
        elif not in_quote and (c in "!?\n" or (c == "." and peek(1) in "\n ")):
            # seek forward if we have consecutive boundary markers but still within the max length
            while (
                pos < len(text) - 1
                and len(current) < max_length
                and peek(1) in "!?."
            ):
                c = seek(1)
            split_pos.append(pos)
            if len(current) >= desired_length:
                commit()
        # treat end of quote as a boundary if its followed by a space or newline
        elif in_quote and peek(1) == '"' and peek(2) in "\n ":
            seek(2)
            split_pos.append(pos)
    rv.append(current)

    # clean up, remove lines with only whitespace or punctuation
    rv = [s.strip() for s in rv]
    rv = [s for s in rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)]

    return rv


def remove_urls(text) -> str:
    """Removes all URLs from the text
    Removes the word "Part" containing a url if it is at the start or end of
    the text.
    """

    # def sanitize_text(text, remove_part):
    #     # remove url if it contains the word "part"
    #     if remove_part:
    #         series_urls = r"\[part.+]|\[Part.+\]"
    #         text = re.sub(series_urls, "", text)
    #
    #     # remove all other urls
    #     other_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    #     text = re.sub(other_urls, "", text)
    #
    #     # replace swear words
    #     for word in load_bad_words():
    #         text.replace(word, "bad word")
    #
    #     return text
    #
    # def load_bad_words():
    #     bad_word_dict = {}
    #     with open("config/profanity.txt", "r") as f:
    #         for w in f.readlines():
    #             bad_word_dict[w] = True
    #     return bad_word_dict

    # TODO: DOUBLE CHECK THIS. PART TWO was included in first item in DB
    # 'My sugar daddy asks me for weird favors'
    # TODO: check this for a better regex https://stackoverflow.com/questions/23394608/python-regex-fails-to-identify-markdown-links
    url_regex = (
        r"((http|https)\:\/\/)"
        r"?[a-zA-Z0-9\.\/\?\:@\-_=#]+\."
        r"([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    )
    clean_text = re.sub(url_regex, "", text)

    clean_text = clean_text.replace("\n", " NEWLINE_CHAR ")
    split_str = clean_text.split()
    # [Part *] at start of the string
    while split_str[0] == "[Part" or split_str[0] == "[part":
        split_str.pop(0)
        split_str.pop(0)

    # [Part *] from end of the string
    while split_str[-1][0].isdigit() and split_str[-1][-1] == "]":
        split_str.pop()
        split_str.pop()

    # [ and ]
    clean_text = " ".join(split_str)
    clean_text = clean_text.replace("[", "")
    clean_text = clean_text.replace("]", "")
    clean_text = clean_text.replace("()", "")

    # add newlines back
    clean_text = clean_text.replace("NEWLINE_CHAR", "\n")
    clean_text = clean_text.replace(" \n", "\n")
    clean_text = clean_text.replace("\n ", "\n")

    return clean_text


# PREVIOUSLY IN STORY
def author_name(author) -> str:
    """Set author name to "deleted" if submission author is None"""
    return "deleted" if not author else author.name


def author_flair(author_flair) -> None:
    """Add HTML tags to author_flair"""
    if not author_flair:
        return ""
    else:
        return f'<span class="flair">{author_flair}</span>'


def title_flair(title_flair) -> None:
    """Add HTML tags to title_flair"""
    if not title_flair:
        return ""
    return f'<span class="linkflairlabel">' f"{title_flair}" "</span>"


def awards_flair(awards) -> None:
    """Add HTML tags to awards"""
    awards_html = ""
    for a in awards:
        count = a["count"] if a["count"] > 1 else ""
        awards_html += (
            f'<a class="awarding-link">'
            '<span class="awarding-icon-container">'
            f'<img class="awarding-icon" src="{a["static_icon_url"]}">'
            f"</span>{count}</a>"
        )
    return awards_html


def time_diff(created) -> None:
    """Calculates how long ago a reddit submission was created.
    Save as created_text
    """

    time_diff = datetime.utcnow() - datetime.fromtimestamp(created)
    minutes_since = time_diff.days * 24 * 60
    hours_since = time_diff.days * 24
    days_since = time_diff.days
    months_since = int((time_diff.days / 30) // 1)
    years_since = int((time_diff.days / 365) // 1)

    if years_since > 1:
        return f"{years_since} years"
    elif months_since > 1:
        return f"{months_since} months"
    elif days_since > 1:
        return f"{days_since} days"
    elif hours_since > 1:
        return f"{hours_since} hours"
    else:
        return f"{minutes_since} minutes"


def extract_reddit_ids(text: str) -> set[str]:
    # First extracts all reddit ids. Then checks to see if the link is
    # a reddit link and if it's subreddt is "nosleep".

    # find submission ids by searching 6 chars after places in link
    text_ids = set()
    for idx in re.finditer("r/nosleep/comments/", text):
        start_idx = idx.start() + len("r/nosleep/comments/")
        end_idx = start_idx + 7
        text_ids.add(text[start_idx:end_idx])
    for idx in re.finditer("https://redd.it/", text):
        start_idx = idx.start() + len("https://redd.it/")
        end_idx = start_idx + 7
        text_ids.add(text[start_idx:end_idx])

    return text_ids
