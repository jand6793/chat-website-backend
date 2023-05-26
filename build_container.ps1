$env:POSTGRES_PASSWORD = (Get-Content .env | Where-Object { $_ -match 'POSTGRES_PASSWORD' } | ForEach-Object { ($_ -split '=')[1] })
$env:BACKEND_PASSWORD = (Get-Content .env | Where-Object { $_ -match 'BACKEND_PASSWORD' } | ForEach-Object { ($_ -split '=')[1] })
docker build --build-arg POSTGRES_PASSWORD=$env:POSTGRES_PASSWORD --build-arg BACKEND_PASSWORD=$env:BACKEND_PASSWORD -t web-backend .
