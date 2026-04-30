# Platform Stack

The hosted product stack is:

- `web`: `Next.js` + `TypeScript` + `Tailwind CSS`
- `api`: `FastAPI` + `Python`
- `shared`: product-facing request and response contracts
- `db`: planned `PostgreSQL`

## Why This Stack

- The control engine already lives in Python, so `FastAPI` fits naturally.
- The product needs a strong dashboard-style frontend, so `Next.js` is the best practical fit.
- The website should display reports, approvals, runs, policies, and work packages in a structured UI.
- The backend should orchestrate `agent_control_stack`, repo integration, and project state.

## Planned Product Flow

1. user creates a project in the web UI
2. user connects a repository
3. user submits a governed request
4. web calls the platform API
5. platform API calls `agent_control_stack`
6. `agent_control_stack` decides `clarify`, `refuse`, `dispatch`, or `escalate`
7. approved dispatches route into governed AOS/CDD execution
8. run data and reports are shown back in the website
