import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  hcpName: "",
  interactionType: "Meeting",
  interactionDate: "",
  interactionTime: "",
  attendees: "",
  discussionTopics: "",
  sentiment: "Positive",
  summary: "",
  outcomes: "",
  followUp: "",
  editingId: null,
  createdAt: "", 
};

const capitalize = (s) => s && s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();

const formSlice = createSlice({
  name: "form",
  initialState,
  reducers: {
    updateForm: (state, action) => {
      const payload = { ...action.payload };
      if (payload.discussionTopics && Array.isArray(payload.discussionTopics)) {
        payload.discussionTopics = payload.discussionTopics.join(', ');
      }
      if (payload.sentiment) {
        payload.sentiment = capitalize(payload.sentiment);
      }
      return { ...state, ...payload };
    },
    updateFormField: (state, action) => {
        const { field, value } = action.payload;
        if (field === 'sentiment') {
            state.sentiment = capitalize(value);
        } else {
            state[field] = value;
        }
    },
    resetForm: () => {
      return initialState;
    },
    startEdit: (state, action) => {
      const { id, data } = action.payload;
      let parsedTopics = [];
      if (data.discussion_topics && typeof data.discussion_topics === 'string') {
        try { parsedTopics = JSON.parse(data.discussion_topics); } catch (e) { console.error("Error parsing JSON:", e); }
      }

      state.hcpName = data.hcp_name || "";
      state.interactionType = data.interaction_type || "Meeting";
      state.interactionDate = data.interaction_date ? data.interaction_date.split('T')[0] : "";
      state.summary = data.summary || "";
      state.discussionTopics = Array.isArray(parsedTopics) ? parsedTopics.join(", ") : "";
      state.sentiment = capitalize(data.sentiment) || "Positive";
      state.outcomes = data.outcomes || "";
      state.followUp = data.follow_up || "";
      state.createdAt = data.created_at || "";
      state.editingId = id;
    },
    // NEW: Add this reducer to set only the active ID for chat context.
    setActiveId: (state, action) => {
        state.editingId = action.payload;
    },
  },
});

// NEW: Export the new action.
export const { updateForm, updateFormField, resetForm, startEdit, setActiveId } = formSlice.actions;
export default formSlice.reducer;