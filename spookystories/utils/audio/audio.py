from utils.runtime import print_runtime
from utils.tts.google import tts





# clip_path = f"{reddit_id}/{clip_idx}"
# os.makedirs(clip_path, exist_ok=True)
# for segment_idx, segment in enumerate(clip):
#
#     test = " ".join(clip)
#     segment_file = f"{clip_path}/{segment_idx}.mp3"
#     if not os.path.isfile(segment_file):
#         total_runtime = audio(test, voice, segment_file)
# # combine each segment into one file clip
# combine_audio(clip_path)
#
#
#
# def combine_audio(clip_path):
#     audio_segments = []
#     for file in os.listdir(clip_path):
#         segment = AudioSegment.from_file(f"{clip_path}/{file}", format="mp3")
#         audio_segments.append(segment)
#     combined_audio = sum(audio_segments)
#     combined_audio.export(f"{clip_path}.mp3", format="mp3")