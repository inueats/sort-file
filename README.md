docker run -d --name postgres -p 5432:5432 --env-file .env -v postgres-data:/var/lib/postgresql/data postgres:17.4
