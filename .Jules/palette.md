## 2024-05-23 - Interactive Sidebar Examples
**Learning:** `st.chat_input` resets on rerun, making it tricky to populate from other widgets like sidebar buttons.
**Action:** Use a "one-way" data flow where button clicks override the prompt variable, or use session state carefully to persist the "intent" to query.
