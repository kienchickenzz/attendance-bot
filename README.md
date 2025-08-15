# Attendance Bot

## 📊 Generate Demo Data

### Prerequisites

1. Install dependencies:
   ```bash
   cd packages/data-pipeline
   bun install
   ```

2. Config database connection in `src/DataSource.js`

### How to run

#### Run with default parameters:
```bash
bun src/index.js
```
- Start Date: `2025-06-01`
- End Date: `2025-08-31` 
- User Email: `ndkien.ts@cmc.com.vn`

#### Run with custom parameters:
```bash
# Define start date
bun src/index.js 2025-07-01

# Define start date and end date
bun src/index.js 2025-07-01 2025-09-30

# Define all arguments (startDate endDate userEmail)
bun src/index.js 2025-07-01 2025-09-30 user@example.com
```

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
