# Troubleshooting

## Common Issues

- **Docker not running**: Start Docker Desktop application
- **Port conflicts**: Modify ports in `docker-compose.yml` if 8080 or 8082 are in use
- **View logs**: `docker-compose logs -f [service-name]`
  - Backend logs: `docker-compose logs -f backend`
  - Database logs: `docker-compose logs -f database`
  - Frontend logs: `docker-compose logs -f frontend`
- **Rebuild containers**: `docker-compose up --build --force-recreate`
- **Clean restart**: `docker-compose down && docker-compose up --build`
- **Database connection issues**: Check that the database service is healthy before the backend starts
- **Migration errors**: Check Flyway logs in backend container output

## Backend Connection Issues

If the frontend cannot connect to the backend:

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Test API directly: `curl http://localhost:8080/healthcheck`
4. Verify CORS is enabled (it should be with `@CrossOrigin` annotations)

## Swagger UI Not Loading

If Swagger UI doesn't load:

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Try accessing: http://localhost:8080/api-docs (should return JSON)
4. Clear browser cache and try again

