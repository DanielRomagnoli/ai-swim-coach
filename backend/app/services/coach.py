import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_full_analysis(metrics: dict):
    prompt = f"""
You are an elite swim coach.

A swimmer's stroke metrics are below:
{json.dumps(metrics, indent=2)}

Your job is to analyze the swimmer and return a structured response.

IMPORTANT:
- Be specific and actionable
- Sound like a real coach (not robotic)
- Keep feedback concise but high quality

Return STRICT JSON in this format:

{{
  "issues": [
    "short label of issue",
    "short label of issue"
  ],
  "feedback": "clear paragraph explaining what they are doing wrong and how to fix it",
  "drills": [
    "specific drill with explanation",
    "specific drill with explanation"
  ],
  "practice": "a short custom practice plan tailored to fix these issues"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # fast + cheap
        messages=[
            {"role": "system", "content": "You are a professional swim coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        print("❌ Failed to parse AI response:", content)
        return {
            "issues": ["Error parsing AI response"],
            "feedback": content,
            "drills": [],
            "practice": ""
        }