#!/usr/bin/env python3
"""
Test BuiltWith Integration

This script tests our BuiltWith integration by calling our FastAPI endpoint
and verifying that BuiltWith data is included in the response.
"""

import httpx
import asyncio
import json
from main import BuiltWithClient

async def test_builtwith_client():
    """Test the BuiltWith client directly"""
    print("🧪 Testing BuiltWith Client")
    print("=" * 50)
    
    # Test with no API key (should return mock data)
    client = BuiltWithClient(api_key=None)
    
    test_domains = ["linkedin.com", "github.com", "google.com"]
    
    for domain in test_domains:
        print(f"\n📊 Testing domain: {domain}")
        result = await client.analyze_domain(domain)
        print(f"✅ Domain: {result.domain}")
        print(f"✅ Technologies found: {len(result.technologies)}")
        print("✅ Sample technologies:")
        for tech in result.technologies[:5]:  # Show first 5
            print(f"   • {tech.name} ({tech.tag})")
        
        if len(result.technologies) > 5:
            print(f"   ... and {len(result.technologies) - 5} more")

async def test_api_endpoint():
    """Test the FastAPI endpoint with BuiltWith integration"""
    print("\n\n🌐 Testing API Endpoint")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/analyze",
                json={
                    "websites": ["https://www.linkedin.com", "https://www.github.com"],
                    "userId": "test-user-123"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Response successful!")
                print(f"✅ Websites analyzed: {data['count']}")
                
                for i, website_data in enumerate(data['data']):
                    print(f"\n📊 Website {i+1}: {website_data['name']}")
                    
                    if 'builtwith_result' in website_data and website_data['builtwith_result']:
                        builtwith = website_data['builtwith_result']
                        print(f"✅ BuiltWith data found!")
                        print(f"   • Domain: {builtwith['domain']}")
                        print(f"   • Technologies: {len(builtwith['technologies'])}")
                        
                        # Group by category
                        categories = {}
                        for tech in builtwith['technologies']:
                            if tech['tag'] not in categories:
                                categories[tech['tag']] = []
                            categories[tech['tag']].append(tech['name'])
                        
                        print(f"   • Categories: {list(categories.keys())}")
                        for category, techs in categories.items():
                            print(f"     - {category}: {', '.join(techs[:3])}")
                    else:
                        print("❌ No BuiltWith data found")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to API server. Is it running on localhost:8000?")
            print("💡 Start the server with: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

async def main():
    """Run all tests"""
    print("🚀 BuiltWith Integration Test Suite")
    print("=" * 70)
    
    # Test 1: BuiltWith Client
    await test_builtwith_client()
    
    # Test 2: API Endpoint
    await test_api_endpoint()
    
    print("\n" + "=" * 70)
    print("✨ Test suite completed!")
    print("\n💡 To see the frontend integration:")
    print("   1. Start the backend: uvicorn main:app --reload")
    print("   2. Start the frontend: npm run dev")
    print("   3. Visit http://localhost:3000")
    print("   4. Click 'Analyze Sample Sites' and check the 'Tech Stack' tab")

if __name__ == "__main__":
    asyncio.run(main())
