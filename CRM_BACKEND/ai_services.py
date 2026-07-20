import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

load_dotenv()

# Setup Groq API Key and instantiate ChatGroq LLM
groq_api_key = os.getenv("GROQ_API")
if not groq_api_key:
    # Try alternate standard naming
    groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=groq_api_key,
    temperature=0.2
)

# 1. AI SEGMENTATION PIPELINE
segment_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an AI business analyst for a manufacturing CRM. "
        "Your task is to filter and segment a list of customer leads based on specific criteria defined by the user.\n\n"
        "Input Data (JSON format):\n{records_json}\n\n"
        "Segmentation Request: \"{criteria}\"\n\n"
        "Respond ONLY with a valid JSON object. Do not include markdown code block formatting (like ```json), introduction or explanations.\n"
        "The JSON object must follow this structure:\n"
        "{{\n"
        "  \"segmented_ids\": [list of matching record IDs],\n"
        "  \"reasoning\": \"A short summary explaining why these records match and highlighting common characteristics.\"\n"
        "}}\n"
        "CRITICAL REQUIREMENT: Do NOT include any code functions, calculations, or non-standard syntax like 'parseFloat' or 'parseInt' in the JSON values. All ID list values must be raw integers."
    )),
    ("user", "Please segment the leads now.")
])

segment_chain = segment_prompt | llm | StrOutputParser()

# 2. AI SUMMARIZATION PIPELINE
summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a professional CRM assistant. Summarize the provided lead profile, notes, and activity log.\n"
        "Highlight the candidate/client's main requirements, deal status, potential value, and suggest the next best action in 3 bullet points."
    )),
    ("user", "Lead Details:\n{details}")
])

summarize_chain = summarize_prompt | llm | StrOutputParser()

# 3. AI VISUALIZATION CONFIGURATION PIPELINE
visualize_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert AI data visualization assistant. "
        "Your task is to transform raw CRM metrics into a structured JSON configuration that can be rendered directly by charting libraries like Chart.js or Recharts.\n\n"
        "Raw Metrics:\n{raw_data}\n\n"
        "Requested Visualization Focus: {focus}\n\n"
        "Respond ONLY with a valid JSON object. Do not include markdown code block formatting or explanations.\n"
        "The JSON must have the following structure:\n"
        "{{\n"
        "  \"chartType\": \"bar\" | \"line\" | \"pie\" | \"doughnut\",\n"
        "  \"title\": \"A descriptive title for the chart\",\n"
        "  \"labels\": [list of strings for the x-axis or categories],\n"
        "  \"datasets\": [\n"
        "    {{\n"
        "      \"label\": \"Dataset Label\",\n"
        "      \"data\": [list of numeric values],\n"
        "      \"backgroundColor\": [list of hex colors matching labels or single color],\n"
        "      \"borderColor\": \"hex color\"\n"
        "    }}\n"
        "  ]\n"
        "}}\n"
        "CRITICAL REQUIREMENT: Do NOT include any code functions, calls, math calculations, or non-standard syntax like 'parseFloat()' or 'parseInt()' in the JSON. All values in 'data' must be raw numeric literals (either integers or floats, e.g. 0.0 or 1500). If stock level is 0, output exactly 0 or 0.0."
    )),
    ("user", "Generate the chart configuration.")
])

visualize_chain = visualize_prompt | llm | StrOutputParser()

# 4. SALES REPORT GENERATION PIPELINE
sales_report_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Senior Revenue Officer and Sales Analyst. "
        "Generate a comprehensive, executive-ready Sales Performance Report in Markdown format based on the provided raw CRM KPIs.\n\n"
        "Raw CRM Statistics:\n{stats_json}\n\n"
        "Report Guidelines:\n"
        "- Use a professional, premium tone with clear headings.\n"
        "- Include an Executive Summary, Key Highlights, Pipeline Health, Inventory/Stock Warning alerts (if any), Accounts Receivable & Outstanding Balance analysis, and 3 actionable Strategic Recommendations.\n"
        "- Make sure tables and bullet points are clean and readable."
    )),
    ("user", "Generate the sales report.")
])

sales_report_chain = sales_report_prompt | llm | StrOutputParser()


# Helper functions to run the pipelines
def clean_and_parse_json(text: str) -> Dict[str, Any]:
    import re
    import json
    cleaned = text.strip()
    # Remove markdown code block wrapping
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    cleaned = cleaned.strip()
    
    # Remove JavaScript functions parseFloat(...) and parseInt(...)
    cleaned = re.sub(r"parseFloat\(\s*([\d\.-]+)\s*\)", r"\1", cleaned)
    cleaned = re.sub(r"parseInt\(\s*([\d\.-]+)\s*\)", r"\1", cleaned)
    
    try:
        return json.loads(cleaned)
    except Exception as e:
        # Fallback to finding boundary braces
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end+1])
            except Exception:
                pass
        raise e

def run_segmentation(records: List[Dict[str, Any]], criteria: str) -> Dict[str, Any]:
    import json
    records_json = json.dumps(records, default=str)
    raw_output = segment_chain.invoke({"records_json": records_json, "criteria": criteria})
    try:
        return clean_and_parse_json(raw_output)
    except Exception as e:
        print(f"JSON parsing error in segmentation: {e}. Raw: {raw_output}")
        return {"segmented_ids": [], "reasoning": "Failed to parse AI segmentation. Invalid JSON structure."}

def run_summarization(details: str) -> str:
    return summarize_chain.invoke({"details": details})

def run_visualization(raw_data: Dict[str, Any], focus: str) -> Dict[str, Any]:
    import json
    raw_data_json = json.dumps(raw_data, default=str)
    raw_output = visualize_chain.invoke({"raw_data": raw_data_json, "focus": focus})
    try:
        return clean_and_parse_json(raw_output)
    except Exception as e:
        print(f"JSON parsing error in visualization: {e}. Raw: {raw_output}")
        return {
            "chartType": "bar",
            "title": "CRM Metrics Visualization",
            "labels": ["Unavailable"],
            "datasets": [
                {
                    "label": "Metric Value",
                    "data": [0],
                    "backgroundColor": ["#6366f1"],
                    "borderColor": "#6366f1"
                }
            ]
        }

def run_sales_report(stats: Dict[str, Any]) -> str:
    import json
    stats_json = json.dumps(stats, default=str)
    return sales_report_chain.invoke({"stats_json": stats_json})
