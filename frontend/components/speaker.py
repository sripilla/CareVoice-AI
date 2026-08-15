"""
Browser-based text-to-speech component.
"""

import json

import streamlit.components.v1 as components


def render_speaker(
    text: str,
    language: str,
    key: str,
):
    """
    Render a button that speaks the given text using
    the browser's Web Speech API.
    """

    if not text or not text.strip():
        return

    language_map = {
        "te": "te-IN",
        "hi": "hi-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "mr": "mr-IN",
        "bn": "bn-IN",
        "gu": "gu-IN",
        "pa": "pa-IN",
        "ur": "ur-IN",
        "en": "en-US",
    }

    speech_language = language_map.get(
        language,
        "en-US",
    )

    text_json = json.dumps(text)
    language_json = json.dumps(speech_language)

    components.html(
        f"""
        <button
            id="{key}"
            style="
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #cccccc;
                cursor: pointer;
                font-size: 14px;
            "
        >
            🔊 Speak
        </button>

        <script>
            const button = document.getElementById(
                "{key}"
            );

            button.onclick = function() {{
                window.speechSynthesis.cancel();

                const utterance =
                    new SpeechSynthesisUtterance(
                        {text_json}
                    );

                utterance.lang = {language_json};

                window.speechSynthesis.speak(
                    utterance
                );
            }};
        </script>
        """,
        height=50,
    )