check: backend-check frontend-check

backend-check:
	cd backend && .venv/bin/ruff check && .venv/bin/alembic check && .venv/bin/pytest -q

frontend-check:
	cd frontend && npm run build