def analyze_metrics(metrics):
    issues = []

    sr = metrics.get("stroke_rate", 0)
    sym = metrics.get("symmetry", 1)
    alt = metrics.get("alternation", 1)
    body = metrics.get("body_position", 1)
    head = metrics.get("head_position", 1)
    cons = metrics.get("consistency", 1)

    if sr < 40:
        issues.append("Low stroke rate")

    if sr > 70:
        issues.append("Stroke rate too high")

    if sym < 0.85:
        issues.append("Poor stroke symmetry")

    if alt < 0.85:
        issues.append("Poor stroke timing")

    if body < 0.75:
        issues.append("Poor body position")

    if head < 0.75:
        issues.append("Head position off")

    if cons < 0.75:
        issues.append("Inconsistent stroke rhythm")

    if not issues:
        issues.append("Minor technique improvements")

    return issues


def generate_feedback(issues):
    feedback_map = {
        "Low stroke rate": [
            "Increase tempo slightly",
            "Speed up recovery phase"
        ],
        "Stroke rate too high": [
            "Slow down stroke",
            "Focus on distance per stroke"
        ],
        "Poor stroke symmetry": [
            "Balance left and right pull",
            "Focus on even rotation"
        ],
        "Poor stroke timing": [
            "Work on alternating rhythm",
            "Smooth out stroke transitions"
        ],
        "Poor body position": [
            "Keep hips higher",
            "Engage core for alignment"
        ],
        "Head position off": [
            "Keep head neutral",
            "Avoid lifting or dropping head"
        ],
        "Inconsistent stroke rhythm": [
            "Maintain steady tempo",
            "Focus on smooth cadence"
        ],
        "Minor technique improvements": [
            "Good swim — refine technique",
            "Focus on efficiency"
        ]
    }

    feedback = []
    for issue in issues:
        feedback.extend(feedback_map.get(issue, []))

    return feedback


def suggest_drills(issues):
    drill_map = {
        "Low stroke rate": ["Fast arms drill"],
        "Stroke rate too high": ["Catch-up drill"],
        "Poor stroke symmetry": ["Single arm freestyle"],
        "Poor stroke timing": ["6-kick switch drill"],
        "Poor body position": ["Kick on side"],
        "Head position off": ["Head-up freestyle"],
        "Inconsistent stroke rhythm": ["Tempo trainer"],
    }

    drills = []
    for issue in issues:
        drills.extend(drill_map.get(issue, []))

    return list(set(drills))


def generate_practice(issues):
    practices = []

    if "Low stroke rate" in issues:
        practices.append(["6x50 fast arms", "8x100 descend"])

    if "Poor stroke symmetry" in issues:
        practices.append(["8x50 single arm", "6x100 alt focus"])

    if "Poor body position" in issues:
        practices.append(["6x50 kick on side", "6x100 pull"])

    # fallback
    while len(practices) < 5:
        practices.append(["400 swim", "4x100 moderate", "200 easy"])

    return practices[:5]