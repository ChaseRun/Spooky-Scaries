from tts_engine.api import TextToSpeech
from tts_engine.utils.audio import combine_audio
from utils.audio import file_exists
from utils.runtime import print_runtime
from utils.mongodb import MongoDB, AUDIO_GENERATED, START_AUDIO_GENERATION
from utils.s3 import S3

@print_runtime
def generate_audio():
    s3, mongo_db = S3(), MongoDB("story")
    # TODO: add voice option
    reddit_id, tts_text = mongo_db.highest_priority_tts()
    s3_files = s3.files_in_bucket(reddit_id)
    tts = TextToSpeech()

    # Start Audio Generation
    # mongo_db.update(reddit_id, START_AUDIO_GENERATION)
    # parse each clips segments
    for clip_idx, clip in enumerate(tts_text):
        # if clip file exists continue
        clip_path = f"{reddit_id}/{clip_idx}"
        if file_exists(clip_path, s3_files):
            continue

        for segment_idx, segment in enumerate(clip):
            # if segment is already in s3, download and continue
            segment_file = f"{clip_path}/{segment_idx}.wav"
            if file_exists(segment_file, s3_files):
                continue

            # create segment audio file and upload to s3
            tts.run(segment, segment_file)
            s3.upload(segment_file)

        # combine segments to make a final clip,  upload to s3
        combine_audio(clip_path, os.getcwd(), len(clip))
        s3.upload(f"{clip_path}.wav")

    # update story "audio generated" in data_storage
    mongo_db.update(reddit_id, AUDIO_GENERATED)

    # stop server


if __name__ == "__main__":
    generate_audio()
