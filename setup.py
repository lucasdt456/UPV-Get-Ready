import subprocess
import sys

import streamlit as st


@st.cache_resource
def setup_playwright():
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while setting up Playwright: {e}")


if __name__ == "__main__":
    setup_playwright()
