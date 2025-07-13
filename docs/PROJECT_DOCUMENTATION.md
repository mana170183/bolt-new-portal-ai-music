# Project Documentation

This document provides an overview of the project structure, API endpoints, and frontend/backend port configurations to ensure seamless development and synchronization.

## Project Structure

The project is organized into the following main directories:

-   `backend/`: Contains the Flask backend application.
    -   `app.py`: The main application file with all API endpoints.
    -   `requirements.txt`: Python dependencies.
    -   `start.py`: Script to run the backend server.
    -   `.env`: Environment variables for the backend, including the port.
-   `src/`: Contains the React frontend application.
    -   `components/`: Reusable React components.
        -   `MusicGenerator.jsx`: The main component for the "Simple Mode".
        -   `AdvancedMusicGenerator.jsx`: The main component for the "Advanced Studio" mode.
    -   `services/`: API service layer for communicating with the backend.
        -   `api.js`: Axios instance and API service definitions.
-   `package.json`: Frontend dependencies and scripts.
-   `.env.local`: Environment variables for the frontend, including the API URL.

## Port Configuration

To ensure proper communication between the frontend and backend, the following ports are used:

-   **Frontend (Next.js):** `3000`
-   **Backend (Flask):** `5002`

These ports are configured in the following files:

-   **Frontend:**
    -   `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:5002`
    -   `src/services/api.js`: Fallback `API_BASE_URL` is set to `http://localhost:5002`.
-   **Backend:**
    -   `backend/.env`: `PORT=5002`
    -   `backend/start.py`: Reads the `PORT` from the `.env` file.

## API Endpoints

The backend provides the following API endpoints, all prefixed with `/api`:

-   `GET /api/health`: Checks the health of the backend server.
-   `POST /api/auth/token`: Generates an authentication token.
-   `GET /api/user/quota`: Retrieves the user's generation quota.
-   `GET /api/genres`: Returns a list of available music genres.
-   `GET /api/moods`: Returns a list of available music moods.
-   `GET /api/instruments`: Returns a list of available instruments.
-   `GET /api/composition-templates`: Returns a list of available composition templates.
-   `POST /api/generate-music`: Generates music in "Simple Mode".
-   `POST /api/generate-enhanced-music`: Generates music in "Advanced Studio" mode.

## How to Run the Application

1.  **Start the Backend:**
    ```bash
    cd backend
    python start.py
    ```
2.  **Start the Frontend:**
    ```bash
    npm run dev
    ```

The frontend will be accessible at `http://localhost:3000`.
