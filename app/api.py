import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.graph.builder import build_graph
from app.schemas.state import AgentState
from app.schemas.api import AgentResponse, HealthResponse
from app.services.speech_to_text import transcribe_audio
from app.services.notion_service import get_dashboard_summary
from app.services.insights import generate_insight

cached_insight = None

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
    global cached_insight 
    try:
        state = AgentState(user_input=text)
        steps = []
        final_state = state

        steps = []
        for event in graph.stream(state):
            for node_name in event.keys():
                steps.append(node_name)
        
        final_state = graph.invoke(state)
        
        if isinstance(final_state, dict):
            final_state = AgentState(**final_state)

        expense_obj = final_state.expense
        summary_obj = final_state.summary_result

        payload = {}
        if expense_obj is not None:
            payload = expense_obj.model_dump()
        elif summary_obj is not None:
            payload = summary_obj

        cached_insight = None
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
    global cached_insight 
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
            for node_name in event.keys():
                steps.append(node_name)
        final_state = graph.invoke(state)

        # Convert dict → AgentState if needed
        if isinstance(final_state, dict):
            final_state = AgentState(**final_state)

        expense_obj = final_state.expense
        summary_obj = final_state.summary_result

        payload = {
            "transcribed_text": transcribed_text
        }

        if expense_obj is not None:
            payload.update(expense_obj.model_dump())

        elif summary_obj is not None:
            payload.update(summary_obj)
            print("FINAL RESPONSE:", {
                    "request_id": final_state.request_id,
                    "intent": final_state.intent,
                    "response": final_state.response,
                    "execution_path": steps,
                    "data": payload,
                    "errors": final_state.errors,
                })
        
        cached_insight = None
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
    


@app.get("/summary")
def summary():
    global cached_insight
    data = get_dashboard_summary()
    if not cached_insight:
        if data.get("total_spend", 0) > 0:
            try:
                cached_insight = generate_insight(data)
            except Exception:
                cached_insight = "Unable to generate insights right now."
        else:
            cached_insight = "Start tracking expenses to get insights."

    data["insight"] = cached_insight

    return data