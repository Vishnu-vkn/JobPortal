#ATS Logic
from decimal import Decimal

def calculate_ats_score(job,candidate):
    #calculate ats score between a job and a candidate
    #convert comma seperated skills into python lists 
    job_skills=[
        skill.strip().lower()
        for skill in job.skills.split(",")
        if skill.strip()
    ]

    candidate_skills=[
        skill.strip().lower()
        for skill in candidate.skills.split(",")
        if skill.strip()
    ]

    #find matchedskills
    matched_skills=[]
    for skill in job_skills:
        if skill in candidate_skills:
            matched_skills.append(skill)

    #skills score(70 marks)
    if job_skills:
        skills_score=(len(matched_skills)/len(job_skills))*70
    else:
        skills_score=0

    #Experience score(20marks)
    if candidate.experience>=job.experience:
        experience_score=20
    elif job.experience>0:
        experience_score=(float(candidate.experience)/float(job.experience))*20 
        
    else:
        experience_score=20

    #Education Score
    if(
        candidate.education and candidate.education.lower()=="bachelor"
    ):
        education_score=10
    else:
        education_score=5

    total_score=round(skills_score+experience_score+education_score,2)

    print("Job Skills:", job_skills)
    print("Candidate Skills:", candidate_skills)
    print("Matched Skills:", matched_skills)
    print("Skills Score:", skills_score)
    print("Experience Score:", experience_score)
    print("Education Score:", education_score)
    print("Total:", total_score)

    return{
        "score":total_score,
        "matched_skills":matched_skills
    }
