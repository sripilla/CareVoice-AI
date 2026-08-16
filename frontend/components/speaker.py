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
            type="button"
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

            button.addEventListener("click", function() {{
                const text = {text_json};
                const language = {language_json};

                if (!text || !text.trim()) {{
                    return;
                }}

                window.speechSynthesis.cancel();

                setTimeout(function() {{
                    const utterance =
                        new SpeechSynthesisUtterance(text);

                    utterance.lang = language;

                    utterance.rate = 1;
                    utterance.pitch = 1;

                    window.speechSynthesis.resume();

                    window.speechSynthesis.speak(
                        utterance
                    );
                }}, 100);
            }});
        </script>
        """,
        height=55,
    )