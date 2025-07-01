from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import httpx
import asyncio
import json
from supabase import create_client, Client

# Load environment variables
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Debug environment loading
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
print(f"Trying to load from: {env_path.absolute()}")

# Try to read .env file manually if dotenv fails
if not os.environ.get("SUPABASE_URL"):
    print("Attempting manual .env file parsing...")
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Manually set {key}")
    except Exception as e:
        print(f"Failed to manually parse .env: {e}")

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print(f"SUPABASE_URL from env: {url}")
print(f"SUPABASE_KEY from env: {key[:20] + '...' if key else None}")

# Check if Supabase credentials are available
supabase: Optional[Client] = None
if url and key:
    try:
        supabase = create_client(url, key)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        supabase = None
else:
    print("⚠️ Supabase credentials not found in environment variables")
    print(f"SUPABASE_URL: {'✅' if url else '❌'}")
    print(f"SUPABASE_KEY: {'✅' if key else '❌'}")

app = FastAPI(title="SimilarWeb API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TrafficSources(BaseModel):
    directVisitsShare: float
    organicSearchVisitsShare: float
    referralVisitsShare: float
    socialNetworksVisitsShare: float
    mailVisitsShare: float
    paidSearchVisitsShare: float
    adsVisitsShare: float

class TopCountry(BaseModel):
    countryAlpha2Code: str
    visitsShare: float
    visitsShareChange: float

class TopKeyword(BaseModel):
    name: str
    volume: int
    estimatedValue: int
    cpc: float

class SocialNetworkDistribution(BaseModel):
    name: str
    visitsShare: float

class TopSimilarityCompetitor(BaseModel):
    domain: str
    visitsTotalCount: int
    affinity: float
    categoryRank: Optional[int] = None  # Allow None values

class ApifyResult(BaseModel):
    name: str
    globalRank: int
    countryRank: int
    categoryRank: int
    companyName: str
    companyYearFounded: int
    companyEmployeesMin: int
    companyEmployeesMax: Optional[int] = None  # Allow None values
    totalVisits: int
    avgVisitDuration: str
    pagesPerVisit: float
    bounceRate: float
    trafficSources: TrafficSources
    topCountries: List[TopCountry]
    topKeywords: List[TopKeyword]
    socialNetworkDistribution: List[SocialNetworkDistribution]
    topSimilarityCompetitors: List[TopSimilarityCompetitor]
    organicTraffic: float  # Change to float to handle decimal values
    paidTraffic: float     # Change to float to handle decimal values

class WebsiteAnalysisRequest(BaseModel):
    websites: List[str]
    userId: str

class AnalysisResponse(BaseModel):
    success: bool
    data: List[ApifyResult]
    count: int
    note: Optional[str] = None

class ApifyClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.actor_id = "heLi1j7hzjC2gFlIx"

    async def analyze_domains(self, websites: List[str]) -> List[ApifyResult]:
        async with httpx.AsyncClient() as client:
            try:
                # Start the actor run
                # The input format might need to be different for this actor
                input_data = {
                    "websites": websites,
                    "maxPages": 1,  # Add this to limit pages if needed
                }
                
                run_response = await client.post(
                    f"https://api.apify.com/v2/acts/{self.actor_id}/runs",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json",
                    },
                    json=input_data,
                    timeout=30.0
                )

                if run_response.status_code != 201:  # Actor runs return 201 on creation
                    print(f"Unexpected status code: {run_response.status_code}")
                    print(f"Response: {run_response.text}")
                    raise HTTPException(status_code=500, detail=f"Failed to start actor run: {run_response.text}")

                run_data = run_response.json()
                run_id = run_data["data"]["id"]
                print(f"Started actor run with ID: {run_id}")

                # Poll for completion with a timeout
                max_polls = 60  # 5 minutes maximum
                poll_count = 0
                while poll_count < max_polls:
                    await asyncio.sleep(5)  # Wait 5 seconds
                    poll_count += 1
                    
                    status_response = await client.get(
                        f"https://api.apify.com/v2/acts/{self.actor_id}/runs/{run_id}",
                        headers={"Authorization": f"Bearer {self.api_token}"},
                        timeout=30.0
                    )
                    run = status_response.json()
                    current_status = run["data"]["status"]
                    print(f"Poll {poll_count}: Status = {current_status}")
                    
                    if current_status not in ["RUNNING", "READY"]:
                        break

                if poll_count >= max_polls:
                    raise HTTPException(status_code=504, detail="Actor run timed out")

                if run["data"]["status"] != "SUCCEEDED":
                    print(f"Actor run failed with status: {run['data']['status']}")
                    print(f"Run data: {run['data']}")
                    raise HTTPException(status_code=500, detail=f"Actor run failed with status: {run['data']['status']}")

                # Get the results from the dataset
                dataset_id = run["data"]["defaultDatasetId"]
                print(f"Fetching results from dataset: {dataset_id}")
                results_response = await client.get(
                    f"https://api.apify.com/v2/datasets/{dataset_id}/items",
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=30.0
                )

                if results_response.status_code != 200:
                    print(f"Failed to fetch results: {results_response.status_code} - {results_response.text}")
                    raise HTTPException(status_code=500, detail=f"Failed to fetch results: {results_response.text}")

                results = results_response.json()
                print(f"Retrieved {len(results)} results")
                print(f"Sample result structure: {results[0] if results else 'No results'}")
                
                # Transform the results to match our model if needed
                transformed_results = []
                for result in results:
                    try:
                        # Create an ApifyResult object from the raw data
                        transformed_result = ApifyResult(**result)
                        transformed_results.append(transformed_result)
                    except Exception as transform_error:
                        print(f"Error transforming result: {transform_error}")
                        print(f"Result data: {result}")
                        # Skip invalid results or create a default one
                        continue
                
                return transformed_results

            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Request timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

