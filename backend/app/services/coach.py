def analyze_metrics(metrics):
    issues = []

    if metrics.get("stroke_rate", 0) < 40:
        issues.append("Low stroke rate")

    if metrics.get("symmetry_score", 1) < 0.8:
        issues.append("Poor stroke symmetry")

    if metrics.get("body_position", 0) < 0.7:
        issues.append("Body position too low")

    return issues


def generate_feedback(issues):
    feedback = []

    for issue in issues:
        if issue == "Low stroke rate":
            feedback.append("Increase tempo slightly while maintaining form")

        if issue == "Poor stroke symmetry":
            feedback.append("Focus on even left/right arm pull")

        if issue == "Body position too low":
            feedback.append("Engage core and keep hips higher")

    return feedback


def suggest_drills(issues):
    drills = []

    if "Low stroke rate" in issues:
        drills.append("Tempo trainer freestyle")

    if "Poor stroke symmetry" in issues:
        drills.append("Single arm freestyle")

    if "Body position too low" in issues:
        drills.append("Kick on side drill")

    return drills


def generate_practice(issues):
    return [
        "400 warm-up",
        "6x50 drill (focus on technique)",
        "8x100 moderate pace",
        "200 cool down"
    ]