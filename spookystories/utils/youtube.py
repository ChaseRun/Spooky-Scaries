import os
from pyyoutube import Client
import pyyoutube.models as mds
from pyyoutube.media import Media
from datetime import datetime
from .databse import MongoDB
from dotenv import load_dotenv


load_dotenv()
CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
CHANNEL_ID = os.getenv("CHANNEL_ID")
YOUTUBE_TAGS = os.getenv("YOUTUBE_TAGS")


def youtube_client():
    client = Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    print(client.get_authorize_url())
    client.generate_access_token(authorization_response=input("Enter the Response URL"))
    return client


def video_tags():
    tags = []
    with open(YOUTUBE_TAGS, "r", encoding="utf8") as f:
        tags = f.read().splitlines()
    return tags


def video_description(story):
    title, author, url = story["title"], story["author"], story["url"]
    author_desc = ""
    disclaimer = ""
    if author != "deleted":
        author_desc = f"A Reddit story by {author}."
        disclaimer = (
            "\n\n\nDisclaimer:\n"
            f"All copyrights belong to the reddit user: {author}\n"
            "Monetization is disabled on this channel.\n"
            "I don't make a profit from uploading this content, I am just a "
            "fan.\n"
            f"If {author} wants this video to be deleted, please send me an "
            f"e-mail and I will delete it immediately\n"
            "My email: spookystories01@gmail.com\n"
            "Thank you!"
        )
    description = (
        f"{title}\n"
        f"{author_desc}\n"
        f"Story link: {url}"
        "If you enjoy our Narrations / Readings, Don't forget to leave a "
        "like and subscribe!\n"
        "Feel free to let me know other stories you would like to hear "
        "down in the comments.\n"
        "Hit that notification bell to not miss another video!"
        f"{disclaimer}"
    )
    return description


def insert_video(youtube_client, story, file_name):

    body = mds.Video(
        snippet=mds.VideoSnippet(
            title=story["title"],
            description=video_description(story),
            channelId=CHANNEL_ID,
            channelTitle="SpookyStories",
            tags=video_tags(),
            categoryId="24",  # Entertainment, cannot select Horror
            defaultLanguage="en",
            defaultAudioLanguage="en",
        )
    )
    upload = youtube_client.videos.insert(
        body=body,
        media=Media(filename=file_name),
        parts=["snippet"],
       # notify_subscribers=True,
        notify_subscribers=False,
        status={
            "embeddable": True,
            "license": "creativeCommon",
            "privacyStatus": "private",
            "publicStatsViewable": True,
            # "publishAt": publish_date(),
            "selfDeclaredMadeForKids": False,
        }
    )

    video_body = None
    while video_body is None:
        status, video_body = upload.next_chunk()
        if status:
            print(f"Upload progress: {status.progress()}")
    return video_body["id"]


def insert_playlist(youtube_client, story_id):
    # create a playlist
    playlist = youtube_client.playlists.insert(
        body=mds.PlaylistSnippet(
            title=story["playlist_title"],
        ),
    )

    test = playlist.id
    # update all the playlist ids for the series
    MongoDB().update_playlist(story["id"], playlist.id)
    return playlist.id


def insert_playlist_item(youtube_client, video_id, playlist_id):
    # add story to playlist
    playlist_item = youtube_client.playlistItems.insert(
        body=mds.PlaylistItemSnippet(
            playlistId=playlist_id,
            resourceId=video_id
        )
    )

    test = playlist_item.id


def upload_to_youtube(story, dir):
    print("Uploading to YouTube")
    video_file = f"{dir}/final.mp4"

    client = None
    #client = youtube_client()
    db_client = MongoDB("story")

    # upload story and add to a playlist if it is a series
    video_id = insert_video(client, story, video_file)
    # if story["is_series"]:
    #     playlist_id = story["playlist_id"]
    #     if not playlist_id:
    #         playlist_id = insert_playlist(client, db_client,
    #                                       story["_id"])
    #     add_to_playlist(client, video_body["id"], playlist_id)

    # mark as posted
    db_client.uploaded(story["_id"])
    return True