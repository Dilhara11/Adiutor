+-----------------------------------------------------------+
|                     DEVELOPMENT PHASE                     |
|                                                           |
| +----------------+        +---------------------------+   |
| |   DEVELOPER    |------->|   VS CODE IDE (Free)      |   |
| | (Manual Coding)|        | (Writes all Python Code)  |   |
| +----------------+        +-------------+-------------+   |
|                                         |                 |
|                   +---------------------+-----------------+
|                   |                     |
|                   v                     v
| +---------------------------+   +-----------------------+ |
| |      HR API BACKEND       |   |    AI ORCHESTRATOR    | |
| | (FastAPI / Python/ SQLite)|   |   (Python Middleware) | |
| | - Defines `GET /staff`    |   | - Connects User to AI | |
| | - Stores Mock Data        |   | - Connects AI to API  | |
| +-------------+-------------+   +-----------+-----------+ |
|               |                             |             |
|        (Auto-Generates)              (Reads)|             |
|               v                             v             |
| +---------------------------+   +-----------------------+ |
| |      OPENAPI SCHEMA       |---|   GOOGLE AI STUDIO    | |
| |      (Swagger UI)         |   |    (Gemini API Key)   | |
| | - Technical Specs (JSON)  |   | - Lacks Domain context| |
| | - No human definitions    |   | - Requires structuring| |
| +---------------------------+   +-----------------------+ |
|                                                           |
+-----------------------------------------------------------+
                              ||
                              || (Execution & Testing)
                              vv
+-----------------------------------------------------------+
|                       SIMULATION PHASE                    |
|                                                           |
|   +-----------+         +--------------+         +-----+  |
|   |   USER    | Natural | ORCHESTRATOR | API Call| HR  |  |
|   | (Input:   |-------->|   SCRIPT     |-------->| API |  |
|   | "New guy")| Language| (Middleware) |  (JSON) |     |  |
|   +-----------+         +---+------+---+         +--+--+  |
|                             ^      |                |     |
|                        (Asks|      |(Returns  +-----+--+  |
|                        for  |      | Action)  | SQLite  |  |
|                      Mapping)      v          | DB      |  |
|                     +-------+------+-----+    +--------+  |
|                     |     GEMINI AI      |                |
|                     |  (Struggles to map |                |
|                     |  intent to Schema) |                |
|                     +--------------------+                |
+-----------------------------------------------------------+