def get_mock_data() -> List[ApifyResult]:
    """Return mock data for testing when no API token is available"""
    return [
        ApifyResult(
            name="LinkedIn",
            globalRank=27,
            countryRank=15,
            categoryRank=1,
            companyName="LinkedIn Corporation",
            companyYearFounded=2003,
            companyEmployeesMin=10000,
            companyEmployeesMax=50000,
            totalVisits=2500000000,
            avgVisitDuration="8:45",
            pagesPerVisit=4.2,
            bounceRate=0.35,
            trafficSources=TrafficSources(
                directVisitsShare=0.45,
                organicSearchVisitsShare=0.35,
                referralVisitsShare=0.10,
                socialNetworksVisitsShare=0.05,
                mailVisitsShare=0.03,
                paidSearchVisitsShare=0.02,
                adsVisitsShare=0.00
            ),
            topCountries=[
                TopCountry(countryAlpha2Code="US", visitsShare=0.42, visitsShareChange=0.02),
                TopCountry(countryAlpha2Code="IN", visitsShare=0.15, visitsShareChange=0.05),
                TopCountry(countryAlpha2Code="GB", visitsShare=0.08, visitsShareChange=-0.01),
            ],
            topKeywords=[
                TopKeyword(name="linkedin", volume=50000000, estimatedValue=45000000, cpc=2.50),
                TopKeyword(name="linkedin login", volume=25000000, estimatedValue=20000000, cpc=1.80),
                TopKeyword(name="jobs", volume=15000000, estimatedValue=12000000, cpc=3.20),
            ],
            socialNetworkDistribution=[
                SocialNetworkDistribution(name="Facebook", visitsShare=0.35),
                SocialNetworkDistribution(name="Twitter", visitsShare=0.25),
                SocialNetworkDistribution(name="Instagram", visitsShare=0.20),
            ],
            topSimilarityCompetitors=[
                TopSimilarityCompetitor(domain="indeed.com", visitsTotalCount=1800000000, affinity=0.85, categoryRank=2),
                TopSimilarityCompetitor(domain="glassdoor.com", visitsTotalCount=500000000, affinity=0.75, categoryRank=5),
            ],
            organicTraffic=875000000.0,
            paidTraffic=50000000.0
        ),
        ApifyResult(
            name="GitHub",
            globalRank=64,
            countryRank=35,
            categoryRank=2,
            companyName="GitHub Inc.",
            companyYearFounded=2008,
            companyEmployeesMin=1000,
            companyEmployeesMax=5000,
            totalVisits=1200000000,
            avgVisitDuration="12:30",
            pagesPerVisit=6.8,
            bounceRate=0.28,
            trafficSources=TrafficSources(
                directVisitsShare=0.55,
                organicSearchVisitsShare=0.30,
                referralVisitsShare=0.12,
                socialNetworksVisitsShare=0.02,
                mailVisitsShare=0.01,
                paidSearchVisitsShare=0.00,
                adsVisitsShare=0.00
            ),
            topCountries=[
                TopCountry(countryAlpha2Code="US", visitsShare=0.38, visitsShareChange=0.01),
                TopCountry(countryAlpha2Code="CN", visitsShare=0.12, visitsShareChange=0.03),
                TopCountry(countryAlpha2Code="IN", visitsShare=0.11, visitsShareChange=0.04),
            ],
            topKeywords=[
                TopKeyword(name="github", volume=30000000, estimatedValue=25000000, cpc=1.20),
                TopKeyword(name="git", volume=20000000, estimatedValue=15000000, cpc=0.80),
                TopKeyword(name="open source", volume=8000000, estimatedValue=6000000, cpc=1.50),
            ],
            socialNetworkDistribution=[
                SocialNetworkDistribution(name="Twitter", visitsShare=0.45),
                SocialNetworkDistribution(name="Reddit", visitsShare=0.30),
                SocialNetworkDistribution(name="LinkedIn", visitsShare=0.15),
            ],
            topSimilarityCompetitors=[
                TopSimilarityCompetitor(domain="gitlab.com", visitsTotalCount=150000000, affinity=0.90, categoryRank=3),
                TopSimilarityCompetitor(domain="stackoverflow.com", visitsTotalCount=800000000, affinity=0.70, categoryRank=1),
            ],
            organicTraffic=360000000.0,
            paidTraffic=0.0
        )
    ]

