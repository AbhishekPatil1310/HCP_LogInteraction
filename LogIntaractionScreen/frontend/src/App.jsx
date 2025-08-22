import { useState } from "react";
import FormView from "./component/FormView";
import ChatView from "./component/ChatView";
import InteractionList from "./component/InteractionList";

const App = () => {
  // State to trigger a refresh in the list component
  const [refreshKey, setRefreshKey] = useState(0);

  // A function to be called on successful submission to trigger the refresh
  const handleFormSuccess = () => {
    setRefreshKey(prevKey => prevKey + 1); 
  };

  return (
    <div className="max-w-6xl mx-auto p-12 bg-gray-100 font-serif text-gray-800">
      <header className="text-center mb-10">
        <h1 className="text-4xl font-light mb-2">HCP Interaction Log</h1>
        <p className="text-lg text-gray-600">Document your professional interactions with ease.</p>
      </header>
      <div className="flex gap-10">
        {/* Left Panel: Form and List */}
        <div className="w-1/2 p-8 bg-white rounded-lg shadow-md border border-gray-200">
          <h2 className="text-2xl font-semibold mb-6 text-gray-700 border-b pb-2">Interaction Details</h2>
          {/* Pass the success handler to the form */}
          <FormView onSuccess={handleFormSuccess} />
          {/* Pass the refresh key to the list */}
          <InteractionList refreshKey={refreshKey} />
        </div>

        {/* Right Panel: Chat */}
        <div className="w-1/3 p-8 bg-white rounded-lg shadow-md border border-gray-200">
          <div className="h-1/8 flex flex-col">
            <h2 className="text-2xl font-semibold mb-2 text-gray-700">AI Assistant</h2>
            <p className="text-sm text-gray-500 mb-6">Log interactions using natural language.</p>
            <ChatView />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;