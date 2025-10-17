# LLM Code Deployment Project

This is an automated API for generating and deploying web apps using AIPipe (gpt-4o-mini) on GitHub Pages.

## Setup
1. Fork this repo.
2. Enable GitHub Pages in repo Settings > Pages > Source: Deploy from a branch > main.
3. Deploy to Hugging Face Spaces (see deployment instructions below).

## Usage
- POST JSON to `/api` with request details.
- API verifies, generates, deploys, and notifies.

## Files
- `app.py`: FastAPI endpoint.
- `generator.py`: AIPipe code gen.
- `github_handler.py`: GitHub ops.
- `models.py`: Data models.

## License
MIT (see LICENSE).