@app.get("/")
async def root():
    return {
        "message": "SimilarWeb Analysis API",
        "usage": "POST /api/analyze with { 'websites': ['domain1.com', 'domain2.com'] }"
    }

@app.options("/api/analyze")
async def options_analyze():
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_websites(request: WebsiteAnalysisRequest):
    if not request.websites:
        raise HTTPException(status_code=400, detail="Please provide an array of websites to analyze")

    # Check if API token is available
    api_token = os.getenv("APIFY_API_TOKEN")
    print(f"APIFY_API_TOKEN: {api_token}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment file exists: {os.path.exists('.env')}")
    
    if not api_token:
        print("No API token found, using mock data")
        # Return mock data
        mock_data = get_mock_data()
        # Save to Supabase
        try:
            if supabase:
                # Convert Pydantic models to dictionaries
                data_to_insert = [item.dict() for item in mock_data]
                result = supabase.table("users").update({"similarweb_result": json.dumps(data_to_insert)}).eq("id", request.userId).execute()
                print("✅ Data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")

        return AnalysisResponse(
            success=True,
            data=mock_data,
            count=len(mock_data),
            note="Using mock data - APIFY_API_TOKEN not configured"
        )

    try:
        client = ApifyClient(api_token)
        results = await client.analyze_domains(request.websites)
        
        # Save to Supabase
        try:
            if supabase:
                # Convert Pydantic models to dictionaries
                data_to_insert = [item.dict() for item in results]
                result = supabase.table("users").update({"similarweb_result": json.dumps(data_to_insert)}).eq("id", request.userId).execute()
                print("✅ Data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")

        return AnalysisResponse(
            success=True,
            data=results,
            count=len(results)
        )

    except Exception as e:
        print(f"Error with Apify API: {str(e)}")
        print("Falling back to mock data")
        # Fall back to mock data if API fails
        mock_data = get_mock_data()
        # Save to Supabase
        try:
            if supabase:
                # Convert Pydantic models to dictionaries
                data_to_insert = [item.dict() for item in mock_data]
                result = supabase.table("users").update({"similarweb_result": json.dumps(data_to_insert)}).eq("id", request.userId).execute()
                print("✅ Data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")
            
        return AnalysisResponse(
            success=True,
            data=mock_data,
            count=len(mock_data),
            note=f"API failed, using mock data. Error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
