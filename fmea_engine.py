import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Llista completa segons la teva imatge
TESTS_LIST = [
    "DESIGN CHANGE", "DIM & WORST CASE", "SIMULATION", "REDESIGN", "CHARACTERIZE",
    "CPPP", "WORST CASING-TOLERANCE", "FUNCTIONALITY TEST", "DOE - SIGNAL LOSS TESTS",
    "OOBE & INSTALL", "SYSTEM TEST WORKFLOWS", "SPECS PERFORMANCE XPUT", "SIT E2E APP",
    "USER ABUSE - TORTURE", "HALT - HIGH ACCELERATED", "BEST-BOARDS STRIFE TEST",
    "ALT - LIFE TEST", "ROBUSTNESS", "REGS EMC", "REGS SAFETY", "USABILITY",
    "SW-FW TESTS", "DATA QUALITY", "VENDOR PQAP", "HASS MFG TESTS", "MFG LINE TESTS",
    "MFG PPA", "MAINTENANCE", "DIAGNOSABILITY", "SERVICEABILITY"
]

def clamp(value):
    try: return max(1, min(5, int(value)))
    except: return 3

def build_prompt(form_data, part):
    tests_str = ", ".join(TESTS_LIST)
    return f"""
Act as a Senior Reliability and Safety Engineer specialized in FMEA (Failure Mode and Effects Analysis).
Your goal is to provide a HIGH-ACCURACY technical analysis for the following product:

PRODUCT: {form_data.get('object_name')}
PART TO ANALYZE: {part}
TECHNICAL SPECS: {form_data.get('specs')}
SAFETY REQS: {form_data.get('safety')}

INSTRUCTIONS:
1. Identify realistic failure modes based on engineering physics and historical reliability data.
2. For each failure mode, assign Severity (S), Occurrence (O), and Detectability (D) using a 1-5 scale according to AIAG/VDA standards.
3. SOURCES/LINKS: Provide a VALID technical URL or reference (ISO, IEC, IEEE standards, or manufacturer whitepapers) that justifies the failure mode or the mitigation strategy. Avoid generic URLs if possible.
4. INVESTIGATION & TESTING: From the list below, select ONLY the tests that are technically relevant to validate or mitigate THIS specific failure mode. 

AVAILABLE TESTS:
{tests_str}

RETURN FORMAT (JSON ONLY):
[
  {{
    "Failure": "Technical description of the failure",
    "Function": "What the part is supposed to do",
    "Failure Mode": "degradation | partial degradation | total failure-breakage",
    "Effects": "Impact on the system/user",
    "Causes": "Root physical or logical cause",
    "Sources": "Reference name (e.g., IEC 60601-1)",
    "Severity": 1-5,
    "Occurrence": 1-5,
    "Detectability": 1-5,
    "Cost": 100,
    "Links": "Direct URL or standard reference link",
    "Applied_Tests": ["EXACT NAME FROM THE TEST LIST"]
  }}
]
"""

def generate_fmea(form_data):
    parts = form_data.get("piezas", "").split(",")
    all_failures = []
    
    for part in parts:
        part = part.strip()
        if not part: continue
        
        # Utilitzem gpt-4o per a una millor cerca de dades tècniques
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precise engineering assistant. You only output valid JSON based on technical standards."},
                {"role": "user", "content": build_prompt(form_data, part)}
            ],
            temperature=0.1 # Temperatura baixa per evitar "al·lucinacions" i ser més determinista
        )
        
        try:
            # Netegem la resposta per si la IA afegeix format Markdown
            raw_content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            failures = json.loads(raw_content)
            
            for f in failures:
                f["Part"] = part
                f["Severity"] = clamp(f.get("Severity"))
                f["Occurrence"] = clamp(f.get("Occurrence"))
                f["Detectability"] = clamp(f.get("Detectability"))
                all_failures.append(f)
        except Exception as e:
            print(f"Error processant part {part}: {e}")
            continue
            
    return all_failures
