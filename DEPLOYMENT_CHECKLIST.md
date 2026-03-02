# Deployment Checklist

Use this checklist before promoting LuminaLib beyond local development.

## 1. Pre-Deployment Validation

- [ ] `.env` values reviewed and non-default secrets applied
- [ ] `JWT_SECRET` is strong and rotated
- [ ] Database connectivity verified
- [ ] API and frontend containers build successfully
- [ ] Required ports are available or remapped

## 2. Application Readiness

- [ ] Auth flows validated (signup/login/profile)
- [ ] Book upload and metadata operations validated
- [ ] Borrow/return flow validated
- [ ] Review and analysis paths validated
- [ ] Recommendation endpoint behavior verified

## 3. Data and Storage

- [ ] Persistent volumes configured correctly
- [ ] Backup strategy defined for PostgreSQL
- [ ] Storage backend selected (`local` or `s3`)
- [ ] File retention and cleanup policy documented

## 4. Security and Compliance

- [ ] HTTPS termination configured (reverse proxy or ingress)
- [ ] CORS policy restricted to allowed origins
- [ ] Rate limiting strategy in place
- [ ] Audit and access logging enabled

## 5. Observability

- [ ] Centralized logs enabled for api/frontend/db
- [ ] Error tracking integrated
- [ ] Health checks wired into orchestration
- [ ] Basic metrics collection enabled

## 6. Run Commands

```bash
cd c:\Amit\submissionjk
cp .env.example .env
docker-compose up --build
```

## 7. Smoke Test URLs

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 8. Rollback Plan

```bash
docker-compose down
docker-compose up --build
```

If persistent data is intentionally reset:

```bash
docker-compose down -v
```

## Deployment Status

Current baseline: ready for controlled environments (dev/staging), with production hardening items listed above.
