# My-App: Task 2 & Task 3

## Overview
This repository contains solutions for **Task 2** and **Task 3** within a Dockerized environment for easy setup, development, and testing.

## Project Structure

my-app/
├── frontend/
├── backend/
├── Dockerfile
├── docker-compose.yml
└── ...other files

text

- All code for Task 2 and Task 3 resides in the `my-app` folder.
- The project includes both frontend and backend components.

## Docker Environment

Both frontend and backend components are containerized using Docker.

- **Frontend**
  - Runs on port **80**
  - Accessible at: [http://localhost](http://localhost)

- **Backend**
  - Runs on port **5000**
  - Accessible at: [http://localhost:5000](http://localhost:5000)

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine

### Setup and Run

1. Clone the repository:
git clone https://github.com/littlegoblinjr/Aeroleads_tasks.git
cd Aeroleads_tasks/my-app

text

2. Build and start the containers:
docker-compose up --build

text

3. Access the application:
- Frontend: [http://localhost](http://localhost)
- Backend: [http://localhost:5000](http://localhost:5000)

4. To stop the containers:
docker-compose down

text

## Notes
- All environment variables should be kept in a `.env` file, which is excluded from version control via `.gitignore`.
- Make sure ports 80 and 5000 are free before starting containers.
