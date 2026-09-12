from typing import TypedDict
import json

from langgraph.graph import END, START, StateGraph

from app.services.ai.groq import llm


class ComplaintState(TypedDict):
    user_input: str
    complaint: dict
    risk_assessment: dict
    completeness: dict
    summary: str


def clean_json_response(response):
    text = response.content.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


def extract_complaint(state: ComplaintState):
    prompt = f"""
You are an AI assistant for a pharmaceutical Quality Management System (QMS).

Extract complaint information from the user's message.

User message:
{state["user_input"]}

Return ONLY valid JSON with these fields:

{{
    "complaint_source": null,
    "customer_name": null,
    "product_name": null,
    "product_strength": null,
    "batch_number": null,
    "manufacturing_date": null,
    "expiry_date": null,
    "affected_quantity": null,
    "complaint_type": null,
    "complaint_description": null
}}

Rules:
- Only extract information explicitly present in the user message.
- Do not invent missing information.
- Use null when information is unavailable.

- complaint_source represents the TYPE OF SOURCE through which the complaint was received.
  Examples: Pharmacy, Hospital, Doctor, Patient, Distributor, Retailer.

- customer_name represents the specific person or organization that reported the complaint.
  If the message says "Apollo Pharmacy reported...", set:
    complaint_source = "Pharmacy"
    customer_name = "Apollo Pharmacy"

- If a pharmacy, hospital, distributor, retailer, or other organization is explicitly named
  as the reporting party, preserve its exact name in customer_name.

- Never put the organization's specific name in complaint_source.
  complaint_source should contain only the source type.

- complaint_type should be a concise description of the problem.

- complaint_description should summarize the complaint using only information
  explicitly provided by the user.
"""

    response = llm.invoke(prompt)

    complaint = clean_json_response(response)

    return {
        "complaint": complaint
    }


def assess_risk(state: ComplaintState):
    complaint = state["complaint"]

    prompt = f"""
You are a pharmaceutical Quality Management System (QMS) complaint assessment assistant.

Assess the following customer complaint:

{complaint}

Return ONLY valid JSON:

{{
    "severity": "Minor | Major | Critical",
    "priority": "Low | Medium | High",
    "complaint_category": "string",
    "suggested_next_action": "string",
    "initial_risk_assessment": "string"
}}

Severity guidance:

- Minor:
  Use when the complaint appears unlikely to affect patient safety or product efficacy,
  such as a minor cosmetic or appearance issue with no evidence of contamination,
  degradation, incorrect labeling, incorrect dosage, or product mix-up.

- Major:
  Use when there is a reasonable possibility of affecting product quality,
  efficacy, or patient safety.

- Critical:
  Use when the complaint indicates a serious or potentially life-threatening risk,
  such as confirmed or strongly suspected contamination, incorrect medication,
  incorrect strength/dosage, serious adverse event, or dangerous product mix-up.

Priority guidance:

- Low: routine investigation with no immediate safety concern.
- Medium: investigation should be prioritized because product quality or integrity
  may potentially be affected.
- High: prompt containment/investigation is required because of significant
  potential safety, quality, or efficacy risk.

Important rules:

- Base the assessment only on the information provided.
- Do not invent test results, contamination, degradation, adverse events, or regulatory findings.
- A cosmetic/appearance complaint alone should not automatically be classified as Major or Critical.
- Do not recommend a recall or regulatory notification unless justified by the information.
- Suggested actions should be proportional to the assessed risk.
- The assessment is an initial AI recommendation and does not replace formal QA
  investigation or regulatory decision-making.
"""

    response = llm.invoke(prompt)

    risk = clean_json_response(response)

    return {
        "risk_assessment": risk
    }


def check_completeness(state: ComplaintState):
    complaint = state["complaint"]

    required_fields = [
        "complaint_source",
        "customer_name",
        "product_name",
        "product_strength",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
        "affected_quantity",
        "complaint_type",
        "complaint_description",
    ]

    missing_fields = [
        field
        for field in required_fields
        if not complaint.get(field)
    ]

    return {
        "completeness": {
            "is_complete": len(missing_fields) == 0,
            "missing_fields": missing_fields,
        }
    }


