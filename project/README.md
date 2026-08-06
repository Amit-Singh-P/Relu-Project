# Company Enrichment (MERN Stack)

A MERN application that enriches company information using an AI provider
(OpenAI, Gemini, or Claude) and stores the results in MongoDB Atlas.

## Project Structure

```
project/
├── backend/
│   ├── controllers/     # companyController.js, aiService.js
│   ├── models/          # Company.js (Mongoose model)
│   ├── routes/          # companyRoutes.js
│   ├── config/          # db.js, aiConfig.js (enrichment JSON schema)
│   ├── middleware/      # errorHandler.js
│   ├── app.js
│   ├── server.js
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/  # EnrichSection, ResultsSection, ProfileCard
│   │   ├── services/    # api.js (Axios client)
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
└── README.md
```

## API Endpoints

### `POST /enrich`
Request body:
```json
{ "websiteName": "Acme Corp", "url": "https://acme.com" }
```
Validates the input, calls the configured AI provider, saves the enriched
profile to MongoDB, and returns the saved document.

### `GET /results`
Returns every enriched company document stored in MongoDB, most recent first.

## Setup

### 1. Backend

```bash
cd backend
npm install
cp .env.example .env
```

Edit `backend/.env`:

```
MONGODB_URI=your MongoDB Atlas connection string
PORT=5000
AI_PROVIDER=openai        # openai | gemini | claude
AI_API_KEY=your AI provider API key
AI_MODEL=gpt-4o-mini       # any valid model for your chosen provider
CLIENT_ORIGIN=http://localhost:5173
```

Run the server:

```bash
npm run dev     # with nodemon
# or
npm start
```

The API will be available at `http://localhost:5000`.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
```

Edit `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:5000
```

Run the dev server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

## How Enrichment Works

1. The user submits a Website Name and Company URL from the **Enrich** section.
2. The backend validates the input and sends a prompt to the configured AI
   provider, instructing it to return JSON matching the schema defined in
   `backend/config/aiConfig.js`.
3. The AI's JSON response is parsed and normalized (missing fields default to
   `null` so the shape is always consistent) and saved to MongoDB inside the
   `enrichedProfile` field of a `Company` document.
4. The saved document (including `websiteName`, `url`, `enrichedProfile`,
   `createdAt`, `updatedAt`) is returned to the frontend and rendered.
5. The **Results** section calls `GET /results` to list every stored company.

## Enriched Profile Schema

Every enrichment response includes the following fields (any unknown value is
`null`, never omitted):

```
companyName, website, industry, description, foundedYear, headquarters,
employeeCount, companyType, products[], socialLinks { linkedin, twitter,
facebook }, contactEmail, phone
```

## Deployment

This project is split into two independently deployable apps:

- **Backend** → Render or Railway
  - Set the root directory to `backend`
  - Build command: `npm install`
  - Start command: `npm start`
  - Add the environment variables from `backend/.env.example`

- **Frontend** → Vercel or Netlify
  - Set the root directory to `frontend`
  - Build command: `npm run build`
  - Output directory: `dist`
  - Add `VITE_API_BASE_URL` pointing to your deployed backend URL

No authentication is required — the app is publicly accessible once deployed.

## Notes

- Do not commit `.env` files; use `.env.example` as a template.
- Swap AI providers at any time by changing `AI_PROVIDER`, `AI_API_KEY`, and
  `AI_MODEL` in `backend/.env` — no code changes required.
