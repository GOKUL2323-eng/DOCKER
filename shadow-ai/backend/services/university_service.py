import os
import json
from typing import Dict, Any, List

class UniversityService:
    _data: Dict[str, Any] = None

    @classmethod
    def _load_data(cls) -> Dict[str, Any]:
        if cls._data is None:
            data_file = os.path.join(os.path.dirname(__file__), "..", "data", "takshashila_university.json")
            if os.path.exists(data_file):
                with open(data_file, "r", encoding="utf-8") as f:
                    cls._data = json.load(f)
            else:
                cls._data = {}
        return cls._data

    @classmethod
    def get_university_profile(cls) -> Dict[str, Any]:
        return cls._load_data()

    @classmethod
    def get_university_system_context(cls) -> str:
        data = cls._load_data()
        if not data:
            return ""

        univ = data.get("university", {})
        top_mgmt = data.get("top_management", [])
        deans = data.get("deans", [])
        aiml = data.get("aiml_department_contacts", [])
        areas = data.get("major_academic_areas", [])

        mgmt_str = "\n".join([f"  - {person['name']}: {person['position']}" for person in top_mgmt])
        deans_str = "\n".join([f"  - {d['name']}: {d['title']} ({d.get('bio', '')})" for d in deans])
        aiml_str = "\n".join([f"  - {person['name']}: {person['role']}" for person in aiml])
        areas_str = ", ".join(areas)

        context = f"""
# TAKSHASHILA UNIVERSITY PROFILE & LEADERSHIP ARCHITECTURE #
- Name: {univ.get('name')}
- Location: {univ.get('location')}
- Motto: "{univ.get('motto')}"
- Vision: {univ.get('vision')}
- Official Website: {univ.get('website')}

TOP MANAGEMENT:
{mgmt_str}

DEANS & ACADEMIC LEADERSHIP:
{deans_str}

AI & ML DEPARTMENT CONTACTS / BOARD OF STUDIES CHAIRS:
{aiml_str}

MAJOR ACADEMIC AREAS:
{areas_str}
"""
        return context.strip()

    @classmethod
    def search_university_info(cls, query: str) -> str:
        query_lower = query.lower().strip()
        data = cls._load_data()
        if not data:
            return ""

        matches: List[str] = []
        terms = [t for t in query_lower.replace("&", "").split() if len(t) > 1]
        if not terms:
            terms = [query_lower]

        # Check Top Management
        for item in data.get("top_management", []):
            if query_lower in item["name"].lower() or query_lower in item["position"].lower() or any(t in item["name"].lower() or t in item["position"].lower() for t in terms):
                matches.append(f"Top Management: {item['name']} - {item['position']}")

        # Check Governing Council
        for item in data.get("governing_council", []):
            if query_lower in item["name"].lower() or query_lower in item["role"].lower() or any(t in item["name"].lower() or t in item["role"].lower() for t in terms):
                matches.append(f"Governing Council: {item['name']} - {item['role']}")

        # Check Deans
        for item in data.get("deans", []):
            if query_lower in item["name"].lower() or query_lower in item["title"].lower() or any(t in item["name"].lower() or t in item["title"].lower() for t in terms):
                matches.append(f"Dean: {item['name']} - {item['title']} | Bio: {item.get('bio', '')}")

        # Check Academic Council / BOS Chairs
        for item in data.get("academic_council_and_bos_chairs", []):
            if query_lower in item["name"].lower() or query_lower in item["role"].lower() or any(t in item["name"].lower() or t in item["role"].lower() for t in terms):
                matches.append(f"Academic Leader / BOS Chair: {item['name']} - {item['role']}")

        # Check AI & ML Department Contacts
        for item in data.get("aiml_department_contacts", []):
            if query_lower in item["name"].lower() or query_lower in item["role"].lower() or any(t in item["name"].lower() or t in item["role"].lower() for t in terms):
                matches.append(f"AI & ML Department Leader: {item['name']} - {item['role']}")

        if matches:
            # Deduplicate matches while preserving order
            unique_matches = list(dict.fromkeys(matches))
            return "TAKSHASHILA UNIVERSITY KNOWLEDGE BASE FINDINGS:\n" + "\n".join(f"- {m}" for m in unique_matches[:10])
        
        # If specific match not isolated, return general summary if query is about university
        if "takshashila" in query_lower or "university" in query_lower or "ongur" in query_lower or "chancellor" in query_lower:
            return cls.get_university_system_context()

        return ""
