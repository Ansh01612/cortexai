---
title: CortexAI
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# CortexAI

CortexAI is a full-stack AI chat application with a React frontend and a
Node.js backend split into gateway, authentication, chat, agent, and billing
services.

## Architecture

```text
Browser (Vite, port 5173)
        |
        v
Gateway (port 8000)
  |       |       |       |
 Auth    Chat    Agent   Billing
 8001    8002    8003     8004
        |
 Redis (port 6379)     MongoDB (port 27017)
```

The backend uses MongoDB for application data, Redis for sessions, Firebase
Authentication for Google sign-in, and Razorpay for billing. The agent service
can also use the configured model, search, vector database, and object storage
providers.

## Requirements

- Node.js 22 or newer
- npm
- Docker Desktop with Docker Compose
- Firebase project configured for Google sign-in

The local Compose setup runs MongoDB and Redis on localhost. MongoDB Atlas is
optional if you prefer a remote database.

Additional provider credentials are needed for the agent and billing features
you enable.

## Local development

Clone the repository and open PowerShell in the project folder:

```powershell
git clone https://github.com/Ansh01612/cortex-ai-.git
cd cortex-ai-
```

Create a `.env` file in each location listed under [Environment configuration](#environment-configuration),
and add the Firebase Admin service-account JSON described below. Do not commit
`.env` files or service-account credentials.

Install dependencies from each package directory:

```powershell
cd backend
npm install
cd gateway
npm install
cd ..\services\auth
npm install
cd ..\chat
npm install
cd ..\agent
npm install
cd ..\billing
npm install
cd ..\..\..\frontend
npm install
```

Start the full local stack with one command from the project root:

```powershell
.\start-dev.ps1
```

The script starts MongoDB, Redis, and any backend/frontend services that are
not already running, opens the frontend at <http://localhost:5173>, and leaves
service output visible in separate PowerShell windows. Keep those windows
open. If PowerShell blocks local scripts, run it once using:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-dev.ps1
```

Stop the containers when finished with:

```powershell
cd "path\to\cortex-ai-\backend"
docker compose down
```

## Environment configuration

Create local `.env` files using the variable names below. Use real values from
your own provider accounts; never copy credentials into source code or commit
them to Git.

| File | Variables |
| --- | --- |
| `frontend/.env` | `VITE_FIREBASE_API_KEY`, `VITE_RAZORPAY_KEY_ID`, `VITE_SERVER_URL` |
| `backend/gateway/.env` | `PORT`, `AUTH_SERVICE`, `CHAT_SERVICE`, `AGENT_SERVICE`, `BILLING_SERVICE`, `FRONTEND_URL`, `REDIS_URL` |
| `backend/services/auth/.env` | `PORT`, `MONGODB_URI`, `REDIS_URL` |
| `backend/services/chat/.env` | `PORT`, `MONGODB_URI` |
| `backend/services/agent/.env` | `PORT`, `MONGODB_URI`, `GROQ_API_KEY`, `GOOGLE_API_KEY`, `CHAT_SERVICE`, `AUTH_SERVICE`, `REDIS_URL`, `TAVILY_API_KEY`, `OPENROUTER_API_KEY`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_KEY`, `AWS_BUCKET_NAME`, `QDRANT_API_KEY`, `QDRANT_URL` |
| `backend/services/billing/.env` | `PORT`, `MONGODB_URI`, `AUTH_SERVICE`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` |

For local development, set each service's `MONGODB_URI` to its local database:
`mongodb://localhost:27017/auth`, `/chat`, `/agent`, or `/billing`,
respectively. Compose keeps local MongoDB data in a persistent Docker volume.
If you want to use Atlas instead, configure the Atlas URI in each service's
`.env` file and allow your development IP in Atlas Network Access.

The backend service URLs normally use ports `8000`
(gateway), `8001` (auth), `8002` (chat), `8003` (agent), and `8004` (billing).
Set `FRONTEND_URL` to `http://localhost:5173`, and `VITE_SERVER_URL` to
`http://localhost:8000`. Compose binds Redis to localhost on port `6379` and
MongoDB to localhost on port `27017`.

The auth service also needs a Firebase Admin service-account JSON file at
`backend/services/auth/serviceAccountKey.json`. This file is excluded from
Git; obtain it from your Firebase project and keep it private.

Agent provider variables are required only for the corresponding integrations.
Keep all provider secrets server-side; only frontend values prefixed with
`VITE_` are exposed to the browser.

## Production deployment

### Vercel

The Vercel deployment uses one serverless API function for the existing API
routers and serves the Vite frontend from the same project origin. Import the
GitHub repository into Vercel and set:

- Git branch: `initial-project-upload`
- Root directory: `.`
- Build command: `npm run build`
- Output directory: `frontend/dist`
- Install command: `npm install`

Do not set `VITE_SERVER_URL` in Vercel; the frontend then calls the same-origin
`/api` routes. Set these server-side Vercel environment variables:

- `MONGODB_URI`: MongoDB Atlas URI using one shared application database
- `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
- `FIREBASE_SERVICE_ACCOUNT_JSON`: the complete Firebase Admin service-account
  JSON, stored as a secret environment variable
- `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, and `TAVILY_API_KEY`
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_KEY`, and `AWS_BUCKET_NAME`
- `QDRANT_API_KEY` and `QDRANT_URL`

Also set the frontend build variables `VITE_FIREBASE_API_KEY` and
`VITE_RAZORPAY_KEY_ID`. Add the final Vercel domain to Firebase Authentication's
authorized domains. Keep `MONGODB_URI` and all provider credentials server-side;
never prefix them with `VITE_`.

The project depends on managed MongoDB and Upstash Redis in Vercel. The local
Docker MongoDB/Redis containers are only for development. Hobby deployments
have serverless execution and request-size limits; large PDF/image uploads or
long-running agent tasks may need a paid plan or a separate worker service.

### Hugging Face Spaces

This repository also contains a Docker Space configuration. Create a new
Docker Space and connect this repository, or push this repository's contents
to the Space. The Space listens on port `7860` and runs the frontend and
combined API in one container. Configure these values under the Space's
**Settings → Variables and secrets**; do not commit them to the repository:

- `MONGODB_URI`: a reachable MongoDB Atlas URI using a newly rotated database
  password; use an application database name in the URI
- `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`
- `FIREBASE_SERVICE_ACCOUNT_JSON`: complete Firebase Admin service-account
  JSON as a secret; the frontend Firebase web API key is not a substitute
- `VITE_FIREBASE_API_KEY`: Firebase web API key (used during container startup
  to build the frontend)
- `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENROUTER_API_KEY`, and `TAVILY_API_KEY`
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` for payments
- `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_KEY`, and `AWS_BUCKET_NAME`
  for object storage
- `QDRANT_API_KEY` and `QDRANT_URL` for vector search

Use fresh provider credentials because credentials previously shared in chat
should be considered compromised. Allow network access from Hugging Face
Spaces in MongoDB Atlas. The Space needs external managed MongoDB and Redis;
the local Compose databases are not available to the deployed container.
After setting variables and secrets, restart the Space so the frontend rebuilds
with its Firebase key. On the Space's page, check `/api/health` for the API
health response.

The repository includes a GitHub Actions workflow at
`.github/workflows/deploy.yml` for deploying backend images to AWS ECR/ECS and
the frontend to S3/CloudFront. Configure the AWS credentials, resource names,
and other required values as GitHub Actions repository secrets before enabling
that workflow. Configure each service's runtime environment in the deployment
platform as well.

## Security

- `.env` files, Firebase service-account keys, dependencies, and build output
  are excluded from Git.
- Rotate any credential that has been shared or accidentally exposed.
- Do not expose Redis directly to the public internet.
- Restrict Firebase browser API keys to the intended domains in Firebase
  settings.
