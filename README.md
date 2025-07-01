# SimilarWeb Analytics Dashboard
 ./node_modules/.bin/next dev
A powerful web analytics dashboard that integrates with Apify's SimilarWeb scraper to provide comprehensive website intelligence reports. Built with Next.js, TypeScript, and Tailwind CSS.

## Features

🚀 **Real-time Website Analysis**
- Analyze any website using real SimilarWeb data via Apify API
- Support for multiple websites simultaneously
- Predefined analysis for popular sites (LinkedIn, GitHub, Medium)

📊 **Comprehensive Analytics**
- Global ranking and traffic metrics
- Traffic source breakdown
- Geographic distribution
- Top keywords analysis
- Social media traffic distribution
- Competitor analysis
- Company information and demographics

🎨 **Modern UI/UX**
- Beautiful, responsive design using shadcn/ui components
- Interactive tabs for different analysis sections
- Real-time loading states and error handling
- Mobile-friendly interface

## Architecture

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React hooks (useState)

### Backend API
- **Real API**: `/api/analyze` - Connects to Apify SimilarWeb scraper
- **Mock API**: `/api/analyze-mock` - Provides realistic mock data for development
- **Auto-fallback**: Automatically uses mock data if Apify API token is not configured

### Data Flow
```
Frontend → API Route → Apify Client → SimilarWeb Scraper → Real Data
                   ↘ Mock Data (fallback)
```

## Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd similarweb-simulator
npm install
# or
pnpm install
```

### 2. Environment Setup (Optional for Mock Data)
Create `.env.local` file:
```bash
# Required only for real Apify data
APIFY_API_TOKEN=your_apify_api_token_here
NEXT_PUBLIC_API_URL=http://localhost:3000
```

### 3. Run Development Server
```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Start Analyzing!
- Click "Analyze Sample Sites" to test with LinkedIn, GitHub, and Medium
- Or enter any domain in the search box to analyze individual websites

## API Endpoints

### POST `/api/analyze`
Analyzes websites using real Apify SimilarWeb data.

**Request:**
```json
{
  "websites": ["https://www.linkedin.com", "https://www.github.com"]
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "linkedin.com",
      "globalRank": 34,
      "totalVisits": 756000000,
      "trafficSources": { ... },
      "topKeywords": [ ... ],
      // ... more data
    }
  ],
  "count": 1
}
```

### POST `/api/analyze-mock`
Provides realistic mock data for development and testing.

Same request/response format as real API, with additional `note` field indicating mock data usage.

## Data Structure

The application handles comprehensive website analytics data including:

```typescript
interface ApifyResult {
  name: string;                    // Domain name
  globalRank: number;              // Global website ranking
  countryRank: number;             // Country-specific ranking
  categoryRank: number;            // Category ranking
  companyName: string;             // Company name
  companyYearFounded: number;      // Founding year
  totalVisits: number;             // Monthly visits
  avgVisitDuration: string;        // Average session duration
  pagesPerVisit: number;           // Pages per session
  bounceRate: number;              // Bounce rate (0-1)
  
  trafficSources: {
    directVisitsShare: number;
    organicSearchVisitsShare: number;
    referralVisitsShare: number;
    socialNetworksVisitsShare: number;
    // ... more sources
  };
  
  topCountries: Array<{
    countryAlpha2Code: string;
    visitsShare: number;
    visitsShareChange: number;
  }>;
  
  topKeywords: Array<{
    name: string;
    volume: number;
    estimatedValue: number;
    cpc: number;
  }>;
  
  // ... more data fields
}
```

## Getting Apify API Token

1. Sign up at [Apify](https://apify.com/)
2. Navigate to Settings → Integrations → API tokens
3. Create a new token
4. Add it to your `.env.local` file as `APIFY_API_TOKEN`

## Development Features

- **TypeScript**: Full type safety throughout the application
- **Error Handling**: Comprehensive error states with user-friendly messages
- **Loading States**: Beautiful loading animations during API calls
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Mock Data Fallback**: Test without API setup using realistic mock data

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and developer experience
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **Lucide React** - Beautiful icons
- **Apify API** - SimilarWeb data scraping

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── analyze/route.ts          # Real Apify API endpoint
│   │   └── analyze-mock/route.ts     # Mock data endpoint
│   ├── globals.css                   # Global styles
│   ├── layout.tsx                    # Root layout
│   └── page.tsx                      # Main dashboard component
├── api/
│   └── apify-client.ts              # Apify client and types
├── components/
│   └── ui/                          # shadcn/ui components
├── lib/
│   └── utils.ts                     # Utility functions
└── public/                          # Static assets
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Inspired By

This project recreates the SimilarWeb analytics interface while providing real data integration through Apify's SimilarWeb scraper, similar to the analysis shown in the provided Jupyter notebook examples.
