// Types for the API responses
export interface TrafficSources {
  directVisitsShare: number;
  organicSearchVisitsShare: number;
  referralVisitsShare: number;
  socialNetworksVisitsShare: number;
  mailVisitsShare: number;
  paidSearchVisitsShare: number;
  adsVisitsShare: number;
}

export interface TopCountry {
  countryAlpha2Code: string;
  visitsShare: number;
  visitsShareChange: number;
}

export interface TopKeyword {
  name: string;
  volume: number;
  estimatedValue: number;
  cpc: number;
}

export interface SocialNetworkDistribution {
  name: string;
  visitsShare: number;
}

export interface TopSimilarityCompetitor {
  domain: string;
  visitsTotalCount: number;
  affinity: number;
  categoryRank: number;
}

export interface ApifyResult {
  name: string;
  globalRank: number;
  countryRank: number;
  categoryRank: number;
  companyName: string;
  companyYearFounded: number;
  companyEmployeesMin: number;
  companyEmployeesMax: number;
  totalVisits: number;
  avgVisitDuration: string;
  pagesPerVisit: number;
  bounceRate: number;
  trafficSources: TrafficSources;
  topCountries: TopCountry[];
  topKeywords: TopKeyword[];
  socialNetworkDistribution: SocialNetworkDistribution[];
  topSimilarityCompetitors: TopSimilarityCompetitor[];
  organicTraffic: number;
  paidTraffic: number;
}

export interface AnalysisResponse {
  success: boolean;
  data: ApifyResult[];
  count: number;
  note?: string;
}
