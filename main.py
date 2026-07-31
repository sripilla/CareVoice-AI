from speech.transcriber import SpeechTranscriber


def main():

    AUDIO_FILE = "data/raw_audio/telugu/TE001.wav"
    OUTPUT_FILE = "data/transcripts/TE001.txt"

    transcriber = SpeechTranscriber(model_name="large-v3")

    transcript = transcriber.transcribe(AUDIO_FILE)

    print("\n========== TRANSCRIPT ==========\n")
    print(transcript)

    transcriber.save_transcript(
        transcript=transcript,
        output_path=OUTPUT_FILE
    )

    print("\nSpeech module completed successfully.")


if __name__ == "__main__":
    main()