def generate_summary(state: ComplaintState):
    complaint = state["complaint"]
    risk = state["risk_assessment"]

    prompt = f"""
Create a concise professional summary of this pharmaceutical complaint.

Complaint:
{complaint}

Risk assessment:
{risk}

Rules:
- Use only the provided information.
- Do not invent facts.
- Keep the summary to 2-3 sentences.
- Mention the product, complaint, batch if available, and risk level when available.
- Return ONLY the summary text.
"""

    response = llm.invoke(prompt)

    return {
        "summary": response.content.strip()
    }


def edit_complaint(state: ComplaintState):
    existing_complaint = state["complaint"]
    user_input = state["user_input"]

    prompt = f"""
You are an AI assistant for a pharmaceutical Quality Management System (QMS).

An existing complaint has already been recorded.

Existing complaint:
{existing_complaint}

The user wants to correct or update the complaint using this message:

User message:
{user_input}

Identify ONLY the fields that the user explicitly wants to change.

Return ONLY valid JSON using exactly these fields:

{{
    "complaint_source": null,
    "customer_name": null,
    "product_name": null,
    "product_strength": null,
    "batch_number": null,
    "manufacturing_date": null,
    "expiry_date": null,
    "affected_quantity": null,
    "complaint_type": null,
    "complaint_description": null
}}

Rules:

- Return a value ONLY for fields explicitly being changed.
- Use null for fields that are not being changed.
- Do NOT copy unchanged fields.
- Do NOT invent information.
- Preserve the exact value provided by the user.

Examples:

If the user says:
"the batch number is BMX240602"

Return:
{{
    "complaint_source": null,
    "customer_name": null,
    "product_name": null,
    "product_strength": null,
    "batch_number": "BMX240602",
    "manufacturing_date": null,
    "expiry_date": null,
    "affected_quantity": null,
    "complaint_type": null,
    "complaint_description": null
}}

If the user says:
"affected quantity is 48 capsules"

Return:
{{
    "complaint_source": null,
    "customer_name": null,
    "product_name": null,
    "product_strength": null,
    "batch_number": null,
    "manufacturing_date": null,
    "expiry_date": null,
    "affected_quantity": "48 capsules",
    "complaint_type": null,
    "complaint_description": null
}}
"""

    response = llm.invoke(prompt)

    updates = clean_json_response(response)

    # IMPORTANT:
    # Always start from the complete existing complaint.
    updated_complaint = dict(existing_complaint)

    for field in [
        "complaint_source",
        "customer_name",
        "product_name",
        "product_strength",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
        "affected_quantity",
        "complaint_type",
        "complaint_description",
    ]:
        value = updates.get(field)

        if value is not None:
            updated_complaint[field] = value

    return {
        "complaint": updated_complaint
    }


# ============================================================
# INITIAL COMPLAINT GRAPH
# ============================================================

graph_builder = StateGraph(ComplaintState)

graph_builder.add_node("extract_complaint", extract_complaint)
graph_builder.add_node("assess_risk", assess_risk)
graph_builder.add_node("check_completeness", check_completeness)
graph_builder.add_node("generate_summary", generate_summary)

graph_builder.add_edge(
    START,
    "extract_complaint",
)

graph_builder.add_edge(
    "extract_complaint",
    "assess_risk",
)

graph_builder.add_edge(
    "assess_risk",
    "check_completeness",
)

graph_builder.add_edge(
    "check_completeness",
    "generate_summary",
)

graph_builder.add_edge(
    "generate_summary",
    END,
)

complaint_graph = graph_builder.compile()


# ============================================================
# EDIT COMPLAINT GRAPH
# ============================================================

edit_graph_builder = StateGraph(ComplaintState)

edit_graph_builder.add_node(
    "edit_complaint",
    edit_complaint,
)

edit_graph_builder.add_node(
    "assess_risk",
    assess_risk,
)

edit_graph_builder.add_node(
    "check_completeness",
    check_completeness,
)

edit_graph_builder.add_node(
    "generate_summary",
    generate_summary,
)

edit_graph_builder.add_edge(
    START,
    "edit_complaint",
)

edit_graph_builder.add_edge(
    "edit_complaint",
    "assess_risk",
)

edit_graph_builder.add_edge(
    "assess_risk",
    "check_completeness",
)

edit_graph_builder.add_edge(
    "check_completeness",
    "generate_summary",
)

edit_graph_builder.add_edge(
    "generate_summary",
    END,
)

edit_complaint_graph = edit_graph_builder.compile()