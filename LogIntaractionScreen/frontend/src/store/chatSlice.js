import { createSlice } from "@reduxjs/toolkit";

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    mode: "form", // "form" or "chat"
    history: [],
  },
  reducers: {
    toggleMode: (state) => {
      return { ...state, mode: state.mode === "form" ? "chat" : "form" };
    },
    addMessage: (state, action) => {
      return { ...state, history: [...state.history, action.payload] };
    },
    clearChat: (state) => {
      return { ...state, history: [] };
    },
  },
});

export const { toggleMode, addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
