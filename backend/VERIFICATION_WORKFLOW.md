# FACTLY Verification Workflow Design

## Overview

The FACTLY verification system implements a comprehensive, multi-stage workflow for determining the credibility of news headlines, articles, and claims. The system combines NLP-based claim extraction, multi-source evidence gathering, cross-source analysis, and weighted scoring to produce accurate, explainable results.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FACTLY Verification Workflow                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Input (Text/   │
│     URL)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: CLAIM EXTRACTION                                                    │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ ClaimExtractor Service                                                   │ │
│ │ • Sentence tokenization                                                  │ │
│ │ • Factual indicator detection (dates, numbers, statistics)              │ │
│ │ • Claim type classification (factual, quotation, prediction, etc.)      │ │
│ │ • Entity extraction                                                      │ │
│ │ • Verifiability scoring                                                  │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: MULTI-SOURCE EVIDENCE SEARCH                                        │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ EvidenceSearchService                                                    │ │
│ │                                                                          │ │
│ │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │ │
│ │  │ Google Fact     │  │ NewsLdr API     │  │ NewsAPI         │         │ │
│ │  │ Check Tools     │  │ (Primary News)  │  │ (Fallback)      │         │ │
│ │  │ API             │  │                 │  │                 │         │ │
│ │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │ │
│ │           │                    │                    │                   │ │
│ │           └────────────────────┼────────────────────┘                   │ │
│ │                                ▼                                        │ │
│ │                    ┌─────────────────────┐                              │ │
│ │                    │ EvidenceCollection  │                              │ │
│ │                    │ • EvidenceItems     │                              │ │
│ │                    │ • Source diversity  │                              │ │
│ │                    │ • Agreement score   │                              │ │
│ │                    │ • Coverage gaps     │                              │ │
│ │                    └─────────────────────┘                              │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: CROSS-SOURCE ANALYSIS                                               │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ CrossSourceAnalyzer                                                      │ │
│ │                                                                          │ │
│ │ • Source credibility assessment                                          │ │
│ │ • Verdict normalization (True/False/Misleading/etc.)                    │ │
│ │ • Agreement calculation (weighted by credibility)                       │ │
│ │ • Consensus determination                                                │ │
│ │ • Contradiction identification                                           │ │
│ │ • Evidence strength classification                                       │ │
│ │ • Recommended verdict generation                                         │ │
│ │ • Uncertainty factor identification                                      │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: FACTLY SCORE™ CALCULATION                                           │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ ScoringService                                                           │ │
│ │                                                                          │ │
│ │  Component Weights:                                                      │ │
│ │  ┌────────────────────────┬──────────┬─────────────────────────────────┐ │ │
│ │  │ Component              │ Weight   │ Description                     │ │ │
│ │  ├────────────────────────┼──────────┼─────────────────────────────────┤ │ │
│ │  │ NLP Confidence         │ 40%      │ Claim extraction confidence     │ │ │
│ │  │ Google Fact Check      │ 35%      │ Fact-check database results     │ │ │
│ │  │ NewsLdr Credibility    │ 15%      │ Source reliability scores       │ │ │
│ │  │ Language Bias/Tone     │ 10%      │ Linguistic pattern analysis     │ │ │
│ │  └────────────────────────┴──────────┴─────────────────────────────────┘ │ │
│ │                                                                          │ │
│ │  Score Adjustment based on:                                              │ │
│ │  • Consensus level (strong agreement → +5, strong disagreement → -15)   │ │
│ │  • Evidence strength (strong → +5, conflicting → -10)                   │ │
│ │  • Cross-source confidence score                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: SUMMARY GENERATION                                                  │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ SummaryGenerator                                                         │ │
│ │                                                                          │ │
│ │ • Headline generation (Likely True/Uncertain/Likely False)              │ │
│ │ • Explanation composition                                                │ │
│ │ • Key findings extraction                                                │ │
│ │ • Recommendations (share/verify/don't share)                            │ │
│ │ • Confidence statement                                                   │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTPUT: CompleteVerificationResult                                           │
│ • Factly Score™ (0-100)                                                     │
│ • Classification (Likely Authentic/Uncertain/Likely Fake)                   │
│ • Evidence summary                                                          │
│ • Source analysis                                                           │
│ • Human-readable explanation                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

### 1. Multi-Source Verification
- **Never rely on a single source**: The system queries multiple independent APIs
- **Source diversity matters**: Evidence from different types of sources (fact-checkers, news, academic) increases confidence
- **Weighted by credibility**: High-credibility sources (Reuters, AP, BBC) carry more weight than unknown sources

### 2. Cross-Source Consensus
- **Agreement scoring**: Calculate how much sources agree, weighted by their credibility
- **Conflict detection**: Identify and flag when credible sources contradict each other
- **Consensus levels**:
  - Strong Agreement (≥80% agreement)
  - Moderate Agreement (60-80%)
  - Mixed (40-60%)
  - Moderate Disagreement (20-40%)
  - Strong Disagreement (<20%)

### 3. Explainable Results
Every verification result includes:
- **Headline**: Clear true/false/uncertain statement
- **Explanation**: Why the system reached this conclusion
- **Key points**: Bullet points of important findings
- **Evidence**: Sources consulted with their individual assessments
- **Confidence statement**: How confident the system is in its assessment

### 4. Uncertainty Handling
The system explicitly identifies:
- **Coverage gaps**: Missing evidence types (e.g., no fact-checks found)
- **Uncertainty factors**: Why the result might be uncertain
- **Confidence levels**: Low/Medium/High based on evidence quality

## Data Flow

```
1. User Input (Text/URL)
   │
   ├─→ URL Extraction (if URL provided)
   │
   ├─→ Text Preprocessing
   │   • Cleaning (URLs, emails, special chars)
   │   • Tokenization
   │   • Language detection
   │
   └─→ Claim Extraction
       • Identify verifiable claims
       • Score verifiability
       • Select primary claim

2. Evidence Gathering (Parallel where possible)
   │
   ├─→ Google Fact Check API
   │   • Search for existing fact-checks
   │   • Extract verdicts and confidence
   │
   ├─→ NewsLdr API
   │   • Search related news coverage
   │   • Assess source reliability
   │
   └─→ NewsAPI (Fallback)
       • Additional news coverage
       • Credibility scoring by domain

3. Evidence Processing
   │
   ├─→ Normalize verdicts (True/False/Misleading/etc.)
   ├─→ Calculate source credibility scores
   ├─→ Compute relevance scores
   └─→ Identify coverage gaps

4. Analysis
   │
   ├─→ Cross-source comparison
   ├─→ Agreement calculation
   ├─→ Consensus determination
   ├─→ Contradiction identification
   └─→ Recommended verdict generation

5. Scoring
   │
   ├─→ Calculate base Factly Score™
   ├─→ Adjust based on cross-source analysis
   ├─→ Determine classification
   └─→ Assess confidence level

6. Output Generation
   │
   ├─→ Generate headline
   ├─→ Compose explanation
   ├─→ Extract key points
   ├─→ Create recommendations
   └─→ Format confidence statement
```

## API Integration Details

### Google Fact Check Tools API
- **Purpose**: Check if claim has already been fact-checked
- **Rate Limit**: 100 requests per 100 seconds per user
- **Response**: Claim reviews with verdicts from fact-checkers
- **Credibility**: Fact-checkers rated by review count and reputation

### NewsLdr API
- **Purpose**: Find related news coverage and assess source reliability
- **Endpoints**:
  - `/news/search` - Related articles
  - `/sources/reliability` - Source credibility scores
- **Credibility Factors**: Reliability score, bias rating, factual reporting history

### NewsAPI (Fallback)
- **Purpose**: Additional news coverage when NewsLdr is unavailable
- **Domain-based Credibility**: Pre-defined credibility scores for major news outlets
- **Trusted Domains**: Reuters, AP, BBC, NPR, major newspapers

## Scoring Algorithm

### Base Score Calculation
```
Factly Score = (NLP_Score × 0.40) +
               (Google_Score × 0.35) +
               (NewsLdr_Score × 0.15) +
               (Bias_Score × 0.10)
```

### Adjustments
```
Adjusted Score = Base Score +
                 Consensus_Adjustment +
                 Evidence_Strength_Adjustment +
                 Confidence_Boost

Where:
- Consensus_Adjustment: +5 (strong agreement) to -15 (strong disagreement)
- Evidence_Strength_Adjustment: +5 (strong) to -15 (insufficient)
- Confidence_Boost: (Confidence - 0.5) × 20
```

### Classification Thresholds
- **Likely Authentic**: 61-100
- **Uncertain**: 31-60
- **Likely Fake**: 0-30

## Error Handling & Resilience

1. **API Failures**: Continue with available sources, note gaps in response
2. **Rate Limiting**: Built-in rate limiter prevents quota exhaustion
3. **Caching**: TTL cache reduces redundant API calls
4. **Timeouts**: All external calls have timeouts to prevent hanging
5. **Graceful Degradation**: Partial results returned when some sources fail

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **Input Sanitization**: Text cleaned to prevent injection attacks
3. **Rate Limiting**: Per-user rate limits on verification endpoints
4. **Caching**: Sensitive data not cached beyond TTL
