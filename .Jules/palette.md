## 2024-05-23 - Streamlit Component Styling
**Learning:** Streamlit's `st.markdown(unsafe_allow_html=True)` allows injecting custom HTML/CSS, which is crucial for styling elements that Streamlit's native API doesn't fully support, like custom download buttons.
**Action:** Use this pattern to improve the visual hierarchy of actions like "Download" or "Export" that default to plain links.

## 2024-05-23 - Session State Management for UX
**Learning:** Adding a "Clear History" button requires direct manipulation of `st.session_state` and a `st.rerun()`. This is a powerful pattern for giving users control over their session without needing a full page reload.
**Action:** Look for other areas where session state can be manipulated to provide "reset" or "undo" functionality.
