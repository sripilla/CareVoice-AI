from careinsight.engine import CareVoiceEngine


def main():

    AUDIO_FILE = "data/raw_audio/telugu/TE001.wav"

    engine = CareVoiceEngine()

    report = engine.process_audio(AUDIO_FILE)

    print(report["clinical_report"])


if __name__ == "__main__":
    main()