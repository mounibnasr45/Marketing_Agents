"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  BarChart3,
  Users,
  MousePointer,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Smartphone,
  Monitor,
  Loader2,
  AlertCircle,
  TrendingUp,
  Globe,
  Search,
  Share2,
  Target,
} from "lucide-react";

// Define the interface for the analysis result data
interface TrafficSources {
  directVisitsShare: number;
  organicSearchVisitsShare: number;
  referralVisitsShare: number;
  socialNetworksVisitsShare: number;
  mailVisitsShare: number;
  paidSearchVisitsShare: number;
  adsVisitsShare: number;
}

interface TopCountry {
  countryAlpha2Code: string;
  visitsShare: number;
  visitsShareChange: number;
}

interface TopKeyword {
  name: string;
  volume: number;
  estimatedValue: number;
  cpc: number;
}

interface SocialNetworkDistribution {
  name: string;
  visitsShare: number;
}

interface TopSimilarityCompetitor {
  domain: string;
  visitsTotalCount: number;
  affinity: number;
  categoryRank: number;
}

interface ApifyResult {
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

export default function SimilarwebSimulator() {
  const [selectedDomain, setSelectedDomain] = useState("");
  const [analysisData, setAnalysisData] = useState<ApifyResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState("6m");
  const [device, setDevice] = useState("all");
  const [predefinedWebsites] = useState([
    "linkedin.com",
    "github.com", 
    "medium.com"
  ]);

  const analyzeDomain = async (domains: string[]) => {
    setLoading(true);
    setError(null);
    
    try {
      // Use FastAPI backend
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websites: domains.map(domain => 
            domain.startsWith('http') ? domain : `https://www.${domain}`
          ),
          userId: "123e4567-e89b-12d3-a456-426614174000" // Valid UUID format
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || 'Failed to analyze domain');
      }

      setAnalysisData(result.data);
      
      // Show note if using mock data
      if (result.note) {
        console.log('ℹ️', result.note);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeClick = () => {
    if (selectedDomain.trim()) {
      analyzeDomain([selectedDomain.trim()]);
    }
  };

  const handleAnalyzePredefined = () => {
    analyzeDomain(predefinedWebsites);
  };

  const currentWebsite = analysisData.length > 0 ? analysisData[0] : null;

  // Helper function to format numbers
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">SimilarWeb Analytics</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Input
                  placeholder="Enter domain (e.g., example.com)"
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="w-64"
                  onKeyPress={(e) => e.key === 'Enter' && handleAnalyzeClick()}
                />
                <Button 
                  onClick={handleAnalyzeClick} 
                  disabled={loading || !selectedDomain.trim()}
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Analyze"}
                </Button>
              </div>
            </div>
          </div>
          
          {/* Predefined Analysis Button */}
          <div className="mt-4 flex justify-center">
            <Button 
              onClick={handleAnalyzePredefined}
              disabled={loading}
              className="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Analyzing LinkedIn, GitHub & Medium...
                </>
              ) : (
                <>
                  <Target className="h-4 w-4 mr-2" />
                  Analyze Sample Sites (LinkedIn, GitHub, Medium)
                </>
              )}
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        {/* Error Display */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-lg font-medium">Analyzing website data...</p>
              <p className="text-sm text-muted-foreground mt-2">
                This may take a few minutes to complete
              </p>
            </div>
          </div>
        )}

        {/* No Data State */}
        {!loading && analysisData.length === 0 && !error && (
          <div className="text-center py-12">
            <Search className="h-16 w-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Ready to Analyze Websites
            </h3>
            <p className="text-gray-600 mb-6">
              Enter a domain name or use our sample analysis to get started
            </p>
            <Button 
              onClick={handleAnalyzePredefined}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Target className="h-4 w-4 mr-2" />
              Try Sample Analysis
            </Button>
          </div>
        )}

        {/* Results Display */}
        {!loading && analysisData.length > 0 && (
          <>
            {/* Domain Header */}
            <div className="mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">
                    {currentWebsite?.name || "Website Analysis"}
                  </h2>
                  <p className="text-gray-600">Real-time Digital Intelligence Report</p>
                  {analysisData.length > 1 && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Analyzing {analysisData.length} websites
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-4">
                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1m">1 Month</SelectItem>
                      <SelectItem value="3m">3 Months</SelectItem>
                      <SelectItem value="6m">6 Months</SelectItem>
                      <SelectItem value="1y">1 Year</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={device} onValueChange={setDevice}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Devices</SelectItem>
                      <SelectItem value="desktop">Desktop</SelectItem>
                      <SelectItem value="mobile">Mobile</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="traffic">Traffic & Engagement</TabsTrigger>
                <TabsTrigger value="keywords">Keywords</TabsTrigger>
                <TabsTrigger value="audience">Audience</TabsTrigger>
                <TabsTrigger value="competitors">Competitors</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Global Rank</CardTitle>
                      <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        #{currentWebsite?.globalRank?.toLocaleString() || 'N/A'}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center">
                        <Globe className="h-3 w-3 mr-1" />
                        Global ranking
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Total Visits</CardTitle>
                      <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {currentWebsite?.totalVisits ? formatNumber(currentWebsite.totalVisits) : 'N/A'}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center">
                        <ArrowUpRight className="h-3 w-3 text-green-500 mr-1" />
                        Monthly visits
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Avg. Visit Duration</CardTitle>
                      <Clock className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {currentWebsite?.avgVisitDuration || 'N/A'}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center">
                        <ArrowUpRight className="h-3 w-3 text-green-500 mr-1" />
                        Time per session
                      </p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium">Bounce Rate</CardTitle>
                      <MousePointer className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {currentWebsite?.bounceRate ? `${(currentWebsite.bounceRate * 100).toFixed(1)}%` : 'N/A'}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center">
                        <ArrowDownRight className="h-3 w-3 text-green-500 mr-1" />
                        User engagement
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Traffic Sources */}
                {currentWebsite?.trafficSources && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Traffic Sources</CardTitle>
                      <CardDescription>Breakdown of traffic by source</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(currentWebsite.trafficSources).map(([key, value], index) => {
                          const sourceNames: { [key: string]: string } = {
                            directVisitsShare: 'Direct',
                            organicSearchVisitsShare: 'Organic Search',
                            referralVisitsShare: 'Referrals',
                            socialNetworksVisitsShare: 'Social Networks',
                            mailVisitsShare: 'Email',
                            paidSearchVisitsShare: 'Paid Search',
                            adsVisitsShare: 'Display Ads'
                          };
                          const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-pink-500', 'bg-red-500', 'bg-yellow-500'];
                          
                          if (value > 0) {
                            return (
                              <div key={key} className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`} />
                                  <span className="font-medium">{sourceNames[key] || key}</span>
                                </div>
                                <div className="flex items-center space-x-4">
                                  <div className="text-right">
                                    <div className="font-semibold">{(value * 100).toFixed(1)}%</div>
                                  </div>
                                  <div className="w-24">
                                    <Progress value={value * 100} className="h-2" />
                                  </div>
                                </div>
                              </div>
                            );
                          }
                          return null;
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Company Information */}
                {currentWebsite && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Company Information</CardTitle>
                      <CardDescription>Details about the organization</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-muted-foreground">Company Name</div>
                          <div className="text-lg">{currentWebsite.companyName || 'N/A'}</div>
                        </div>
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-muted-foreground">Founded</div>
                          <div className="text-lg">{currentWebsite.companyYearFounded || 'N/A'}</div>
                        </div>
                        {currentWebsite.companyEmployeesMin && currentWebsite.companyEmployeesMax && (
                          <div className="space-y-2">
                            <div className="text-sm font-medium text-muted-foreground">Employees</div>
                            <div className="text-lg">
                              {currentWebsite.companyEmployeesMin.toLocaleString()} - {currentWebsite.companyEmployeesMax.toLocaleString()}
                            </div>
                          </div>
                        )}
                        <div className="space-y-2">
                          <div className="text-sm font-medium text-muted-foreground">Pages per Visit</div>
                          <div className="text-lg">{currentWebsite.pagesPerVisit || 'N/A'}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="traffic" className="space-y-6">
                {/* Geographic Distribution */}
                {currentWebsite?.topCountries && currentWebsite.topCountries.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Geographic Distribution</CardTitle>
                      <CardDescription>Traffic by country</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {currentWebsite.topCountries.slice(0, 8).map((country, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center space-x-3">
                              <div className="font-medium text-lg">{country.countryAlpha2Code}</div>
                              <div className="text-sm text-muted-foreground">
                                {(country.visitsShare * 100).toFixed(1)}% of traffic
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Badge 
                                className={
                                  country.visitsShareChange > 0 
                                    ? "bg-green-100 text-green-800" 
                                    : country.visitsShareChange < 0 
                                      ? "bg-red-100 text-red-800" 
                                      : "bg-gray-100 text-gray-800"
                                }
                              >
                                {country.visitsShareChange > 0 ? "↗" : country.visitsShareChange < 0 ? "↘" : "→"}
                                {(country.visitsShareChange * 100).toFixed(1)}%
                              </Badge>
                              <Progress value={country.visitsShare * 100} className="w-20 h-2" />
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="keywords" className="space-y-6">
                {/* Top Keywords */}
                {currentWebsite?.topKeywords && currentWebsite.topKeywords.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Top Keywords</CardTitle>
                      <CardDescription>Keywords driving traffic to the site</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {currentWebsite.topKeywords.slice(0, 10).map((keyword, index) => (
                          <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                            <div className="flex-1">
                              <div className="font-medium">{keyword.name}</div>
                              <div className="text-sm text-muted-foreground mt-1">
                                Volume: {keyword.volume?.toLocaleString() || 'N/A'} • 
                                Est. Value: ${keyword.estimatedValue?.toLocaleString() || 'N/A'}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold">${keyword.cpc?.toFixed(2) || 'N/A'}</div>
                              <div className="text-sm text-muted-foreground">CPC</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="audience" className="space-y-6">
                {/* Social Network Distribution */}
                {currentWebsite?.socialNetworkDistribution && currentWebsite.socialNetworkDistribution.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Social Media Traffic</CardTitle>
                      <CardDescription>Traffic from social networks</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {currentWebsite.socialNetworkDistribution.slice(0, 6).map((network, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <Share2 className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm font-medium">{network.name}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className="text-sm font-medium">{(network.visitsShare * 100).toFixed(1)}%</span>
                              <Progress value={network.visitsShare * 100} className="w-16 h-2" />
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="competitors" className="space-y-6">
                {/* Competitor Analysis */}
                {currentWebsite?.topSimilarityCompetitors && currentWebsite.topSimilarityCompetitors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Competitor Analysis</CardTitle>
                      <CardDescription>Similar websites and competitors</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {currentWebsite.topSimilarityCompetitors.slice(0, 8).map((competitor, index) => (
                          <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                            <div className="flex items-center space-x-4">
                              <div className="text-lg font-bold text-muted-foreground">#{index + 1}</div>
                              <div>
                                <div className="font-medium">{competitor.domain}</div>
                                <div className="text-sm text-muted-foreground">
                                  Visits: {formatNumber(competitor.visitsTotalCount)} • 
                                  Category Rank: {competitor.categoryRank || 'N/A'}
                                </div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold">Affinity: {competitor.affinity.toFixed(3)}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>

            {/* Multiple Website Comparison */}
            {analysisData.length > 1 && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Website Comparison</CardTitle>
                  <CardDescription>Compare metrics across all analyzed websites</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {analysisData.map((website, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="font-medium text-lg">{website.name}</div>
                          <div className="text-sm text-muted-foreground">
                            Global Rank: #{website.globalRank?.toLocaleString() || 'N/A'} • 
                            Visits: {website.totalVisits ? formatNumber(website.totalVisits) : 'N/A'}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">{website.companyName || 'N/A'}</div>
                          <div className="text-sm text-muted-foreground">
                            Founded: {website.companyYearFounded || 'N/A'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}
