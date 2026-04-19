from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def full_analysis(metrics):
    prompt = f"""
You are an elite swim coach.

Given these metrics:
{metrics}

Return JSON with:
- issues
- feedback (clear coaching advice)
- drills (specific drills)
- practice (structured swim set)
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    import json

    try:
        content = response.choices[0].message.content
        return json.loads(content)
    except:
        return {
            "issues": ["Could not parse AI response"],
            "feedback": content,
            "drills": [],
            "practice": []
        }