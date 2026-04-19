from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_practice(issues, metrics, feedback):

    prompt = f"""
You are an elite swim coach.

A swimmer uploaded a video and we analyzed their technique.

ISSUES:
{issues}

METRICS:
{metrics}

FEEDBACK:
{feedback}

Your task:
Create a 30-45 minute swim practice tailored to fix these issues.

Requirements:
- Be specific and actionable
- Include warmup, main set, and cooldown
- Include drill names and purpose (drills should be 25s and 50s)
- Explain WHY each drill is included
- Keep it concise but structured
- Make it sound like a real coach wrote it

Format:
Warmup:
- ...

Main Set:
- ...

Cooldown:
- ...

Coaching Notes:
- ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + cheap
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content