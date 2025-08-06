# Attendance Bot

## 🐳 How to run with Docker

### Step 1: Build Docker Image

1. At the root of the project, navigate to `packages` then `server`

2. Build the image locally:
    ```bash
    docker build --no-cache -t bot-backend .
    ```

3. At the root of the project, navigate to `packages` then `bot`

4. Build the image locally:
    ```bash
    docker build --no-cache -t bot .
    ```

### Step 2: Run Docker Compose

1. Go to `docker` folder at the root of the project

2. Copy `.env.example` file, paste it into the same location, and rename to `.env` file

3. `docker compose up -d`

4. You can bring the containers down by `docker compose stop`
