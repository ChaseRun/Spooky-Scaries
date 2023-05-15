import os
from dotenv import load_dotenv
from google.cloud import texttospeech
from ..runtime import print_runtime


load_dotenv()
cwd = os.path.dirname(os.path.abspath(__file__))
google_credentials = f"{cwd}/../../../google_tts_credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials


@print_runtime
def generate_audio(story, dir):
    print(" - Generating Audio")
    # parse each clips segments
    for idx, segment in enumerate(story["tts_text"]):
        audio_file = f"{dir}/{idx}.mp3"
        if not os.path.isfile(audio_file):
            tts(segment, story["voice"], f"{dir}/{idx}.mp3")



def tts(text, voice, output_file):
    print(f"Writing Audio content to: {output_file}")

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(ssml=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Neural2-D"
    )
    # Convert response to mp3 and save audio to disk
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file: {output_file}"')


def list_voices():
    """Lists the available voices."""
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices()
    for voice in voices.voices:
        print(f"Name: {voice.name}")
        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)
        # Display the SSML Voice Gender
        print(f"SSML Voice Gender: {ssml_gender.name}")
        # Display the natural sample rate hertz for this voice. Example: 24000
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")
