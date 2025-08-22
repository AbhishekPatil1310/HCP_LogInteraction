AI-Powered HCP Interaction Logger
This is a full-stack web application designed to help medical representatives and other professionals log their interactions with Healthcare Professionals (HCPs). It features a modern, dual-interface system that allows for both traditional form-based data entry and an advanced AI-powered conversational assistant.

✨ Features
Dual Logging Modes: Log interactions using a detailed form or by simply describing the interaction to the AI assistant in natural language.

AI-Powered Data Extraction: Paste unstructured notes, and the AI will automatically parse the details and populate the form for you.

Conversational AI Assistant: The AI can ask clarifying questions to ensure all necessary details for a new log are captured.

Chat-Based Record Management: Use natural language commands to find, load, and update existing interaction records directly from the chat interface.

Centralized History: View all past interactions in a clean, filterable list and load any record for editing with a single click.

Modern Tech Stack: Built with a high-performance FastAPI backend and a responsive React frontend.

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Ensure you have the following software installed:

Python (version 3.8 or newer)

Node.js (version 16 or newer)

MySQL Server (or another compatible SQL database)

Backend Setup
Clone the Repository

Bash

git clone <your-repository-url>
cd <your-repository-url>/backend 
Create a Virtual Environment

Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install Dependencies
Create a requirements.txt file with the following content and run the install command.

requirements.txt:

annotated-types==0.7.0
anyio==4.10.0
certifi==2025.8.3
charset-normalizer==3.4.3
click==8.2.1
colorama==0.4.6
distro==1.9.0
fastapi==0.116.1
groq==0.31.0
h11==0.16.0
httpcore==1.0.9
httptools==0.6.4
httpx==0.28.1
idna==3.10
jsonpatch==1.33
jsonpointer==3.0.0
langchain-core==0.3.74
langchain-groq==0.3.7
langgraph==0.6.5
langgraph-checkpoint==2.1.1
langgraph-prebuilt==0.6.4
langgraph-sdk==0.2.2
langsmith==0.4.14
mysql-connector-python==9.4.0
orjson==3.11.2
ormsgpack==1.10.0
packaging==25.0
pydantic==2.11.7
pydantic_core==2.33.2
python-dotenv==1.1.1
PyYAML==6.0.2
requests==2.32.5
requests-toolbelt==1.0.0
sniffio==1.3.1
starlette==0.47.2
tenacity==9.1.2
typing-inspection==0.4.1
typing_extensions==4.14.1
urllib3==2.5.0
uvicorn==0.35.0
watchfiles==1.1.0
websockets==15.0.1
xxhash==3.5.0
zstandard==0.24.0


pip install -r requirements.txt
Set Up the Database

Log in to your MySQL server and create a new database.

SQL

CREATE DATABASE hcpinteractio;
Configure Environment Variables

Create a file named .env in the backend's root directory and add your credentials. Use the provided database password Abhishek@1259 or your own.

You will also need an API key from Groq.

.env:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=put your local mysql passwoard
DB_NAME=hcpinteractio
GROQ_API_KEY="Put your GROQ api key" 
Run the Backend Server

Bash

uvicorn main:app --reload --port 8000
The backend API will now be running at http://localhost:8000.

Frontend Setup
Navigate to Frontend Directory
From the project root, open a new terminal and navigate to the frontend folder.

Bash

cd ../frontend 
Install Dependencies

Bash

npm install
Run the Frontend App

Bash

npm run dev
The React application will open in your browser, usually at http://localhost:3000.

🤖 Using the AI Assistant
The AI Assistant provides several powerful ways to streamline your workflow.

Conversational Logging
Simply start typing in the chat box as if you were telling a colleague about your meeting. The AI will ask follow-up questions until it has enough information to create a log.

You: Met with Dr. Aruna Sharma today about the new trial results for Oncoboost. She seemed pretty positive.

AI: That's great to hear! What were the key topics you discussed? And what was the date of the meeting?

One-Shot Extraction
If you have pre-written notes, just paste them into the chat. The AI will read them, extract the relevant data, and instantly fill out the form on the left.

You: Quick note: Call with Dr. Patel on 2025-08-21. Discussed phase IV results and he mentioned patient onboarding issues. Follow up next week.

AI: I've filled out the form with the details from your message. Please review and confirm.

Managing Records via Chat
Use direct commands to find, load, and update interactions.

To find a record:

find my meeting with Dr. Patel from last week

To update a record (after loading it):

change the summary to reflect our new agreement

🎨 Design Choices & Assumptions
Technology Stack:

FastAPI was chosen for the backend due to its high performance, asynchronous support (crucial for handling LLM API calls without blocking), and automatic API documentation.

React was chosen for the frontend to create a modern, component-based, and highly interactive user interface. Redux Toolkit is used for state management to handle the complex state shared between the form, chat, and interaction list components.

LangGraph was selected over a simpler LangChain agent to build a robust, stateful AI. This allows for more complex, multi-step reasoning, such as deciding whether to use a tool, ask a question, or extract data.

Assumptions:

The application assumes a running MySQL instance is available and accessible.

It relies on the Groq API for fast LLM inference and assumes the user has a valid API key.

The frontend and backend run on different ports (3000 and 8000) and CORS is configured to allow them to communicate during development.

