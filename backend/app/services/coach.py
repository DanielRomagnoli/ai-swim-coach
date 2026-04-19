def analyze_metrics(metrics):
    issues = []

    stroke_rate = metrics.get("stroke_rate", 0)
    symmetry = metrics.get("symmetry_score", 1)
    body_pos = metrics.get("body_position", 1)
    head_pos = metrics.get("head_position", 1)
    consistency = metrics.get("stroke_consistency", 1)

    if stroke_rate < 40:
        issues.append("Low stroke rate")

    if stroke_rate > 65:
        issues.append("Stroke rate too high")

    if symmetry < 0.8:
        issues.append("Poor stroke symmetry")

    if body_pos < 0.7:
        issues.append("Poor body position")

    if head_pos < 0.7:
        issues.append("Head position too low")

    if consistency < 0.75:
        issues.append("Inconsistent stroke timing")

    return issues


# -------------------------
# FEEDBACK
# -------------------------

def generate_feedback(issues):
    feedback_map = {
        "Low stroke rate": [
            "Increase tempo slightly while maintaining technique",
            "Focus on quicker hand recovery over the water"
        ],
        "Stroke rate too high": [
            "Slow down and focus on distance per stroke",
            "Emphasize a stronger pull phase"
        ],
        "Poor stroke symmetry": [
            "Ensure both arms are pulling evenly",
            "Focus on balanced body rotation"
        ],
        "Poor body position": [
            "Engage your core to keep hips high",
            "Keep your body flat and streamlined"
        ],
        "Head position too low": [
            "Lift your eyes slightly forward",
            "Avoid excessive downward head tilt"
        ],
        "Inconsistent stroke timing": [
            "Work on rhythm and stroke timing",
            "Focus on smooth, continuous movement"
        ]
    }

    feedback = []
    for issue in issues:
        feedback.extend(feedback_map.get(issue, []))

    return feedback


# -------------------------
# DRILLS
# -------------------------

def suggest_drills(issues):
    drill_map = {
        "Low stroke rate": [
            "Tempo trainer freestyle",
            "Fast arms drill"
        ],
        "Stroke rate too high": [
            "Catch-up drill",
            "Glide drill"
        ],
        "Poor stroke symmetry": [
            "Single arm freestyle",
            "3-3-3 drill"
        ],
        "Poor body position": [
            "Kick on side",
            "Superman glide"
        ],
        "Head position too low": [
            "Head-up freestyle",
            "Sight breathing drill"
        ],
        "Inconsistent stroke timing": [
            "6-kick switch drill",
            "Pause drill"
        ]
    }

    drills = []
    for issue in issues:
        drills.extend(drill_map.get(issue, []))

    return list(set(drills))  # remove duplicates


# -------------------------
# PRACTICES (🔥 MAIN UPGRADE)
# -------------------------

def generate_practice(issues):

    base_practices = [
        [
            "400 warm-up",
            "4x50 drill (choice)",
            "6x100 moderate pace",
            "200 cool down"
        ],
        [
            "300 warm-up",
            "8x50 build",
            "4x200 aerobic",
            "100 easy"
        ]
    ]

    issue_practices = []

    if "Low stroke rate" in issues:
        issue_practices.append([
            "400 warm-up",
            "6x50 fast arms",
            "8x100 descending",
            "200 cool down"
        ])

    if "Stroke rate too high" in issues:
        issue_practices.append([
            "300 warm-up",
            "6x50 catch-up drill",
            "6x100 focus DPS (distance per stroke)",
            "200 easy"
        ])

    if "Poor stroke symmetry" in issues:
        issue_practices.append([
            "400 warm-up",
            "8x50 single arm",
            "6x100 alternating focus left/right",
            "200 cool down"
        ])

    if "Poor body position" in issues:
        issue_practices.append([
            "300 warm-up",
            "6x50 kick on side",
            "6x100 pull buoy focus body line",
            "200 easy"
        ])

    if "Head position too low" in issues:
        issue_practices.append([
            "300 warm-up",
            "6x50 head-up freestyle",
            "6x100 breathing control",
            "200 cool down"
        ])

    if "Inconsistent stroke timing" in issues:
        issue_practices.append([
            "400 warm-up",
            "6x50 6-kick switch",
            "6x100 smooth rhythm focus",
            "200 easy"
        ])

    # combine + ensure 5 practices
    all_practices = issue_practices + base_practices

    # 🔥 ensure always 5
    while len(all_practices) < 5:
        all_practices.append(base_practices[len(all_practices) % len(base_practices)])

    return all_practices[:5]