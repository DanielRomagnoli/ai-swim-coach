from openai import OpenAI

client = OpenAI()


def ask_coach(question, context=None):
    system_prompt = """
    You are an expert swim coach working with varsity swimmers.

    Provide:
    - clear, actionable advice
    - technique explanations
    - drills and training suggestions
    - Optimal practices
    - Elite dryland suggestions for the athlete

    
    Format respones:
    - Use short sections
    - Use bullet points
    - Aboid excessive headings
    - Keep it clean and readable
    """

    user_prompt = f"""
    Swimmer Data: {context}

    Question: {question}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content