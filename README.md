docker run -d --name postgres -p 5432:5432 --env-file .env -v postgres-data:/var/lib/postgresql/data postgres:17.4
docker run -d --name dynamodb-local -p 8000:8000 --env-file .env -v dynamodb_data:/home/dynamodblocal/data amazon/dynamodb-local:2.6.1 -jar DynamoDBLocal.jar -sharedDb -dbPath /home/dynamodblocal/data
docker run -d --name minio -p 9000:9000 -p 9001:9001 --env-file .env -v minio-data:/data minio/minio:RELEASE.2025-04-22T22-12-26Z-cpuv1 server /data --console-address ":9001"
docker run -d --name mlflow-tracking-server -p 5000:5000 --env-file .env gaiotechnology/gaio-car-ai-mlflow:latest mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@host.docker.internal:5432/${POSTGRES_DB} --default-artifact-root ${MLFLOW_ARTIFACT_URI}
docker run -d --name api -p 8080:8080 --env-file .env gaiotechnology/gaio-car-ai-inference-api:lates
