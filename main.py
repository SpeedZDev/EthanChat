from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_community.document_loaders import PyMuPDFLoader
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import tempfile


load_dotenv()

if "ChatHistory" not in st.session_state:
    st.session_state["ChatHistory"] = []

AgentModel = ChatOpenAI(model="gpt-5.4", max_completion_tokens=2000, temperature=0.1)
WebSearchTool = TavilySearch(max_result=5, topic="general")
Tools = [WebSearchTool]
SystemPrompt = "You are a General AI Information Assistant that Answers Questions and helps Users On general Everday Actives. When Questions are asks you find the *MOST UP TO DATE* sources from the current date regargding the subject and put these sources that use in a neatly fromatted list! When User Uploads documents Scan these doucments and do as the user asks with these documents"
Model = create_agent(AgentModel, tools=Tools, system_prompt=SystemPrompt)

def LoadUploadedFiles(UploadedFiles):
    if UploadedFiles is None:
        return ""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as TemporaryFile:
        TemporaryFile.write(UploadedFiles.read())
        TemporaryPath = TemporaryFile.name
        
    loader = PyMuPDFLoader(TemporaryPath, mode="single",pages_delimiter="\n\n Page Break \n\n")
    docs = loader.load()
    return docs[0].page_content

def ProcessChat(model, FileContext = ""):
    messages = []
   
    if FileContext:
        messages.append(HumanMessage(content=f"Uploaded File Content: {FileContext}"))
   
    for message in st.session_state["ChatHistory"]:
        if message["Role"] == "user":
            messages.append(HumanMessage(content=message["Content"]))
        
        if message["Role"] == "assistant":
            messages.append(AIMessage(content=message["Content"]))
        
    Response = model.invoke({"messages": messages})
    return Response

st.title("Big Brother")

for message in st.session_state["ChatHistory"]:
    with st.chat_message(message["Role"]):
        st.markdown(message["Content"])
    

UserQuery = st.chat_input(placeholder="Enter Prompt Here Or Upload files")
FileUploader = st.file_uploader(label="Upload Files Here", type="pdf")

if UserQuery != "quit" and UserQuery:
    with st.chat_message("user"):
        st.markdown(UserQuery)
    
    st.session_state["ChatHistory"].append({"Role": "user", "Content": UserQuery})
    
    FileContext = LoadUploadedFiles(FileUploader)
    Response = ProcessChat(Model, FileContext)

    with st.chat_message("assistant"):
        st.markdown(Response["messages"][-1].content)
       
        
    st.session_state["ChatHistory"].append({"Role": "assistant","Content": Response["messages"][-1].content})
    st.write(st.session_state["ChatHistory"])
    





    

