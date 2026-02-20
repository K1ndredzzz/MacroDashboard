#!/usr/bin/env bash
set -e

echo "=========================================="
echo "  Macro Dashboard - Quick Deploy Script"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "Please create .env file from template:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  - POSTGRES_PASSWORD"
    echo "  - FRED_API_KEY"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo ""
    echo "Install Docker:"
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo ""
    echo "Install Docker Compose:"
    echo "  sudo apt install docker-compose -y"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# Load environment variables safely
set -a
source .env
set +a

# Check required variables
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ POSTGRES_PASSWORD is not set in .env"
    exit 1
fi

if [ -z "$FRED_API_KEY" ]; then
    echo "❌ FRED_API_KEY is not set in .env"
    exit 1
fi

echo "✓ Environment variables loaded"
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start services
echo ""
echo "Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker exec macro-postgres pg_isready -U macro_user > /dev/null 2>&1; then
    echo "✓ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
if docker exec macro-redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Check API
API_PORT="${API_PORT:-8888}"
if curl -f http://localhost:${API_PORT}/api/v1/health > /dev/null 2>&1; then
    echo "✓ API is ready"
else
    echo "⚠️  API is starting (may take a few more seconds)"
fi

# Check Frontend
if curl -f http://localhost:80/health > /dev/null 2>&1; then
    echo "✓ Frontend is ready"
else
    echo "⚠️  Frontend is starting (may take a few more seconds)"
fi

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Access your application:"
echo "  Frontend:    http://localhost"
echo "  API Docs:    http://localhost:${API_PORT}/api/v1/docs"
echo "  Health:      http://localhost:${API_PORT}/api/v1/health"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo ""
echo "For remote access, replace 'localhost' with your server IP"
echo ""
