export POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD .env | cut -d '=' -f2)
export BACKEND_PASSWORD=$(grep BACKEND_PASSWORD .env | cut -d '=' -f2)
docker build --build-arg POSTGRES_PASSWORD=$POSTGRES_PASSWORD --build-arg BACKEND_PASSWORD=$BACKEND_PASSWORD -t web-backend .
