def calculate_ats_score(skills):

    total_possible_skills = 10

    score = (len(skills) / total_possible_skills) * 100

    if score > 100:
        score = 100

    return round(score)