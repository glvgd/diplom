from django.db.models import Count
from .models import UserProgress, Profession, ProfessionRequirement

def recommend_professions(user, limit=3):
    results = UserProgress.objects.filter(user=user, is_correct=True)
    
    if not results.exists():
        return Profession.objects.all()[:limit]
    
    subject_scores = {}
    for result in results:
        subject_id = result.task.subject.id
        subject_scores[subject_id] = subject_scores.get(subject_id, 0) + 1
    
    max_score = max(subject_scores.values()) if subject_scores else 1
    for subject_id in subject_scores:
        subject_scores[subject_id] /= max_score
    
    profession_scores = []
    for profession in Profession.objects.all():
        total_importance = 0
        weighted_score = 0
        
        requirements = ProfessionRequirement.objects.filter(profession=profession)
        for req in requirements:
            score = subject_scores.get(req.subject.id, 0)
            importance = req.importance
            total_importance += importance
            weighted_score += importance * score
        
        if total_importance > 0:
            final_score = weighted_score / total_importance
            profession_scores.append((profession, final_score))
        else:
            profession_scores.append((profession, 0))
    
    profession_scores.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in profession_scores[:limit]]