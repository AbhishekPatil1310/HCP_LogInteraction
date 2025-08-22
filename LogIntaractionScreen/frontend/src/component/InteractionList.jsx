import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { startEdit } from "../store/formSlice";

const InteractionList = ({ refreshKey }) => {
  const dispatch = useDispatch();
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchInteractions = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/interactions");
      if (response.ok) {
        const data = await response.json();
        setInteractions(data);
      } else {
        console.error("Failed to fetch interactions.");
      }
    } catch (error) {
      console.error("Network error:", error);
    } finally {
      setLoading(false);
    }
  };

  // This useEffect now depends on refreshKey
  useEffect(() => {
    fetchInteractions();
  }, [refreshKey]);

  const handleEdit = (interaction) => {
    dispatch(startEdit({ id: interaction.id, data: interaction }));
  };

  if (loading) {
    return <div className="p-4 text-center text-gray-500">Loading interactions...</div>;
  }

  return (
    <div className="mt-8 space-y-4">
      <h3 className="text-xl font-semibold border-b pb-2">Recent Interactions</h3>
      {interactions.length === 0 ? (
        <p className="text-gray-500">No interactions logged yet.</p>
      ) : (
        interactions.map((interaction) => (
          <div key={interaction.id} className="p-4 border rounded-md shadow-sm bg-gray-50 flex justify-between items-center">
            <div>
              <p className="text-md font-medium text-gray-700">{interaction.hcp_name}</p>
              <p className="text-sm text-gray-500">
                {new Date(interaction.interaction_date).toLocaleDateString()}
              </p>
            </div>
            <button
              onClick={() => handleEdit(interaction)}
              className="px-4 py-2 text-sm bg-indigo-100 text-indigo-700 rounded-md hover:bg-indigo-200 transition-colors"
            >
              Edit
            </button>
          </div>
        ))
      )}
    </div>
  );
};

export default InteractionList;