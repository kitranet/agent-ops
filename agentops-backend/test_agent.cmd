@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo ---------------------------
echo 1. Register agent-901
curl -s -X POST http://127.0.0.1:8000/agents/register -H "Content-Type: application/json" -d "{ \"agent_id\": \"agent-901\", \"agent_name\": \"ZetaTest\", \"agent_type\": \"executor\", \"version\": \"1.5\", \"framework\": \"LangGraph\", \"owner\": \"Team-Test\", \"status\": \"active\", \"task\": \"unit-test\", \"health_endpoint\": \"/health-zeta\", \"deployed_at\": \"2025-06-29T19:00:00\" }"
echo.

echo ---------------------------
echo 2. Get agent-901 status
curl -s http://127.0.0.1:8000/agents/status/agent-901
echo.

echo ---------------------------
echo 3. Get ALL agents
curl -s http://127.0.0.1:8000/agents/status/all
echo.

echo ---------------------------
echo 4. Retire agent-901
curl -s -X POST http://127.0.0.1:8000/agents/retire/agent-901
echo.

echo ---------------------------
echo 5. Update agent-901 status to maintenance
curl -s -X POST "http://127.0.0.1:8000/agents/update-status/agent-901?new_status=maintenance"
echo.

echo ---------------------------
echo 6. Summary of all agents
curl -s http://127.0.0.1:8000/agents/summary
echo.

echo ---------------------------
echo 7. List active agents
curl -s http://127.0.0.1:8000/agents/list/active
echo.

echo ---------------------------
echo 8. Delete agent-901
curl -s -X DELETE http://127.0.0.1:8000/agents/delete/agent-901
echo.

echo ---------------------------
echo 9. Confirm Deletion of agent-901
curl -s http://127.0.0.1:8000/agents/status/agent-901
echo.

echo ==== TESTS COMPLETE ====
