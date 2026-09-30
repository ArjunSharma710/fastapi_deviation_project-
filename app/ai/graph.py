import json
import os
from typing import TypedDict

from dotenv import load_dotenv
from groq import Groq
from langgraph.graph import StateGraph, START, END


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_NAME = "openai/gpt-oss-120b"


class DeviationState(TypedDict, total=False):
    input_text: str

    site: str | None
    batch_number: str | None
    event_datetime: str | None
    description: str
    category: str | None

    impact: str
    severity: str
    severity_reason: str


def extract_deviation(state: DeviationState):
    prompt = f"""
You are an AI assistant for pharmaceutical deviation management.

Read the following deviation text and extract the relevant information.

Deviation text:
{state["input_text"]}

Return ONLY valid JSON.

Use exactly these fields:

{{
    "site": "string or null",
    "batch_number": "string or null",
    "event_datetime": "ISO datetime string or null",
    "description": "clear description of the deviation",
    "category": "Process, Equipment, Material, Documentation, Personnel, or Other"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    extracted = json.loads(response.choices[0].message.content)

    return extracted


def assess_deviation(state: DeviationState):
    prompt = f"""
You are an AI assistant helping assess a pharmaceutical manufacturing deviation.

Deviation information:

Site: {state.get("site")}
Batch Number: {state.get("batch_number")}
Date/Time: {state.get("event_datetime")}
Description: {state.get("description")}
Category: {state.get("category")}

Assess the initial impact and severity.

Return ONLY valid JSON.

Use exactly these fields:

{{
    "impact": "Low, Medium, or High",
    "severity": "Minor, Major, or Critical",
    "severity_reason": "short explanation of why this severity was recommended"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    assessment = json.loads(response.choices[0].message.content)

    return assessment


graph_builder = StateGraph(DeviationState)

graph_builder.add_node("extract_deviation", extract_deviation)
graph_builder.add_node("assess_deviation", assess_deviation)

graph_builder.add_edge(START, "extract_deviation")
graph_builder.add_edge("extract_deviation", "assess_deviation")
graph_builder.add_edge("assess_deviation", END)

deviation_graph = graph_builder.compile()


if __name__ == "__main__":
    test_input = """
    During API manufacturing batch B-2026-041,
    the reactor temperature exceeded the approved range of 20-25°C
    and reached 29°C for 15 minutes.
    The operator identified the issue during routine monitoring.
    """

    result = deviation_graph.invoke({
        "input_text": test_input
    })

    print("\n--- AI RESULT ---")
    print(result)