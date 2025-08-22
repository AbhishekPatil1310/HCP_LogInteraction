import { useState, useEffect, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { addMessage } from "../store/chatSlice";
import { startEdit, updateForm, resetForm } from "../store/formSlice"; // Make sure resetForm is imported
import SendIcon from "./icons/SendIcon";

const ChatView = () => {
    const chatHistory = useSelector((state) => state.chat.history);
    const { editingId } = useSelector((state) => state.form);
    const dispatch = useDispatch();
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [choices, setChoices] = useState([]);
    const [needsConfirmation, setNeedsConfirmation] = useState(false);
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatHistory, needsConfirmation]);

    const handleSelectChoice = (interaction) => {
        dispatch(startEdit({ id: interaction.id, data: interaction }));
        dispatch(addMessage({ sender: 'agent', text: `Great, I've loaded the interaction with ${interaction.hcp_name} from ${new Date(interaction.interaction_date).toLocaleDateString()}. How can I help you update it?` }));
        setChoices([]);
    };
    
    const handleConfirmSave = () => {
        if (window.triggerFormSubmit) {
            window.triggerFormSubmit();
        }
        setNeedsConfirmation(false);
        dispatch(addMessage({ sender: 'user', text: 'Yes, save it.' }));
        dispatch(addMessage({ sender: 'agent', text: 'Saving the interaction details now.' }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = { sender: "user", text: input };
        dispatch(addMessage(userMessage));
        const currentInput = input;
        setInput("");
        setLoading(true);
        setNeedsConfirmation(false);
        setChoices([]);

        // Step 1: Check for high-priority tool commands first.
        const isUpdateRequest = /update|change|edit|modify/.test(currentInput.toLowerCase());
        const isFetchRequest = /find|load|get|populate|fetch/.test(currentInput.toLowerCase());

        if ((editingId && isUpdateRequest) || isFetchRequest) {
            let endpoint = isFetchRequest ? "/api/populate-form-from-chat" : "/api/update-from-chat";
            try {
                const response = await fetch(`http://localhost:8000${endpoint}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: currentInput, chatHistory: chatHistory, interactionId: editingId }),
                });
                const result = await response.json();

                if (endpoint === "/api/populate-form-from-chat" && result.data) {
                    if (result.data.status === 'success') {
                        dispatch(startEdit({ id: result.data.data.id, data: result.data.data }));
                        dispatch(addMessage({ sender: 'agent', text: "I've populated the form with the details." }));
                    } else if (result.data.status === 'multiple_found') {
                        dispatch(addMessage({ sender: 'agent', text: "I found a few matching interactions. Please select the correct one:" }));
                        setChoices(result.data.data);
                    } else {
                        dispatch(addMessage({ sender: 'agent', text: "Sorry, I couldn't find any matching interactions." }));
                    }
                } else {
                    dispatch(addMessage({ sender: "agent", text: result.response }));
                }
            } catch (error) {
                dispatch(addMessage({ sender: "agent", text: "Sorry, something went wrong with that command." }));
            } finally {
                setLoading(false);
            }
            return;
        }

        // Step 2: If no command, try proactive form-filling.
        try {
            const extractResponse = await fetch("http://localhost:8000/api/extract-and-populate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: currentInput }),
            });
            const extractResult = await extractResponse.json();

            if (extractResult.status === 'success' && extractResult.data) {
                // --- THIS IS THE CORRECTED LOGIC ---
                // First, reset the form completely to clear any old context (like editingId).
                dispatch(resetForm()); 
                
                // Then, populate the form with the newly extracted data.
                dispatch(updateForm(extractResult.data)); 
                // --- END OF CORRECTION ---

                dispatch(addMessage({ sender: 'agent', text: "I've filled out the form with the details from your message. Please review and confirm." }));
                setNeedsConfirmation(true);
                setLoading(false);
                return;
            }
        } catch (error) {
            console.error("Extraction attempt failed, proceeding to conversational chat.", error);
        }

        // Step 3: If all else fails, use the default conversational endpoint.
        try {
            const response = await fetch(`http://localhost:8000/api/log-interaction/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: currentInput, chatHistory: chatHistory, interactionId: editingId }),
            });
            const result = await response.json();
            dispatch(addMessage({ sender: "agent", text: result.response }));
        } catch (error) {
             dispatch(addMessage({ sender: "agent", text: "Sorry, I'm having trouble connecting." }));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex-grow p-4 bg-gray-50 border rounded-t-md overflow-y-auto min-h-0">
                {chatHistory.map((msg, index) => (
                    <div key={index} className={`mb-4 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`p-3 rounded-lg max-w-lg ${msg.sender === 'user' ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-800'}`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {choices.length > 0 && (
                    <div className="space-y-2 my-2">
                        {choices.map(choice => (
                            <button key={choice.id} onClick={() => handleSelectChoice(choice)} className="w-full text-left p-2 border rounded-md bg-white hover:bg-indigo-50">
                                <p className="font-semibold">{choice.hcp_name} - {new Date(choice.interaction_date).toLocaleDateString()}</p>
                                <p className="text-sm text-gray-600 truncate">{choice.summary}</p>
                            </button>
                        ))}
                    </div>
                )}
                {needsConfirmation && (
                    <div className="my-2 p-2 bg-indigo-100 rounded-md">
                        <button onClick={handleConfirmSave} className="w-full p-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
                            Click Here to Save to Database
                        </button>
                    </div>
                )}
                {loading && <div className="text-center text-gray-500">Agent is thinking...</div>}
                <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleSubmit} className="flex p-2 border-t bg-white rounded-b-md">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Describe an interaction to get started..."
                    className="flex-grow p-2 border-none focus:outline-none"
                    disabled={loading}
                />
                <button type="submit" className="p-2 text-indigo-500 disabled:text-gray-400" disabled={loading}>
                    <SendIcon />
                </button>
            </form>
        </div>
    );
};

export default ChatView;