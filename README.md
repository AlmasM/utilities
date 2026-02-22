# utilities

A file-to-Markdown conversion API powered by [markitdown](https://github.com/microsoft/markitdown), built with Flask and deployable to Vercel.

## Project Structure

```
utilities/
├── app.py              # Flask app factory + local dev entry point
├── api/
│   ├── index.py        # Vercel entry point
│   ├── convert.py      # POST /convert
│   └── health.py       # GET /health
├── utils/
│   └── auth.py         # Shared auth decorator
├── vercel.json
├── requirements.txt
└── .env                # Local secrets (not committed)
```

## Setup

**Requirements:** Python 3.10+

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env` and set your admin key:

```bash
cp .env .env.local   # or just edit .env directly
```

```env
ADMIN_KEY=your-secret-key-here
```

## Running Locally

```bash
source .venv/bin/activate
python app.py
# API available at http://localhost:8080
```

## API Reference

### `GET /health`

No auth required. Returns server status.

```bash
curl http://localhost:8080/health
```

```json
{ "success": true, "message": "OK" }
```

---

### `POST /convert`

Converts an uploaded file to Markdown.

**Auth:** `X-Admin-Key` header required.

**Supported formats:** PDF, DOCX, PPTX, XLSX, HTML, TXT, MD, CSV, JSON, XML, ZIP

```bash
curl -X POST http://localhost:8080/convert \
     -H "X-Admin-Key: your-secret-key-here" \
     -F "file=@/path/to/document.pdf"
```

**Success response:**

```json
{
  "success": true,
  "data": "# Document Title\n\nContent in markdown..."
}
```

**Error response:**

```json
{
  "success": false,
  "message": "Unauthorized. Provide a valid X-Admin-Key header."
}
```

## Adding a New Endpoint

1. Create `api/your_endpoint.py` with a Flask `Blueprint`
2. Register it in `app.py`:

```python
from api.your_endpoint import your_bp
app.register_blueprint(your_bp)
```

## Deploying to Vercel

```bash
npm i -g vercel

# Preview locally
vercel dev

# Deploy
vercel --prod
```

Set `ADMIN_KEY` in your Vercel project:  
**Dashboard → Project → Settings → Environment Variables**

> ⚠️ Never commit `.env` to version control.
