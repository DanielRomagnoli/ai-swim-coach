import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------
# MAIN AI CALL (ALL-IN-ONE)
# ------------------------
def analyze_all(metrics: dict):
    """
    Takes metrics and returns:
    - issues
    - feedback
    - drills
    - practice
    """

    prompt = f"""
You are an elite swim coach.

A swimmer's technique metrics are provided below.

Your job:
1. Identify key issues
2. Give clear coaching feedback
3. Suggest drills to fix each issue
4. Generate a 4–5km swim practice tailored to these issues

Keep everything structured and concise.

METRICS:
{metrics}

Return JSON with keys:
issues (list of strings)
feedback (list of strings)
drills (list of strings)
practice (list of strings)
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # fast + cheap
        messages=[
            {"role": "system", "content": "You are a professional swim coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    text = response.choices[0].message.content

    # 🔥 VERY IMPORTANT: safely parse JSON
    try:
        import json
        result = json.loads(text)
    except:
        # fallback if model doesn't return perfect JSON
        result = {
            "issues": ["Could not parse issues"],
            "feedback": [text],
            "drills": [],
            "practice": []
        }

    return result


# ------------------------
# WRAPPER FUNCTIONS (USED BY PIPELINE)
# ------------------------

def analyze_metrics(metrics):
    return analyze_all(metrics)["issues"]


def generate_feedback(issues, metrics=None):
    # optional metrics for better context
    return analyze_all(metrics or {"issues": issues})["feedback"]


def suggest_drills(issues, metrics=None):
    return analyze_all(metrics or {"issues": issues})["drills"]


def generate_practice(issues, metrics=None):
    return analyze_all(metrics or {"issues": issues})["practice"]


# ------------------------
# 🔥 BEST PRACTICE (USE THIS IN PIPELINE)
# ------------------------

def full_analysis(metrics):
    """
    USE THIS instead of calling 4 separate functions.
    Much faster (1 API call instead of 4)
    """
    return analyze_all(metrics)