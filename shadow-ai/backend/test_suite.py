import asyncio
import sys
import os
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from httpx import AsyncClient, ASGITransport
from main import app
from services.db import init_db

async def run_audit_suite():
    print("=" * 70)
    print("SHADOW AI: AUTOMATED TEST SUITE & END-TO-END VERIFICATION")
    print("=" * 70)
    
    await init_db()
    transport = ASGITransport(app=app)
    
    passed_tests = 0
    total_tests = 0
    
    def log_result(name, passed, details=""):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if passed:
            passed_tests += 1
            print(f"[PASS] Scenario {total_tests}: {name} {('- ' + details) if details else ''}")
        else:
            print(f"[FAIL] Scenario {total_tests}: {name} -> {details}")
            
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check endpoint
        try:
            res = await client.get("/api/health")
            passed = res.status_code == 200 and res.json().get("status") in ["online", "degraded"]
            log_result("Public Health Check Endpoint", passed, f"Status: {res.status_code}, Data: {res.json()}")
        except Exception as e:
            log_result("Public Health Check Endpoint", False, str(e))

        # 2. UI Endpoint & Static Assets
        try:
            res = await client.get("/ui")
            passed = res.status_code == 200 and "SHADOW AI" in res.text
            log_result("Frontend Web Interface Delivery", passed, f"Status: {res.status_code}, Length: {len(res.text)}")
        except Exception as e:
            log_result("Frontend Web Interface Delivery", False, str(e))

        # 3. User Registration
        import uuid
        test_user = f"operative_{uuid.uuid4().hex[:6]}"
        test_email = f"{test_user}@shadow.net"
        test_pass = "TacticalPassword123!"
        try:
            res = await client.post("/api/auth/register", json={
                "username": test_user,
                "email": test_email,
                "password": test_pass
            })
            passed = res.status_code == 200 and res.json().get("username") == test_user
            user_id_1 = res.json().get("id")
            log_result("User Account Registration", passed, f"User: {test_user}")
        except Exception as e:
            log_result("User Account Registration", False, str(e))

        # 4. User Login with Username
        token_1 = None
        try:
            res = await client.post("/api/auth/login", data={
                "username": test_user,
                "password": test_pass
            })
            passed = res.status_code == 200 and "access_token" in res.json()
            token_1 = res.json().get("access_token")
            log_result("User Authentication (via Username)", passed, "JWT Token acquired")
        except Exception as e:
            log_result("User Authentication (via Username)", False, str(e))

        # 5. User Login with Email
        try:
            res = await client.post("/api/auth/login", data={
                "username": test_email,
                "password": test_pass
            })
            passed = res.status_code == 200 and "access_token" in res.json()
            log_result("User Authentication (via Email)", passed, "Email-based login works")
        except Exception as e:
            log_result("User Authentication (via Email)", False, str(e))

        # 6. Invalid Credentials Handling
        try:
            res = await client.post("/api/auth/login", data={
                "username": test_user,
                "password": "WrongPassword999!"
            })
            passed = res.status_code == 401
            log_result("Invalid Credentials Rejection", passed, f"Status: {res.status_code}")
        except Exception as e:
            log_result("Invalid Credentials Rejection", False, str(e))

        # 7. Empty Message Validation
        headers_user_1 = {"Authorization": f"Bearer {token_1}"}
        try:
            res = await client.post("/api/chat/message", headers=headers_user_1, json={"message": "   "})
            passed = res.status_code == 400
            log_result("Empty Chat Input Validation", passed, f"Returned 400 Bad Request as expected")
        except Exception as e:
            log_result("Empty Chat Input Validation", False, str(e))

        # 8. Start New Chat Session & Persist Message 1
        session_id_user_1 = None
        try:
            res = await client.post("/api/chat/message", headers=headers_user_1, json={
                "message": "Initiate tactical uplink status check"
            })
            passed = res.status_code == 200
            lines = res.text.strip().split("\n")
            import json
            for line in lines:
                if line.startswith("data: "):
                    d = json.loads(line[6:])
                    if "session_id" in d and not session_id_user_1:
                        session_id_user_1 = d["session_id"]
            passed = passed and bool(session_id_user_1)
            log_result("Initial Chat Message & New Session Creation", passed, f"Session ID: {session_id_user_1}")
        except Exception as e:
            log_result("Initial Chat Message & New Session Creation", False, str(e))

        # 9. Multi-turn Conversation Context (Message 2 in same session)
        try:
            res = await client.post("/api/chat/message", headers=headers_user_1, json={
                "session_id": session_id_user_1,
                "message": "Verify second command in this operational thread"
            })
            passed = res.status_code == 200
            # Verify session was maintained
            res_detail = await client.get(f"/api/chat/sessions/{session_id_user_1}", headers=headers_user_1)
            msgs = res_detail.json().get("messages", [])
            passed = passed and len(msgs) >= 3 # message 1 + AI 1 + message 2 (+ AI 2)
            log_result("Multi-turn Context Persistence in Same Session", passed, f"Total messages in thread: {len(msgs)}")
        except Exception as e:
            log_result("Multi-turn Context Persistence in Same Session", False, str(e))

        # 10. Chat History Listing & Rename
        try:
            # Rename session
            new_title = "Tactical Recon Alpha"
            res_rename = await client.patch(
                f"/api/chat/sessions/{session_id_user_1}",
                headers=headers_user_1,
                json={"title": new_title}
            )
            # List sessions
            res_list = await client.get("/api/chat/sessions", headers=headers_user_1)
            sessions = res_list.json()
            found = any(s["id"] == session_id_user_1 and s["title"] == new_title for s in sessions)
            log_result("Chat Session Listing and Renaming", found, f"Updated title: {new_title}")
        except Exception as e:
            log_result("Chat Session Listing and Renaming", False, str(e))

        # 11. User Isolation & Security (Prevent IDOR cross-user access)
        # Create second user
        test_user_2 = f"operative_{uuid.uuid4().hex[:6]}"
        res_u2 = await client.post("/api/auth/register", json={
            "username": test_user_2,
            "email": f"{test_user_2}@shadow.net",
            "password": test_pass
        })
        token_2 = (await client.post("/api/auth/login", data={"username": test_user_2, "password": test_pass})).json().get("access_token")
        headers_user_2 = {"Authorization": f"Bearer {token_2}"}

        try:
            # User 2 tries to access User 1's session
            res_idor = await client.get(f"/api/chat/sessions/{session_id_user_1}", headers=headers_user_2)
            # Should be 404 Not Found (User 2 does not own it)
            passed = res_idor.status_code == 404
            log_result("Cross-User Conversation Isolation (IDOR Protection)", passed, f"Status code: {res_idor.status_code}")
        except Exception as e:
            log_result("Cross-User Conversation Isolation (IDOR Protection)", False, str(e))

        # 12. Delete Chat Session Operation
        try:
            res_del = await client.delete(f"/api/chat/sessions/{session_id_user_1}", headers=headers_user_1)
            passed = res_del.status_code == 200
            res_check = await client.get(f"/api/chat/sessions/{session_id_user_1}", headers=headers_user_1)
            passed = passed and res_check.status_code == 404
            log_result("Chat Session Deletion and Cleanup", passed, "Session deleted successfully")
        except Exception as e:
            log_result("Chat Session Deletion and Cleanup", False, str(e))

        # 13. Sandboxed Code Execution
        try:
            res_code = await client.post("/api/chat/execute", json={
                "lang": "python",
                "code": "print('Matrix computation nominal'); print(42 * 2)"
            })
            passed = res_code.status_code == 200 and "84" in res_code.json().get("stdout", "")
            log_result("Sandboxed Python Code Execution", passed, f"Output: {res_code.json().get('stdout', '').strip()}")
        except Exception as e:
            log_result("Sandboxed Python Code Execution", False, str(e))

        # 14. Takshashila University Knowledge API
        try:
            res_univ = await client.get("/api/university/takshashila")
            passed = res_univ.status_code == 200 and "Takshashila" in res_univ.text
            log_result("University Knowledge System API", passed, "Domain info retrieved")
        except Exception as e:
            log_result("University Knowledge System API", False, str(e))

    print("=" * 70)
    print(f"AUDIT SUMMARY: {passed_tests} / {total_tests} SCENARIOS PASSED")
    print("=" * 70)
    if passed_tests == total_tests:
        print("ALL AUDIT SCENARIOS PASSED WITH ZERO FAILURES.")
    else:
        print(f"WARNING: {total_tests - passed_tests} scenarios did not pass.")

if __name__ == "__main__":
    asyncio.run(run_audit_suite())
