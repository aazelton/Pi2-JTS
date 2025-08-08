
import json
import os
import re

# Path to the protocol JSON files (assume already extracted to Pi2)
PROTOCOL_DIR = "./protocol_modules"

# Load all protocol modules into memory
def load_protocols():
    knowledge_base = []
    for filename in os.listdir(PROTOCOL_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(PROTOCOL_DIR, filename), "r", encoding="utf-8") as f:
                knowledge_base.extend(json.load(f))
    return knowledge_base

# Match query to protocol entry using keywords
def find_matching_entry(query, knowledge_base):
    query_lower = query.lower()
    for entry in knowledge_base:
        if "context_required" in entry:
            if not all(word in query_lower for word in entry["context_required"]):
                continue
        if any(term in query_lower for term in [entry.get("medication", ""), entry.get("condition", "")]):
            return entry
    return None

# Evaluate dose based on weight (assume weight is always mentioned in query like '80 kg')
def extract_weight(query):
    match = re.search(r"(\d+)\s?kg", query.lower())
    return int(match.group(1)) if match else 70  # default to 70kg if not specified

# Generate response
def generate_response(entry, weight):
    try:
        dose = eval(entry.get("dose_formula", "0"), {}, {"weight": weight})
        response = entry["response_template"].format(dose=round(dose, 1), route=entry.get("route", ""))
        return response
    except:
        return "Unable to calculate dose. Please check the input."

# Main loop
def run_assistant():
    print("🩺 Crusu Assistant Ready. Type 'exit' to quit.")
    knowledge_base = load_protocols()
    while True:
        query = input("🧑‍⚕️ Query: ").strip()
        if query.lower() == "exit":
            break
        weight = extract_weight(query)
        entry = find_matching_entry(query, knowledge_base)
        if entry:
            print("🤖", generate_response(entry, weight))
        else:
            print("🤖 Sorry, I couldn't find a treatment match for that.")

if __name__ == "__main__":
    run_assistant()
