import os
import re

from .tts_engine import TTSEngine


# def create_text_segments(text, max_chars):
#     segments = []
#     plain_text_segment, ssml_text_segment = "", ""
#     for sentance in text.split("."):
#         sentance.append(".")
#         ssml_sentance = make_ssml(sentance)
#         if len(ssml_text_segment) + len(ssml_sentance) <= max_chars:
#             ssml_text_segment += ssml_sentance
#         else:
#             segments.append((plain_text_segment, ssml_text_segment))
#             sentance = sentance.lstrip(" \n")
#             plain_text_segment, ssml_text_segment = sentance, ssml_sentance
#     segments.append((plain_text_segment, ssml_text_segment))
#     return segments
#
#
# def make_ssml(text):
#     # makes splitting words easier
#
#     # remove bad chars: not removing apostrophes
#     # `^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
#     bad_chars = r"\s['|’]|['|’]\s|[\^_~@!&;#\-–—%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
#
#     text = re.sub(bad_chars, " ", text)
#     text = re.sub("“", '"', text)
#     text = re.sub("”", '"', text)
#     text = text.replace("+", "plus")
#
#     # replace ssml reserved chars
#     # https://docs.aws.amazon.com/polly/latest/dg/escapees.html
#     text = text.replace("&", "and")
#     text = text.replace('"', "")
#     text = text.replace("’", "&apos;")
#     text = text.replace("<", "")
#     text = text.replace(">", "")
#
#     # add pause between periods and colons
#     # - already handled by '.', but adding ssml tag for readability
#     text = text.replace(".", '<break time="0.25s"/>')
#     text = text.replace(":", '<break time="0.25s"/>')
#
#     # add pause between paragraphs
#     text = text.replace("\n\n", '<break time="0.8s"/>')
#     text = text.replace("\n\n", '<break time="0.8s"/> ')
#     text = text.replace("\n", '<break time="0.8s"/> ')
#
#     return text


def generate_ssml_text(title, text, directory):
    # will add space back to <break strength.../> in TTS engine
    # makes splitting words easier

    # remove bad chars: not removing apostrophes
    # `^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    bad_chars = r"\s['|’]|['|’]\s|[\^_~@!&;#\-–—%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"

    title, text = re.sub(bad_chars, " ", title), re.sub(bad_chars, " ", text)
    title, text = re.sub("“", '"', title), re.sub("“", '"', text)
    title, text = re.sub("”", '"', title), re.sub("”", '"', text)
    title, text = title.replace("+", "plus"), text.replace("+", "plus")

    # replace ssml reserved chars
    # https://docs.aws.amazon.com/polly/latest/dg/escapees.html
    title, text = title.replace("&", "and"), text.replace("&", "and")
    title, text = title.replace('"', ""), text.replace('"', "")
    title, text = title.replace("’", "&apos;"), text.replace("’", "&apos;")
    title, text = title.replace("<", ""), text.replace("<", "")
    title, text = title.replace(">", ""), text.replace(">", "")

    # add pause between periods and colons
    # - already handled by '.', but adding ssml tag for readability
    title = title.replace(".", '<breaktime="0.25s"/>')
    title = title.replace(":", '<breaktime="0.25s"/>')
    text = text.replace(".", '<breaktime="0.25s"/>')
    text = text.replace(":", '<breaktime="0.25s"/>')

    # add pause between paragraphs
    text = text.replace("\n\n", '<breaktime="0.8s"/>')
    text = text.replace("\n\n", '<breaktime="0.8s"/> ')
    text = text.replace("\n", '<breaktime="0.8s"/> ')



# def generate_subtitles(title: str, text: str, directory: str) -> None:
#     if not directory:
#         print("ERROR")
#     if not text:
#         print("ERROR")
#     if os.path.exists(f"{directory}/subtitles.txt"):
#         print("Subtitles Exist. No need to regenerate")
#         return
#
#     with open(f"{directory}/subtitles.txt", "w") as f:
#         f.write(title + text)
#


def generate_audio(directory: str = None, voice: str = None) -> None:
    if not directory:
        print("ERROR")
    if os.path.exists(f"{directory}/audio.mp3"):
        print("Audio file already exists. No need to re generate")
        return

    with open(f"{directory}/ssml.txt", "r") as f:
        ssml_text = f.read()
    tts = TTSEngine(path=directory, voice=voice, text=ssml_text)
    tts.run()
