import pytest

import data_storage

SERIES_0 = [
    {
        "_id": "0",
        "title": "Series: 1 - Story: 1",
        "tts_text": None,
        "series_id": 0,
        "series_part": 1,
        "audio_generated": False,
        "processing_audio": False,
        "video_generated": False,
        "processing_video": False,
        "posted": False,
        "posted_date": None,
    },
]

SERIES_1 = [
    {
        "_id": "1",
        "title": "Series: 2 - Story: 1",
        "tts_text": None,
        "series_id": 1,
        "series_part": 1,
        "audio_generated": False,
        "processing_audio": False,
        "video_generated": False,
        "processing_video": False,
        "posted": False,
        "posted_date": None,
    },
    {
        "_id": "2",
        "title": "Series: 2 - Story: 2",
        "tts_text": None,
        "series_id": 1,
        "series_part": 2,
        "audio_generated": False,
        "processing_audio": False,
        "video_generated": False,
        "processing_video": False,
        "posted": False,
        "posted_date": None,
    },
    {
        "_id": "3",
        "title": "Series: 2 - Story: 3",
        "tts_text": None,
        "series_id": 1,
        "series_part": 3,
        "audio_generated": False,
        "processing_audio": False,
        "video_generated": False,
        "processing_video": False,
        "posted": False,
        "posted_date": None,
    },
]


def test_insert():
    mongo_db = data_storage.db.Mongo("test")
    mongo_db.delete_collection()

    story = SERIES_0[0]

    # normal insert
    assert mongo_db.insert(story)
    story_out = mongo_db.get(story["_id"])
    assert story_out and story_out == story

    # duplicate insert
    assert not mongo_db.insert(story)

    # clean
    mongo_db.delete_collection()


def test_get():
    mongo_db = data_storage.db.Mongo("test")
    mongo_db.delete_collection()

    # get story that doesn't exist
    story_out = mongo_db.get("12")
    assert not story_out

    story = SERIES_0[0]

    assert mongo_db.insert(story)
    story_out = mongo_db.get(story["_id"])
    assert story_out and story_out == story

    # clean
    mongo_db.delete_collection()


def test_update():
    mongo_db = data_storage.db.Mongo("test")
    mongo_db.delete_collection()

    # update story that doesn't exist
    assert not mongo_db.update("123", data_storage.db.AUDIO_GENERATED)

    # insert
    story = SERIES_0[0]
    assert mongo_db.insert(story)

    # audio_generated = False
    story_out = mongo_db.get(story["_id"])
    assert story_out and story_out == story
    assert not story_out["audio_generated"]

    # update
    assert mongo_db.update(story["_id"], data_storage.db.AUDIO_GENERATED)

    # audio_generated = True
    story_out = mongo_db.get(story["_id"])
    assert story_out and story_out["audio_generated"]

    # all updates
    assert mongo_db.update(story["_id"], data_storage.db.AUDIO_GENERATED)
    assert mongo_db.update(story["_id"], data_storage.db.VIDEO_GENERATED)
    assert mongo_db.update(story["_id"], data_storage.db.POSTED)
    assert mongo_db.update(story["_id"], data_storage.db.START_AUDIO_GENERATION)
    assert mongo_db.update(story["_id"], data_storage.db.START_VIDEO_GENERATION)
    assert mongo_db.update(story["_id"], data_storage.db.STOP_AUDIO_GENERATION)
    assert mongo_db.update(story["_id"], data_storage.db.STOP_VIDEO_GENERATION)

    # clean
    mongo_db.delete_collection()


def test_series_id_operations():
    mongo_db = data_storage.db.Mongo("test")
    mongo_db.delete_collection()

    # insert series 0
    for story in SERIES_0:
        assert mongo_db.insert(story)
    assert mongo_db.get_series_id() == 1

    # insert series 1
    for story in SERIES_1:
        assert mongo_db.insert(story)
    assert mongo_db.get_series_id() == 2

    # test get_series and shift
    assert mongo_db.get_series_id(True) == 0
    assert mongo_db.get_series_id() == 3
    mongo_db.shift_series_ids()
    assert mongo_db.get_series_id() == 4

    mongo_db.delete_collection()


def test_highest_priority_story():
    mongo_db = data_storage.db.Mongo("test")
    mongo_db.delete_collection()

    # insert series 0
    for story in SERIES_0:
        assert mongo_db.insert(story)
    assert mongo_db.get_series_id() == 1

    # insert series 1
    for story in SERIES_1:
        assert mongo_db.insert(story)
    assert mongo_db.get_series_id() == 2

    # highest priority is 0-1
    story = SERIES_0[0]
    story_id, _ = mongo_db.highest_priority_tts()
    assert story_id == story["_id"]
    # highest priority is 0-1
    story_id, _ = mongo_db.highest_priority_tts()
    assert story_id == story["_id"]
    assert mongo_db.update(story["_id"], data_storage.db.AUDIO_GENERATED)

    # the highest priority is 1-1
    story = SERIES_1[0]
    story_id, _ = mongo_db.highest_priority_tts()
    assert story_id == story["_id"]
    assert mongo_db.update(story["_id"], data_storage.db.START_AUDIO_GENERATION)

    # the highest priority is 1-2
    story = SERIES_1[1]
    story_id, _ = mongo_db.highest_priority_tts()
    assert story_id == story["_id"]
    assert mongo_db.update(story["_id"], data_storage.db.AUDIO_GENERATED)
    assert mongo_db.update(story["_id"], data_storage.db.START_AUDIO_GENERATION)

    # specific story has already been processed
    story_id, _ = mongo_db.highest_priority_tts(story["_id"])
    assert not story_id

    # specific story has not been processed
    story = SERIES_1[2]
    story_id, _ = mongo_db.highest_priority_tts(story["_id"])
    assert story_id == story["_id"]
    assert mongo_db.update(story["_id"], data_storage.db.START_AUDIO_GENERATION)
    assert mongo_db.update(story["_id"], data_storage.db.START_AUDIO_GENERATION)

    # all stories have audio generated
    story_id, _ = mongo_db.highest_priority_tts()
    assert not story_id

    mongo_db.delete_collection()
