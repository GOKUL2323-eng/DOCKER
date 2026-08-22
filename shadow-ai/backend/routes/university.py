from fastapi import APIRouter, Query
from services.university_service import UniversityService

router = APIRouter()

@router.get("/takshashila")
async def get_takshashila_profile():
    """
    Get full profile data for Takshashila University, Ongur, Tamil Nadu.
    Includes Management, Governing Council, Deans, Academic Leaders, AI & ML Chairs, and Programs.
    """
    return UniversityService.get_university_profile()

@router.get("/takshashila/search")
async def search_takshashila_info(q: str = Query(..., description="Query term (e.g. Chancellor, AI & ML, Deans)")):
    """
    Search university database for relevant personnel or academic roles.
    """
    results = UniversityService.search_university_info(q)
    return {"query": q, "results": results}

@router.get("/takshashila/aiml")
async def get_aiml_department_info():
    """
    Get key faculty and Board of Studies chairs for B.Sc AI & ML / Data Science at Takshashila University.
    """
    profile = UniversityService.get_university_profile()
    return {
        "university": profile.get("university", {}).get("name"),
        "aiml_contacts": profile.get("aiml_department_contacts", []),
        "academic_areas": [a for a in profile.get("major_academic_areas", []) if "AI" in a or "Computer" in a or "Data" in a]
    }
