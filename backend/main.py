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
load_dotenv()

# Debug environment loading
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")
print(f"All environment variables: {list(os.environ.keys())}")

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

# Pydantic models for BuiltWith
class Technology(BaseModel):
    name: str
    tag: str  # e.g., "Analytics", "Frameworks", "CDN"

class BuiltWithResult(BaseModel):
    domain: str
    technologies: List[Technology]

class ApifyResult(BaseModel):
    name: str
    globalRank: int
    countryRank: int
    categoryRank: int
    companyName: str
    companyYearFounded: int
    companyEmployeesMin: int
    companyEmployeesMax: Optional[int] = None
    totalVisits: int
    avgVisitDuration: str
    pagesPerVisit: float
    bounceRate: float
    trafficSources: TrafficSources
    topCountries: List[TopCountry]
    topKeywords: List[TopKeyword]
    socialNetworkDistribution: List[SocialNetworkDistribution]
    topSimilarityCompetitors: List[TopSimilarityCompetitor]
    organicTraffic: float
    paidTraffic: float
    builtwith_result: Optional[BuiltWithResult] = None  # Add BuiltWith data

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
            paidTraffic=50000000.0,
            builtwith_result=BuiltWithResult(
                domain="linkedin.com",
                technologies=[
                    Technology(name="React", tag="JavaScript Frameworks"),
                    Technology(name="Node.js", tag="Web Servers"),
                    Technology(name="Amazon CloudFront", tag="CDN"),
                    Technology(name="Google Analytics", tag="Analytics"),
                    Technology(name="Nginx", tag="Web Servers"),
                    Technology(name="Amazon Web Services", tag="Cloud Computing"),
                    Technology(name="Bootstrap", tag="CSS Frameworks"),
                    Technology(name="jQuery", tag="JavaScript Libraries"),
                ]
            )
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
            paidTraffic=0.0,
            builtwith_result=BuiltWithResult(
                domain="github.com",
                technologies=[
                    Technology(name="Ruby on Rails", tag="Web Frameworks"),
                    Technology(name="MySQL", tag="Databases"),
                    Technology(name="Redis", tag="Caching"),
                    Technology(name="Fastly", tag="CDN"),
                    Technology(name="GitHub Analytics", tag="Analytics"),
                    Technology(name="Amazon Web Services", tag="Cloud Computing"),
                    Technology(name="Elasticsearch", tag="Search Engines"),
                    Technology(name="JavaScript", tag="Programming Languages"),
                ]
            )
        )
    ]

class BuiltWithClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.builtwith.com/v20/api.json"

    async def analyze_domain(self, domain: str) -> BuiltWithResult:
        """Analyze a domain's technology stack using BuiltWith API"""
        
        # Clean domain (remove http/https and www)
        clean_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        
        print(f"   🔍 BuiltWith Analysis: {clean_domain}")
        print(f"   📋 API Key Status: {'✅ Valid' if self.api_key and self.api_key != 'your-builtwith-api-key-here' else '❌ Invalid/Missing'}")
        
        if not self.api_key or self.api_key == "your-builtwith-api-key-here":
            print(f"   ⚠️ Using mock data for {clean_domain}")
            return self._get_mock_builtwith_data(clean_domain)
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"   🌐 Calling BuiltWith API...")
                print(f"   🔗 URL: {self.base_url}")
                print(f"   📝 Domain: {clean_domain}")
                
                response = await client.get(
                    self.base_url,
                    params={
                        "KEY": self.api_key,
                        "LOOKUP": clean_domain
                    },
                    timeout=30.0
                )
                
                print(f"   📊 Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"   ❌ API Error: HTTP {response.status_code}")
                    print(f"   📄 Response: {response.text[:200]}...")
                    print(f"   🔄 Falling back to mock data")
                    return self._get_mock_builtwith_data(clean_domain)
                
                data = response.json()
                print(f"   ✅ API response received")
                print(f"   📊 Response size: {len(str(data))} characters")
                
                result = self._parse_builtwith_response(clean_domain, data)
                tech_count = len(result.technologies)
                print(f"   🎯 Parsing complete: {tech_count} technologies extracted")
                
                if tech_count > 0:
                    categories = list(set(tech.tag for tech in result.technologies))
                    print(f"   📂 Categories found: {', '.join(categories[:3])}{'...' if len(categories) > 3 else ''}")
                
                return result
                
            except httpx.TimeoutException:
                print(f"   ⏰ API timeout for {clean_domain}")
                print(f"   🔄 Falling back to mock data")
                return self._get_mock_builtwith_data(clean_domain)
            except Exception as e:
                print(f"   ❌ API error: {str(e)}")
                print(f"   🔄 Falling back to mock data")
                return self._get_mock_builtwith_data(clean_domain)

    def _parse_builtwith_response(self, domain: str, data: dict) -> BuiltWithResult:
        """Parse BuiltWith API response into our model"""
        technologies = []
        
        try:
            print(f"🔍 Parsing BuiltWith response for {domain}")
            print(f"Response keys: {list(data.keys())}")
            
            if "Results" in data and len(data["Results"]) > 0:
                result = data["Results"][0]
                print(f"Result keys: {list(result.keys())}")
                
                if "Result" in result and "Paths" in result["Result"]:
                    paths = result["Result"]["Paths"]
                    print(f"Found {len(paths)} paths")
                    
                    for path in paths:
                        if "Technologies" in path:
                            techs = path["Technologies"]
                            print(f"Found {len(techs)} technology categories in path")
                            
                            for tech_category in techs:
                                # Ensure tech_category is a dict
                                if not isinstance(tech_category, dict):
                                    continue
                                    
                                category_name = tech_category.get("Name", "Other")
                                print(f"Processing category: {category_name}")
                                
                                # Check for direct technologies in the category
                                if "Technologies" in tech_category:
                                    for tech in tech_category["Technologies"]:
                                        if isinstance(tech, dict):
                                            tech_name = tech.get("Name", "Unknown")
                                            if tech_name and tech_name != "Unknown":
                                                technologies.append(Technology(
                                                    name=tech_name,
                                                    tag=category_name
                                                ))
                                                print(f"Added tech: {tech_name} ({category_name})")
                                
                                # Also check for Categories structure
                                if "Categories" in tech_category:
                                    for category in tech_category["Categories"]:
                                        # Ensure category is a dict
                                        if not isinstance(category, dict):
                                            continue
                                            
                                        for tech in category.get("Technologies", []):
                                            # Ensure tech is a dict
                                            if not isinstance(tech, dict):
                                                continue
                                                
                                            tech_name = tech.get("Name", "Unknown")
                                            if tech_name and tech_name != "Unknown":
                                                technologies.append(Technology(
                                                    name=tech_name,
                                                    tag=category_name
                                                ))
                                                print(f"Added tech: {tech_name} ({category_name})")
                
                # If no technologies found in Paths, check for a simpler structure
                if not technologies and "Technologies" in result:
                    print("Checking alternative technologies structure")
                    for tech_item in result["Technologies"]:
                        if isinstance(tech_item, dict):
                            tech_name = tech_item.get("Name", tech_item.get("name", "Unknown"))
                            category = tech_item.get("Category", tech_item.get("tag", "Other"))
                            if tech_name and tech_name != "Unknown":
                                technologies.append(Technology(
                                    name=tech_name,
                                    tag=category
                                ))
                                print(f"Added tech (alt): {tech_name} ({category})")
                                
        except Exception as e:
            print(f"Error parsing BuiltWith response for {domain}: {e}")
            print(f"Response data: {data}")
        
        print(f"Final result: {len(technologies)} technologies parsed for {domain}")
        
        # If no technologies were found, fallback to mock data
        if not technologies:
            print(f"⚠️ No technologies found for {domain}, using mock data fallback")
            return self._get_mock_builtwith_data(domain)
        
        return BuiltWithResult(domain=domain, technologies=technologies)

    def _get_mock_builtwith_data(self, domain: str) -> BuiltWithResult:
        """Generate mock BuiltWith data for testing"""
        mock_data = {
            "linkedin.com": [
                Technology(name="React", tag="JavaScript Frameworks"),
                Technology(name="Node.js", tag="Web Servers"),
                Technology(name="Amazon CloudFront", tag="CDN"),
                Technology(name="Google Analytics", tag="Analytics"),
                Technology(name="Nginx", tag="Web Servers"),
                Technology(name="Amazon Web Services", tag="Cloud Computing"),
                Technology(name="Bootstrap", tag="CSS Frameworks"),
                Technology(name="jQuery", tag="JavaScript Libraries"),
            ],
            "github.com": [
                Technology(name="Ruby on Rails", tag="Web Frameworks"),
                Technology(name="MySQL", tag="Databases"),
                Technology(name="Redis", tag="Caching"),
                Technology(name="Fastly", tag="CDN"),
                Technology(name="GitHub Analytics", tag="Analytics"),
                Technology(name="Amazon Web Services", tag="Cloud Computing"),
                Technology(name="Elasticsearch", tag="Search Engines"),
                Technology(name="JavaScript", tag="Programming Languages"),
            ],
            "medium.com": [
                Technology(name="Node.js", tag="Web Servers"),
                Technology(name="React", tag="JavaScript Frameworks"),
                Technology(name="Amazon CloudFront", tag="CDN"),
                Technology(name="Google Analytics", tag="Analytics"),
                Technology(name="Amazon Web Services", tag="Cloud Computing"),
                Technology(name="GraphQL", tag="APIs"),
                Technology(name="PostgreSQL", tag="Databases"),
                Technology(name="TypeScript", tag="Programming Languages"),
            ],
            "facebook.com": [
                Technology(name="React", tag="JavaScript Frameworks"),
                Technology(name="PHP", tag="Programming Languages"),
                Technology(name="MySQL", tag="Databases"),
                Technology(name="Memcached", tag="Caching"),
                Technology(name="Facebook CDN", tag="CDN"),
                Technology(name="Facebook Analytics", tag="Analytics"),
                Technology(name="HipHop", tag="Web Frameworks"),
                Technology(name="Cassandra", tag="Databases"),
            ],
            "google.com": [
                Technology(name="Go", tag="Programming Languages"),
                Technology(name="JavaScript", tag="Programming Languages"),
                Technology(name="Google Cloud CDN", tag="CDN"),
                Technology(name="Google Analytics", tag="Analytics"),
                Technology(name="Bigtable", tag="Databases"),
                Technology(name="Google Cloud Platform", tag="Cloud Computing"),
                Technology(name="V8", tag="JavaScript Engines"),
                Technology(name="Protocol Buffers", tag="APIs"),
            ]
        }
        
        # Get mock data for the domain or default
        technologies = mock_data.get(domain, [
            Technology(name="JavaScript", tag="Programming Languages"),
            Technology(name="HTML5", tag="Markup Languages"),
            Technology(name="CSS3", tag="Stylesheets"),
            Technology(name="Google Analytics", tag="Analytics"),
            Technology(name="Cloudflare", tag="CDN"),
        ])
        
        return BuiltWithResult(domain=domain, technologies=technologies)

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
    """Step 1: Analyze websites with SimilarWeb only"""
    if not request.websites:
        raise HTTPException(status_code=400, detail="Please provide an array of websites to analyze")

    print("📊 Starting SimilarWeb Analysis (Step 1)")
    print("=" * 50)

    # Check if API tokens are available
    apify_token = os.getenv("APIFY_API_TOKEN")
    
    print(f"APIFY_API_TOKEN: {'✅' if apify_token else '❌'}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment file exists: {os.path.exists('.env')}")
    
    if not apify_token:
        print("📋 No Apify API token found, using mock data")
        # Return mock data WITHOUT BuiltWith analysis initially
        mock_data = get_mock_data()
        
        # Remove BuiltWith data for step-by-step process
        for item in mock_data:
            item.builtwith_result = None
        
        # Save to Supabase
        try:
            if supabase:
                data_to_insert = [item.model_dump() for item in mock_data]
                result = supabase.table("users").update({
                    "similarweb_result": json.dumps(data_to_insert)
                }).eq("id", request.userId).execute()
                print("✅ SimilarWeb data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")

        print("✅ Step 1 (SimilarWeb) completed with mock data")
        return AnalysisResponse(
            success=True,
            data=mock_data,
            count=len(mock_data),
            note="Step 1 complete: SimilarWeb analysis ready. Click 'Analyze Tech Stack' to continue."
        )

    try:
        print("🔄 Fetching data from Apify API...")
        # Get SimilarWeb data only
        apify_client = ApifyClient(apify_token)
        results = await apify_client.analyze_domains(request.websites)
        
        # Ensure no BuiltWith data is included yet
        for result in results:
            result.builtwith_result = None
        
        # Save to Supabase
        try:
            if supabase:
                data_to_insert = [item.model_dump() for item in results]
                result = supabase.table("users").update({
                    "similarweb_result": json.dumps(data_to_insert)
                }).eq("id", request.userId).execute()
                print("✅ SimilarWeb data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")

        print("✅ Step 1 (SimilarWeb) completed successfully")
        return AnalysisResponse(
            success=True,
            data=results,
            count=len(results),
            note="Step 1 complete: SimilarWeb analysis ready. Click 'Analyze Tech Stack' to continue."
        )

    except Exception as e:
        print(f"❌ Error with Apify API: {str(e)}")
        print("📋 Falling back to mock data")
        # Fall back to mock data if API fails
        mock_data = get_mock_data()
        
        # Remove BuiltWith data for step-by-step process
        for item in mock_data:
            item.builtwith_result = None
        
        # Save to Supabase
        try:
            if supabase:
                data_to_insert = [item.model_dump() for item in mock_data]
                result = supabase.table("users").update({
                    "similarweb_result": json.dumps(data_to_insert)
                }).eq("id", request.userId).execute()
                print("✅ SimilarWeb data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")
            
        print("✅ Step 1 (SimilarWeb) completed with fallback data")
        return AnalysisResponse(
            success=True,
            data=mock_data,
            count=len(mock_data),
            note=f"Step 1 complete (with fallback): SimilarWeb analysis ready. API Error: {str(e)}"
        )

@app.post("/api/analyze-tech-stack", response_model=AnalysisResponse)
async def analyze_tech_stack(request: WebsiteAnalysisRequest):
    """Step 2: Add BuiltWith technology analysis to existing SimilarWeb data"""
    if not request.websites:
        raise HTTPException(status_code=400, detail="Please provide an array of websites to analyze")

    print("🔧 Starting BuiltWith Tech Stack Analysis (Step 2)")
    print("=" * 60)
    
    # Check BuiltWith API key
    builtwith_key = os.getenv("BUILTWITH_API_KEY")
    print(f"BUILTWITH_API_KEY: {'✅' if builtwith_key else '❌'}")
    
    # Initialize BuiltWith client with enhanced logging
    builtwith_client = BuiltWithClient(builtwith_key)
    
    try:
        # Try to get existing data from Supabase first
        existing_data = None
        if supabase:
            try:
                print("📊 Retrieving existing SimilarWeb data from Supabase...")
                result = supabase.table("users").select("similarweb_result").eq("id", request.userId).execute()
                if result.data and len(result.data) > 0 and result.data[0]["similarweb_result"]:
                    existing_data = json.loads(result.data[0]["similarweb_result"])
                    print(f"✅ Found existing data for {len(existing_data)} websites")
                else:
                    print("⚠️ No existing SimilarWeb data found in Supabase")
            except Exception as e:
                print(f"❌ Error retrieving existing data: {e}")
        
        # If no existing data, use mock data or get fresh data
        if not existing_data:
            print("📋 Using mock data as base for BuiltWith analysis...")
            mock_data = get_mock_data()
            # Remove existing BuiltWith data
            for item in mock_data:
                item.builtwith_result = None
            results = mock_data
        else:
            # Convert existing data back to ApifyResult objects
            print("🔄 Converting existing SimilarWeb data to objects...")
            results = []
            for item_data in existing_data:
                try:
                    # Remove existing BuiltWith data if any
                    item_data.pop('builtwith_result', None)
                    result = ApifyResult(**item_data)
                    results.append(result)
                except Exception as e:
                    print(f"❌ Error converting data item: {e}")
                    continue
        
        print(f"🎯 Starting BuiltWith analysis for {len(results)} websites...")
        print("-" * 60)
        
        # Add BuiltWith analysis for each domain
        for i, website_result in enumerate(results):
            # Extract domain from website name or use the provided URL
            if i < len(request.websites):
                website_url = request.websites[i]
            else:
                # Fallback: construct domain from website name
                website_url = website_result.name.lower().replace(" ", "") + ".com"
            
            print(f"\n🔍 Step 2.{i+1}: Analyzing {website_url}")
            print(f"   Website: {website_result.name}")
            print(f"   Global Rank: #{website_result.globalRank}")
            
            try:
                builtwith_result = await builtwith_client.analyze_domain(website_url)
                results[i].builtwith_result = builtwith_result
                
                tech_count = len(builtwith_result.technologies) if builtwith_result.technologies else 0
                print(f"   ✅ BuiltWith analysis complete: {tech_count} technologies found")
                
                if tech_count > 0:
                    # Show first few technologies as preview
                    preview_techs = builtwith_result.technologies[:3]
                    tech_preview = ", ".join([f"{t.name}" for t in preview_techs])
                    print(f"   📋 Preview: {tech_preview}{'...' if tech_count > 3 else ''}")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {website_url}: {e}")
                # Set empty BuiltWith result on error
                results[i].builtwith_result = BuiltWithResult(domain=website_url, technologies=[])
        
        print("\n" + "=" * 60)
        print("💾 Saving enhanced data (SimilarWeb + BuiltWith) to Supabase...")
        
        # Save enhanced data to Supabase
        try:
            if supabase:
                data_to_insert = [item.model_dump() for item in results]
                result = supabase.table("users").update({
                    "similarweb_result": json.dumps(data_to_insert)
                }).eq("id", request.userId).execute()
                print("✅ Enhanced data saved to Supabase successfully")
            else:
                print("⚠️ Supabase client not available, skipping database save")
        except Exception as e:
            print(f"❌ Error saving enhanced data to Supabase: {e}")

        # Calculate summary statistics
        total_technologies = sum(
            len(item.builtwith_result.technologies) if item.builtwith_result else 0 
            for item in results
        )
        
        print(f"🎉 Step 2 Complete!")
        print(f"   Websites analyzed: {len(results)}")
        print(f"   Total technologies found: {total_technologies}")
        print("=" * 60)

        return AnalysisResponse(
            success=True,
            data=results,
            count=len(results),
            note=f"Step 2 complete: BuiltWith analysis added. Found {total_technologies} technologies across {len(results)} websites."
        )

    except Exception as e:
        print(f"\n❌ Error in BuiltWith analysis: {str(e)}")
        print("🔄 Falling back to mock BuiltWith data...")
        
        # Fallback: use mock data with BuiltWith analysis
        mock_data = get_mock_data()
        
        # Save fallback data to Supabase
        try:
            if supabase:
                data_to_insert = [item.model_dump() for item in mock_data]
                result = supabase.table("users").update({
                    "similarweb_result": json.dumps(data_to_insert)
                }).eq("id", request.userId).execute()
                print("✅ Fallback data saved to Supabase successfully")
        except Exception as save_error:
            print(f"❌ Error saving fallback data: {save_error}")
            
        return AnalysisResponse(
            success=True,
            data=mock_data,
            count=len(mock_data),
            note=f"Step 2 complete (with fallback): BuiltWith analysis added. Error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
