import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.university_service import UniversityService

def test_service():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("Testing UniversityService...")
    profile = UniversityService.get_university_profile()
    assert profile.get("university", {}).get("name") == "Takshashila University"
    print("[SUCCESS] Profile loaded successfully.")

    context = UniversityService.get_university_system_context()
    assert "Mr. M. Dhanasekaran" in context
    assert "Dr. Vivek Inder Kochhar" in context
    assert "Dr. R. Sathya Janaki" in context
    print("[SUCCESS] System context generated successfully.")

    search_result = UniversityService.search_university_info("Chancellor")
    assert "Mr. M. Dhanasekaran" in search_result
    print("[SUCCESS] Search query 'Chancellor' returned expected result.")

    aiml_search = UniversityService.search_university_info("AI & ML")
    assert "Dr. R. Sathya Janaki" in aiml_search
    print("[SUCCESS] Search query 'AI & ML' returned expected result.")

    print("\nALL UNIVERSITY SERVICE VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_service()
