@echo off
echo WORKPULSE AI - Quick Start
echo ==========================

if not exist .env copy .env.example .env

echo Starting Docker Compose...
docker-compose up --build
