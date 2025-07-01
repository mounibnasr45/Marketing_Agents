# SimilarWeb Simulator

A web application that simulates SimilarWeb analytics using a FastAPI backend and Next.js frontend.

## Project Structure

```
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables (create this)
├── app/                    # Next.js Frontend
│   ├── page.tsx           # Main page component
│   ├── layout.tsx         # Layout component
│   └── globals.css        # Global styles
├── components/             # UI Components
└── lib/                   # Utilities
```

## Technologies Used

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type annotations
- **httpx** - Async HTTP client for API calls
- **python-dotenv** - Environment variable management
- **uvicorn** - ASGI server

### Frontend (Next.js)
- **Next.js** - React framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Component library
- **Lucide React** - Icon library

## Setup Instructions

### 1. Backend Setup (FastAPI)

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional - for real Apify API)
echo "APIFY_API_TOKEN=your_apify_token_here" > .env

# Run the FastAPI server
python main.py
# Or use uvicorn directly:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The FastAPI backend will be available at: http://localhost:8000

### 2. Frontend Setup (Next.js)

```bash
# Navigate to the project root
cd ..

# Install dependencies
npm install
# or
pnpm install

# Run the development server
npm run dev
# or
pnpm dev
```

The Next.js frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env file in backend/ directory)
```
APIFY_API_TOKEN=your_apify_token_here  # Optional - uses mock data if not provided
```

### Frontend
No environment variables required. The frontend is configured to connect to the FastAPI backend at `http://localhost:8000`.

## API Endpoints

### FastAPI Backend (http://localhost:8000)

- `GET /` - API information
- `POST /api/analyze` - Analyze websites
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

### Example API Request
```bash
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"websites": ["linkedin.com", "github.com"]}'
```

## Features

- **Website Analysis**: Analyze any website's traffic and engagement metrics
- **Multiple Website Comparison**: Compare metrics across multiple websites
- **Interactive Dashboard**: Clean, modern UI with tabs for different data views
- **Mock Data**: Works without API token using realistic mock data
- **Real-time Data**: Connect to Apify API for real SimilarWeb data
- **Responsive Design**: Works on desktop and mobile devices

## Data Displayed

- Global ranking and traffic metrics
- Traffic sources breakdown
- Geographic distribution
- Top keywords and SEO data
- Social media traffic
- Competitor analysis
- Company information

## Development

### Backend Development
- The FastAPI server includes automatic API documentation at `/docs`
- Supports hot reloading with `--reload` flag
- CORS enabled for frontend development

### Frontend Development
- Next.js provides hot reloading for development
- TypeScript for type safety
- Tailwind CSS for styling
- Component-based architecture with Shadcn/UI

## Production Deployment

### Backend
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production ASGI server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Build for production
npm run build

# Start production server
npm start
```

## Troubleshooting

1. **CORS Issues**: Ensure the FastAPI backend is running on port 8000
2. **Module Not Found**: Make sure all dependencies are installed
3. **API Connection**: Verify the backend URL in the frontend code
4. **Mock Data**: If no Apify token is provided, the app uses mock data

## License

This project is for educational purposes and simulates SimilarWeb functionality using mock data.
