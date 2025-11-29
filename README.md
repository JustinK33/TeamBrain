# TeamBrain

A web app where teams collaboratively build, refine, and query a shared knowledge base (documents, FAQs, decisions) with real-time chat/Q&A and AI-powered summarisation.

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- Redis
- Docker
- Pydantic
- SQLAlchemy

---

## Features

- **Full JWT-based authentication**
  - User **registration** and **login** flows
  - **Access + refresh token** pattern for secure, short-lived sessions
  - **Protected routes** that require a valid JWT to access
  - **Logout-style token invalidation**, so tokens can be effectively revoked

- **Per-user, per-endpoint rate limiting**
  - Rate limits are enforced **per user** and **per API endpoint**
  - Uses **distributed storage** (e.g., Redis) so limits work across multiple servers/instances
  - **Layered caching** (Redis + in-memory) to reduce latency
  - Smart **cache invalidation** to keep data fresh without unnecessary recomputation

- **Fullstack messaging system**
  - Users can **create**, **edit**, and **delete** their messages
  - Messages are associated with specific spaces for organized conversations

- **Spaces (Rooms)**
  - Users can **create spaces** (like channels/rooms) to hold conversations
  - Spaces can be **public** or **password-protected**
  - Only users with the correct password can join protected spaces

- **End-to-end app flow**
  - Frontend + backend integrated into a **fullstack app**
  - Authenticated users can:
    - Sign up / log in
    - Join or create spaces
    - Send, edit, and delete messages within those spaces

---

## 📚 What I Learned From This Project

- **Per-user, per-endpoint rate limiting**  
  I learned how to design rate limiting that doesn’t just throttle globally, but **per user and per endpoint**, so heavy usage on one route doesn’t break others. I also learned how to store rate limit counters in **Redis** so the limits work correctly across multiple app instances.

- **Layered caching with Redis and in-memory stores**  
  I experimented with a **layered caching** approach: using in-memory cache for super-fast reads on a single instance, backed by **Redis** as a shared cache. I also had to think about **cache invalidation** so updates (like new messages or changes to spaces) don’t serve stale data.

- **JWT-based authentication and token flows**  
  I implemented **JWT auth** with **access and refresh tokens**, learned how to protect routes using middleware/guards, and how to rotate tokens safely. I also added a **logout-style token invalidation** pattern (e.g., blacklisting or tracking token versions) instead of just deleting cookies on the client.

- **Full authentication flow (register, login, protected routes)**  
  I built a full authentication flow where users can **register**, **log in**, get tokens, and access **protected API endpoints**. This helped me understand the interaction between frontend auth state, HTTP-only tokens or headers, and backend authorization checks.

- **Designing and modeling a messaging system**  
  I learned how to design data models and APIs for **creating, editing, and deleting messages**, and how to enforce permissions so users can only modify their own messages.

---

## Running the Project

### To run the project locally, follow these steps:

  1. Clone the repo (git clone <url>)
  2. Create a virtual environment (python3 -m venv venv)
  3. Activate the environment (source venv/bin/activate)
  4. Install requirements (pip install -r requirements.txt)
  5. Run locally (uvicorn app.main:app --reload)
     
### Run with Docker

  2. Build image (docker build -t teambrain -f Dockerfile .)
  3. Run image (docker run --rm -p 8000:8000 teambrain)
