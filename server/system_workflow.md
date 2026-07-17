          [ USER ]
             |
             | (1) INPUT: Natural Language Command
             |     (e.g., "Find the developer hired last week")
             v
+----------------------------+
|    AI ORCHESTRATOR         |
|    (Python Middleware)     |
+-------------+--------------+
             |
             | (2) REQUEST: "Which API matches this intent?"
             |     (+ Provides Swagger/OpenAPI Schema)
             v
      +--------------+
      |  GEMINI AI   | (Processing Logic)
      +--------------+
             |
             | (3) RESPONSE: { "method": "GET", "path": "/employees", 
             |                 "params": {"dept": "dev"} }
             v
+----------------------------+
|    AI ORCHESTRATOR         |
|    (Triggers API Call)     |
+-------------+--------------+
             |
             | (4) CALL: HTTP GET /employees?dept=dev
             v
+----------------------------+
|    HR API BACKEND          |
|    (FastAPI / Legacy)      |
+-------------+--------------+
             |                     +-----------------+
             | (5) QUERY / UPDATE  |  SQLITE DB      |
             +-------------------->|  (HR Records)   |
             |                     +-----------------+
             | (6) DATA RETURNED
             v
+----------------------------+
|    HR API BACKEND          |
|    (Returns JSON Result)   |
+-------------+--------------+
             |
             | (7) RAW DATA: [{"id": 101, "name": "John Doe", ...}]
             v
+----------------------------+
|    AI ORCHESTRATOR         |
|    (Formats for Human)     |
+-------------+--------------+
             |
             | (8) OUTPUT: Final Result
             |     (e.g., "I found 1 developer: John Doe.")
             v
          [ USER ]