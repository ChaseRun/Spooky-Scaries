import os
from time import time
from datetime import timedelta

from tts_engine import TextToSpeech
from tts_engine.utils.audio import combine_audio

import data_storage
import utils.parser as parser

if __name__ == "__main__":
    start_time = time()
    voice, preset, reddit_id, verbose = parser.get_args()
    tts = TextToSpeech(voice=voice, preset=preset)
    mongo_db = data_storage.db.Mongo("story")
    reddit_id, tts_text = mongo_db.highest_priority_tts(reddit_id)
    s3_files = data_storage.s3.files_in_bucket(reddit_id)

    # TODO: Mark start processing
    # TODO: Mark stop processing

    # parse each clips segments
    for clip_idx, clip in enumerate(tts_text):
        clip_path = f"{reddit_id}/{clip_idx}"

        # create local output dir
        if not os.path.exists(clip_path):
            os.makedirs(clip_path)

        # if clip file has been generated, continue
        if f"{clip_path}.wav" in s3_files:
            continue

        for segment_idx, segment in enumerate(clip):
            # if segment is already in s3, download and continue
            segment_file = f"{clip_path}/{segment_idx}.wav"
            if segment_file in s3_files:
                data_storage.s3.download(segment_file)
                continue

            # create segment audio file and upload to s3
            tts.run(segment, segment_file)
            data_storage.s3.upload(segment_file)

        # combine segments to make a final clip,  upload to s3
        combine_audio(clip_path, os.getcwd(), len(clip))
        data_storage.s3.upload(f"{clip_path}.wav")

    # update story "audio generated" in data_storage
    # data_storage.db.mark_audio_generated()

    # print runtime
    elapsed_time = timedelta(seconds=round(time() - start_time))
    elapsed_time_str = f"Execution Time: {time_str} (HH:MM:SS)"
    print(elapsed_time_str)

    # stop server
