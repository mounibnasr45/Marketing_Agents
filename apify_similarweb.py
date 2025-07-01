from apify_client import ApifyClient
import matplotlib.pyplot as plt
import pandas as pd

# Your actual Apify API token here
client = ApifyClient("apify_api_D1WtSruXP25zCSTScrfBCjEPUZHsds058RFn")

# Input: list of websites to analyze
run_input = {
    "websites": [
        "https://www.linkedin.com",
        "https://www.github.com",
        "https://www.medium.com"
    ]
}


# Run the Similarweb scraper Actor
run = client.actor("heLi1j7hzjC2gFlIx").call(run_input=run_input)

# Store all results for analysis
results = list(client.dataset(run["defaultDatasetId"]).iterate_items())

print(f"📊 Retrieved {len(results)} results")

# Debug: Print the structure of the first result
if results:
    print("\n🔍 Debug - First result structure:")
    first_result = results[0]
    for key, value in first_result.items():
        print(f"  {key}: {type(value)} = {value}")
    print("\n" + "="*50)

# --- Display & Visualize Each Website ---
for item in results:
    # Extract domain name from the API response
    domain = item.get("name", "Unknown Domain")
    if domain == "Unknown Domain":
        # Try alternative fields
        url = item.get("url", "")
        if "website/" in url:
            domain = url.split("website/")[-1].replace("www.", "")
    
    print(f"\n🌐 Domain: {domain}")
    print(f"📊 Global Rank: {item.get('globalRank', 'N/A')}")
    print(f"� Country Rank: {item.get('countryRank', 'N/A')}")
    print(f"📈 Category Rank: {item.get('categoryRank', 'N/A')}")
    print(f"🏢 Company: {item.get('companyName', 'N/A')}")
    print(f"📅 Founded: {item.get('companyYearFounded', 'N/A')}")
    
    total_visits = item.get('totalVisits')
    if total_visits is not None:
        print(f"👥 Total Visits (Latest): {total_visits:,}")
    else:
        print(f"👥 Total Visits (Latest): N/A")
    
    # Display engagement metrics
    avg_duration = item.get('avgVisitDuration', 'N/A')
    pages_per_visit = item.get('pagesPerVisit', 'N/A')
    bounce_rate = item.get('bounceRate')
    
    print(f"⏱️ Avg Visit Duration: {avg_duration}")
    print(f"📄 Pages per Visit: {pages_per_visit}")
    if bounce_rate is not None:
        print(f"🔄 Bounce Rate: {bounce_rate:.2%}")
    else:
        print(f"🔄 Bounce Rate: N/A")

    # --- Pie Chart: Traffic Source Breakdown ---
    traffic_sources_data = item.get("trafficSources", {})
    if traffic_sources_data:
        traffic_sources = {
            "Direct": traffic_sources_data.get("directVisitsShare", 0),
            "Organic Search": traffic_sources_data.get("organicSearchVisitsShare", 0),
            "Referral": traffic_sources_data.get("referralVisitsShare", 0),
            "Social": traffic_sources_data.get("socialNetworksVisitsShare", 0),
            "Mail": traffic_sources_data.get("mailVisitsShare", 0),
            "Paid Search": traffic_sources_data.get("paidSearchVisitsShare", 0),
            "Ads": traffic_sources_data.get("adsVisitsShare", 0)
        }
        
        # Filter out zero values
        valid_traffic_sources = {k: v for k, v in traffic_sources.items() if v > 0}
        
        if valid_traffic_sources:
            plt.figure(figsize=(8, 6))
            plt.title(f"{domain} - Traffic Source Breakdown")
            plt.pie(valid_traffic_sources.values(), labels=valid_traffic_sources.keys(), 
                    autopct="%1.1f%%", startangle=140)
            plt.axis('equal')
            plt.tight_layout()
            # Save chart instead of showing interactively
            chart_filename = f"{domain.replace('.', '_')}_traffic_sources.png"
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📊 Traffic chart saved as: {chart_filename}")
            
            # Print traffic sources as percentages
            print("\n📊 Traffic Sources:")
            for source, share in valid_traffic_sources.items():
                print(f"  {source}: {share:.2%}")
        else:
            print(f"⚠️ No valid traffic source data available for {domain}")
    else:
        print(f"⚠️ No traffic source data available for {domain}")

    # --- Display Top Countries ---
    top_countries = item.get("topCountries", [])
    if top_countries:
        print("\n🌍 Top Countries:")
        for i, country in enumerate(top_countries[:5], 1):
            country_code = country.get('countryAlpha2Code', 'Unknown')
            visits_share = country.get('visitsShare', 0)
            print(f"  {i}. {country_code}: {visits_share:.2%}")
    
    # --- Display Top Keywords ---
    top_keywords = item.get("topKeywords", [])
    if top_keywords:
        print("\n🔍 Top Keywords:")
        for i, keyword in enumerate(top_keywords[:5], 1):
            name = keyword.get('name', 'Unknown')
            volume = keyword.get('volume', 0)
            estimated_value = keyword.get('estimatedValue', 0)
            print(f"  {i}. {name} (Volume: {volume:,}, Est. Value: {estimated_value:,})")
    
    # --- Display Social Network Distribution ---
    social_networks = item.get("socialNetworkDistribution", [])
    if social_networks:
        print("\n📱 Social Network Distribution:")
        for network in social_networks[:5]:
            name = network.get('name', 'Unknown')
            share = network.get('visitsShare', 0)
            print(f"  {name}: {share:.2%}")
    
    # --- Display Top Competitors ---
    competitors = item.get("topSimilarityCompetitors", [])
    if competitors:
        print("\n🏆 Top Competitors:")
        for i, competitor in enumerate(competitors[:5], 1):
            domain_name = competitor.get('domain', 'Unknown')
            visits = competitor.get('visitsTotalCount', 0)
            affinity = competitor.get('affinity', 0)
            print(f"  {i}. {domain_name} (Visits: {visits:,}, Affinity: {affinity:.2f})")
    
    # --- Age and Gender Distribution ---
    age_distribution = item.get("ageDistribution", [])
    if age_distribution:
        print("\n👥 Age Distribution:")
        for age_group in age_distribution:
            min_age = age_group.get('minAge', '')
            max_age = age_group.get('maxAge', '')
            value = age_group.get('value', 0)
            age_range = f"{min_age}-{max_age}" if max_age else f"{min_age}+"
            print(f"  {age_range}: {value:.2%}")
    
    male_dist = item.get("maleDistribution")
    female_dist = item.get("femaleDistribution")
    if male_dist is not None and female_dist is not None:
        print(f"\n⚧ Gender Distribution:")
        print(f"  Male: {male_dist:.2%}")
        print(f"  Female: {female_dist:.2%}")
        
    print("\n" + "="*50)  # Separator between websites
