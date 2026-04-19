from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🔥 1. Analyze metrics → issues
def analyze_metrics(metrics):

    prompt = f"""
You are an elite swim coach.

Here are the swimmer's metrics extracted from video:

{metrics}

Your task:
- Identify the top 3–5 technique issues
- Be specific and technical (but clear)
- Focus on the biggest performance limitations

Return as a bullet list.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content


# 🔥 2. Generate feedback from issues
def generate_feedback(issues):

    prompt = f"""
You are an elite swim coach giving feedback to an athlete.

Here are the identified issues:

{issues}

Your task:
- Explain each issue simply
- Explain WHY it matters for performance
- Give 1 quick correction tip per issue

Keep it concise, clear, and encouraging.

Format as bullet points.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content


# 🔥 3. Suggest drills based on issues
def suggest_drills(issues):

    prompt = f"""
You are an elite swim coach.

Here are the swimmer’s issues:

{issues}

Your task:
- Suggest 3–5 drills to fix these issues
- For each drill:
    - Name
    - Short description
    - What it improves

Keep it concise and practical.

Format:
- Drill Name: ...
  Description: ...
  Focus: ...
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


# 🔥 4. Generate FULL custom practice
def generate_practice(issues, metrics, feedback):

    prompt = f"""
You are an elite swim coach designing a practice.

Swimmer analysis:

ISSUES:
{issues}

METRICS:
{metrics}

FEEDBACK:
{feedback}

Your task:
Create a 30–45 minute swim practice tailored to fix these issues.

Requirements:
- Structured: Warmup, Main Set, Cooldown
- Include specific distances and drills
- Each drill must connect to an issue
- Keep it realistic for a swimmer
- Be concise but high-quality

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
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content