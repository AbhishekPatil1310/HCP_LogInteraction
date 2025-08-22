import { useSelector, useDispatch } from "react-redux";
import { toggleMode } from "../store/chatSlice";

const ToggleSwitch = () => {
  const mode = useSelector((state) => state.chat.mode);
  const dispatch = useDispatch();

  return (
    <label className="relative inline-block w-32 h-10">
      <input
        type="checkbox"
        checked={mode === "chat"}
        onChange={() => dispatch(toggleMode())}
        className="opacity-0 w-0 h-0 peer"
      />
      <span className="absolute cursor-pointer top-0 left-0 right-0 bottom-0 bg-gray-200 
        transition-colors duration-300 rounded-full flex items-center justify-between p-1 
        peer-checked:bg-indigo-600">
        <span className={`text-sm font-medium ${mode === "form" ? "text-white" : "text-gray-500"}`}>
          Form
        </span>
        <span className={`text-sm font-medium ${mode === "chat" ? "text-white" : "text-gray-500"}`}>
          Chat
        </span>
        <div className="absolute w-1/2 h-full bg-white rounded-full shadow-lg transition-transform duration-300 transform peer-checked:translate-x-full"></div>
      </span>
    </label>
  );
};

export default ToggleSwitch;
