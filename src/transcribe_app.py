"""
Author: Dominik Kunz
Date : 15.11.22
Title : Transcribe
Running on replicate
"""
import os
import sys
sys.path.insert(0, os.path.abspath("../"))  # insert the path at the first position


import streamlit as st
import replicate

# set window properties
st.set_page_config(layout="wide")
st.set_option("deprecation.showPyplotGlobalUse", False)

@st.cache_data()
def whisperTranslator(auth_key):
    """
    Establishes a connection to the DeepL Rest-API
    :param auth_key: authentification key
    :return: API-connection
    """
    client = replicate.Client(api_token=auth_key)
    model = client.models.get("openai/whisper")
    version = model.versions.get("91ee9c0c3df30478510ff8c8a3a545add1ad0259ad3a9f78fba57fbc05ee64f7")
    return version


def get_language():
    lang_vals = "af, am, ar, as, az, ba, be, bg, " \
                   "bn, bo, br, bs, ca, cs, cy, da, de, " \
                   "el, en, es, et, eu, fa, fi, fo, fr, gl, " \
                   "gu, ha, haw, he, hi, hr, ht, hu, hy, id, " \
                   "is, it, ja, jw, ka, kk, km, kn, ko, la, lb, " \
                   "ln, lo, lt, lv, mg, mi, mk, ml, mn, mr, ms, " \
                   "mt, my, ne, nl, nn, no, oc, pa, pl, ps, pt, ro, " \
                   "ru, sa, sd, si, sk, sl, sn, so, sq, sr, su, sv, sw, " \
                   "ta, te, tg, th, tk, tl, tr, tt, uk, ur, uz, vi, yi, yo, zh"


    return lang_vals.split(', ')


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False

    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

def main():
    #if check_password():
    # load deepl translator
    whisper_translator = whisperTranslator(st.secrets.api_keys.replicate)

    col1a, space1a, col1c = st.columns([8, 1, 1.2])

    # title
    with col1a:
        st.title("Transcribe")
        st.markdown("## An Audio-To-Text Transcription Application")

    # image
    with col1c:
        st.image("imgs/title.jpg")

    with st.expander("", expanded=True):
        col2a, space2a, col2b, space2b, col2c = st.columns([0.7, 0.1, 0.6, 0.1, 0.8])
        with col2a:
            st.markdown("### 1. Upload file")
            origin_language_known = st.checkbox("Origin language known")
            upload_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "ogg", "mp4"])
            if upload_file is not None:
                st.markdown("*listen your recording*")
                st.audio(upload_file, format="mp3")
            
            if origin_language_known:
                whisper_languages = get_language()
                origin_language = st.selectbox("Choose origin language", whisper_languages)
            
            with col2b:
                st.markdown("### 2. Transcribe Original")
                transcribe_original = st.button("Transcribe Original")
                if transcribe_original and len(upload_file) > 0:
                    if "result" in st.session_state:
                        del st.session_state.result

                    option = {"model": "large-v2", "translate": True, "language": origin_language} \
                        if origin_language_known else {"model": "large-v2", "translate": True}

                    result = whisper_translator.predict(audio=upload_file, **option)
                    if "result" not in st.session_state:
                        st.session_state.result = result
                    
                    if transcribe_original:
                        st.write(st.session_state.result["transcription"])

if __name__ == "__main__":
    main()
                
