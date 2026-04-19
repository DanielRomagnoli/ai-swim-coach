def analyze_metrics(metrics):
    issues = []

    stroke_rate = metrics["stroke_rate"]
    symmetry = metrics["symmetry"]
    alternation = metrics["alternation"]
    hip = metrics["hip"]
    head = metrics["head"]
    stroke_type = metrics["stroke_type"]

    # Stroke rate
    if stroke_type == "normal":
        if stroke_rate < 35:
            issues.append("Low stroke tempo")
    elif stroke_type == "catch-up":
        issues.append("Catch-up drill detected (focus on technique)")

    # Symmetry
    if symmetry > 0.2:
        issues.append("Stroke imbalance between arms")

    # Alternation (only for normal)
    if stroke_type == "normal" and alternation > 0.3:
        issues.append("Irregular stroke timing")

    # Hip sinking
    if hip > 0.07:
        issues.append("Hips dropping during stroke")

    # Head lifting
    if head < -0.03:
        issues.append("Head lifting during breathing")

    return issues

def generate_feedback(issues):
    feedback = []

    for issue in issues:
        if issue == "Low stroke tempo":
            feedback.append({
                "issue": issue,
                "why": "Lower stroke rate can reduce propulsion",
                "fix": "Increase tempo while maintaining technique"
            })

        elif issue == "Stroke imbalance between arms":
            feedback.append({
                "issue": issue,
                "why": "Imbalance creates drag and inefficiency",
                "fix": "Focus on equal pull strength and timing"
            })

        elif issue == "Hips dropping during stroke":
            feedback.append({
                "issue": issue,
                "why": "Sinking hips increase drag",
                "fix": "Engage core and maintain body line"
            })

        elif issue == "Head lifting during breathing":
            feedback.append({
                "issue": issue,
                "why": "Lifting head disrupts alignment",
                "fix": "Rotate head instead of lifting"
            })

        elif issue == "Catch-up drill detected (focus on technique)":
            feedback.append({
                "issue": issue,
                "why": "Drill emphasizes timing and body position",
                "fix": "Maintain strong body alignment during glide"
            })

    return feedback

def suggest_drills(issues):
    drills = []

    if "Stroke imbalance between arms" in issues:
        drills.append("Single-arm freestyle (focus weaker side)")
        drills.append("Catch-up drill")

    if "Hips dropping during stroke" in issues:
        drills.append("Kick with board (focus hips high)")
        drills.append("Streamline kicking")

    if "Head lifting during breathing" in issues:
        drills.append("Side kicking with rotation")
        drills.append("3-3-3 breathing drill")

    if "Low stroke tempo" in issues:
        drills.append("Tempo trainer sets")
        drills.append("Short interval sprints")

    return drills

def generate_practice(issues):
    return {
        "total": "4500m",
        "warmup": "400 swim, 200 kick, 200 pull",
        "preset": "6x100 @1:30 focus on technique",
        "drill": suggest_drills(issues),
        "main": "8x100 @1:20 maintain technique",
        "kick": "4x100 kick @2:00",
        "sprint": "8x25 @0:40 max effort",
        "warmdown": "200 easy"
    }