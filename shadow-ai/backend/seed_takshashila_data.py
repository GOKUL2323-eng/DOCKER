import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.university_service import UniversityService
from services.memory_service import MemoryService

async def seed_takshashila():
    print("=" * 70)
    print(" INGESTING TAKSHASHILA UNIVERSITY KNOWLEDGE BASE INTO SHADOW AI")
    print("=" * 70)

    profile = UniversityService.get_university_profile()
    if not profile:
        print("ERROR: Could not load takshashila_university.json")
        return

    univ = profile.get("university", {})
    records = []

    # General info
    records.append(
        f"Takshashila University Overview: Located at {univ.get('location')}. "
        f"Motto: '{univ.get('motto')}'. Vision: {univ.get('vision')}. Official URL: {univ.get('website')}. "
        f"Educational approach: {univ.get('educational_approach')}."
    )

    # Top Management
    for person in profile.get("top_management", []):
        records.append(
            f"Takshashila University Top Management: {person['name']} is the {person['position']}."
        )

    # Governing Council
    for member in profile.get("governing_council", []):
        records.append(
            f"Takshashila University Governing Council: {member['name']} serves as {member['role']}."
        )

    # Deans
    for dean in profile.get("deans", []):
        records.append(
            f"Takshashila University Dean Profile: {dean['name']} is {dean['title']}. Details: {dean.get('bio', '')}."
        )

    # Academic Council & BOS Chairs
    for leader in profile.get("academic_council_and_bos_chairs", []):
        records.append(
            f"Takshashila University Academic Leader / Board of Studies: {leader['name']} is {leader['role']}."
        )

    # AI & ML Department Contacts
    for aiml in profile.get("aiml_department_contacts", []):
        records.append(
            f"Takshashila University B.Sc AI & ML / Computer Science Leadership: {aiml['name']} is {aiml['role']}."
        )

    user_id = "system-takshashila-ingest"
    print(f"Total knowledge facts extracted: {len(records)}")

    for i, fact in enumerate(records, 1):
        print(f"[{i}/{len(records)}] Ingesting fact: {fact[:80]}...")
        try:
            await MemoryService.add_memory(user_id=user_id, content=fact)
        except Exception as e:
            print(f"  -> Warning: Failed to ingest fact {i}: {e}")

    print("\nIngestion complete! Takshashila University knowledge base successfully indexed into Shadow AI memory.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(seed_takshashila())
