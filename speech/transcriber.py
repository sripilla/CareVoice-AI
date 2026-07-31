from pathlib import Path
from faster_whisper import WhisperModel
import torch


class SpeechTranscriber:
    """
    Speech-to-Text module using Faster Whisper.
    """

    def __init__(self, model_name: str = "small"):

        if torch.backends.mps.is_available():
            self.device = "cpu"
            self.compute_type = "int8"
        else:
            self.device = "cpu"
            self.compute_type = "int8"

        print(f"\nLoading Faster Whisper model ({model_name})...")
        print(f"Running on: {self.device}")

        self.model = WhisperModel(
            model_name,
            device=self.device,
            compute_type=self.compute_type
        )

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file.
        """

        print(f"\nTranscribing: {audio_path}")

        segments, info = self.model.transcribe(
            audio_path,
            language="te",
            beam_size=5, 
            vad_filter=False,
            condition_on_previous_text=False,
            temperature=0.0
        )

        print(f"Detected language: {info.language}")
        print(f"Language probability: {info.language_probability:.2f}")

        transcript = []

        for segment in segments:
            print(
                f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
            )
            transcript.append(segment.text)

        return " ".join(transcript).strip()

    def save_transcript(self, transcript: str, output_path: str):

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(transcript)

        print(f"\nTranscript saved to: {output_file}")