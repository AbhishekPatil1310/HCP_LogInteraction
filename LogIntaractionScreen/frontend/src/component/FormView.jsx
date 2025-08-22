import { useSelector, useDispatch } from "react-redux";
import { useState, useRef } from "react";
import { updateFormField, resetForm, setActiveId } from "../store/formSlice";
import MicIcon from "./icons/MicIcon";
import SearchIcon from "./icons/SearchIcon";
import PlusIcon from "./icons/PlusIcon";

const FormView = ({ onSuccess }) => {
  const formState = useSelector((state) => state.form);
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const submitButtonRef = useRef(null);

  const isEditing = formState.editingId !== null;

  const handleChange = (e) => {
    dispatch(updateFormField({ field: e.target.name, value: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const url = isEditing
      ? `http://localhost:8000/api/edit-interaction/${formState.editingId}`
      : "http://localhost:8000/api/log-interaction/form";
    const method = isEditing ? "PUT" : "POST";

    const payload = {
      ...formState,
      discussionTopics: formState.discussionTopics
        ? formState.discussionTopics.split(",").map((t) => t.trim())
        : [],
    };
    delete payload.editingId;
    delete payload.interactionTime;
    delete payload.attendees;
    delete payload.createdAt;

    try {
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();
      if (response.ok) {
        setMessage(
          isEditing
            ? "Interaction updated successfully!"
            : "Interaction logged successfully!"
        );
        
        // This is the corrected logic:
        dispatch(resetForm()); 
        if (result.data && !isEditing) {
            dispatch(setActiveId(result.data.id));
        }
        if (onSuccess) onSuccess();
        
      } else {
        setMessage(`Error: ${result.detail || "Failed to submit."}`);
      }
    } catch {
      setMessage("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  window.triggerFormSubmit = () => {
    submitButtonRef.current?.click();
  };

  return (
    <div id="form-view">
      {message && (
        <div className={`p-4 mb-4 rounded-md ${message.startsWith("Error") ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`}>
          {message}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-6 text-gray-800">
        
        {isEditing && formState.createdAt && (
          <div className="pb-2 text-xs text-gray-500 border-b">
            <strong>Logged on:</strong> {new Date(formState.createdAt).toLocaleString('en-IN', { dateStyle: 'long', timeStyle: 'short' })}
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">HCP Name</label>
            <input
              name="hcpName"
              value={formState.hcpName || ""}
              onChange={handleChange}
              placeholder="Search or select HCP..."
              required
              className="p-3 border rounded-md w-full bg-gray-50 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Interaction type</label>
            <select
              name="interactionType"
              value={formState.interactionType || ""}
              onChange={handleChange}
              required
              className="p-3 border rounded-md w-full bg-gray-50 focus:outline-none focus:border-indigo-500"
            >
              <option>Meeting</option>
              <option>Phone Call</option>
              <option>Email</option>
              <option>Conference</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Date</label>
            <input
              type="date"
              name="interactionDate"
              value={formState.interactionDate || ""}
              onChange={handleChange}
              required
              className="p-3 border rounded-md w-full bg-gray-50 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Time</label>
            <input
              type="time"
              name="interactionTime"
              value={formState.interactionTime || ""}
              onChange={handleChange}
              required
              className="p-3 border rounded-md w-full bg-gray-50 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Attendees</label>
          <input
            name="attendees"
            value={formState.attendees || ""}
            onChange={handleChange}
            placeholder="Enter names or search..."
            className="p-3 border rounded-md w-full bg-gray-50"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Topics Discussed</label>
          <div className="relative">
            <textarea
              name="discussionTopics"
              value={formState.discussionTopics || ""}
              onChange={handleChange}
              placeholder="Enter key discussion points..."
              className="p-3 border rounded-md w-full h-24 resize-none bg-gray-50"
            />
            <button type="button" className="absolute bottom-3 right-3 text-gray-400 hover:text-gray-600">
              <MicIcon />
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2 text-indigo-600 text-sm cursor-pointer">
          <MicIcon />
          <span>Summarize from Voice Note (Requires Consent)</span>
        </div>
        <div>
          <h3 className="text-base font-semibold text-gray-700 mb-2">Materials Shared / Samples Distributed</h3>
          <div className="flex items-center justify-between mb-2 p-3 bg-gray-50 rounded-md border border-gray-200">
            <div className="flex-1">
              <p className="text-sm font-medium">Materials Shared</p>
              <p className="text-xs text-gray-400">No materials added.</p>
            </div>
            <button type="button" className="flex items-center text-indigo-600 font-medium">
              <SearchIcon className="mr-1" />
              Search/Add
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md border border-gray-200">
            <div className="flex-1">
              <p className="text-sm font-medium">Samples Distributed</p>
              <p className="text-xs text-gray-400">No samples added.</p>
            </div>
            <button type="button" className="flex items-center text-indigo-600 font-medium">
              <PlusIcon className="mr-1" />
              Add Sample
            </button>
          </div>
        </div>
        <div>
          <h3 className="text-base font-semibold text-gray-700 mb-2">Observed/Inferred HCP Sentiment</h3>
          <div className="flex space-x-6">
            <label className="flex items-center text-sm cursor-pointer">
              <input 
                type="radio" 
                name="sentiment" 
                value="Positive" 
                checked={formState.sentiment === 'Positive'} 
                onChange={handleChange} 
                className="mr-2" 
              /> Positive
            </label>
            <label className="flex items-center text-sm cursor-pointer">
              <input 
                type="radio" 
                name="sentiment" 
                value="Neutral" 
                checked={formState.sentiment === 'Neutral'} 
                onChange={handleChange} 
                className="mr-2" 
              /> Neutral
            </label>
            <label className="flex items-center text-sm cursor-pointer">
              <input 
                type="radio" 
                name="sentiment" 
                value="Negative" 
                checked={formState.sentiment === 'Negative'} 
                onChange={handleChange} 
                className="mr-2" 
              /> Negative
            </label>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Outcomes</label>
          <textarea
            name="outcomes"
            value={formState.outcomes || ""}
            onChange={handleChange}
            placeholder="Key outcomes or agreements..."
            className="p-3 border rounded-md w-full h-24 resize-none bg-gray-50"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Follow-up Actions</label>
          <textarea
            name="followUp"
            value={formState.followUp || ""}
            onChange={handleChange}
            placeholder="Enter next steps or tasks..."
            className="p-3 border rounded-md w-full h-24 resize-none bg-gray-50"
          />
        </div>
        <div className="text-sm mt-4">
          <p className="font-semibold text-gray-700 mb-2">AI Suggested Follow-ups</p>
          <ul className="space-y-1 text-indigo-600">
            <li>+ Schedule follow-up meeting in 2 weeks</li>
            <li>+ Send Oncoboost Phase III PDF</li>
            <li>+ Add Dr. Sharma to advisory board invite list</li>
          </ul>
        </div>
        <div className="flex justify-end mt-6">
          <button
            ref={submitButtonRef}
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg shadow-md hover:bg-indigo-700 transition-colors"
          >
            {loading ? "Submitting..." : (isEditing ? "Update" : "Log")}
          </button>
        </div>
      </form>
    </div>
  );
};

export default FormView;