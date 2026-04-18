import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.graph.builder import build_graph
from app.schemas.state import AgentState
from app.schemas.api import AgentResponse, HealthResponse
from app.services.speech_to_text import transcribe_audio

app = FastAPI(title="Finance Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


@app.get("/", response_model=HealthResponse)
def root():
    return HealthResponse(status="ok")


@app.post("/text", response_model=AgentResponse)
async def process_text(text: str = Form(...)):
    try:
        state = AgentState(user_input=text)
        steps = []
        final_state = state

        for event in graph.stream(state):
            for node_name, node_output in event.items():
                steps.append(node_name)
                final_state = node_output

        expense_obj = final_state.expense
        summary_obj = final_state.summary_result

        payload = None
        if expense_obj is not None:
            payload = expense_obj.model_dump()
        elif summary_obj is not None:
            payload = summary_obj


        return AgentResponse(
            request_id=final_state.request_id,
            intent=final_state.intent,
            response=final_state.response or "No response generated.",
            execution_path=steps, 
            data=payload,
            errors=final_state.errors,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice", response_model=AgentResponse)
async def process_voice(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()

        filename = file.filename or "audio.mp3"
        _, ext = os.path.splitext(filename)
        suffix = ext if ext else ".mp3"

        transcribed_text = transcribe_audio(audio_bytes, suffix=suffix)

        state = AgentState(user_input=transcribed_text)
        steps = []
        final_state = state

        for event in graph.stream(state):
            for node_name, node_output in event.items():
                steps.append(node_name)
                final_state = node_output

        expense_obj = final_state.expense
        summary_obj = final_state.summary_result

        payload = {"transcribed_text": transcribed_text}
        if expense_obj is not None:
            payload = expense_obj.model_dump()
        elif summary_obj is not None:
            payload = summary_obj

        return AgentResponse(
            request_id=final_state.request_id,
            intent=final_state.intent,
            response=final_state.response or "No response generated.",
            execution_path=steps, 
            data=payload,
            errors=final_state.errors,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))