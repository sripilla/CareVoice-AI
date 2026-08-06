import streamlit as st

from components.sidebar import render_sidebar


def main():

    st.set_page_config(
        page_title="CareVoice AI",
        page_icon="🏥",
        layout="wide"
    )

    page = render_sidebar()

    st.title("🏥 CareVoice AI")

    st.subheader("Multilingual Clinical Speech Analysis")

    st.divider()

    st.write(f"Current Page: **{page}**")


if __name__ == "__main__":
    main()