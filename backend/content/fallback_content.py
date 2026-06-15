from django.utils import timezone


def _category(name, slug, description, order):
    return {
        'id': order,
        'name': name,
        'slug': slug,
        'description': description,
        'icon': '',
        'order': order,
    }


DEMO_CATEGORIES = [
    _category('News', 'news', 'Fast-moving technology and public-interest updates.', 1),
    _category('Startups', 'startups', 'Funding, builders, products, and African tech companies.', 2),
    _category('Business', 'business', 'Market moves, policy, platforms, and telecoms.', 3),
    _category('Reviews', 'reviews', 'Practical product reviews and buying guidance.', 4),
    _category('Opinion', 'opinion', 'Analysis and arguments worth interrogating.', 5),
    _category('Deep Dive', 'deep-dive', 'Explainers that slow the news down.', 6),
]


def demo_articles():
    now = timezone.now().isoformat()
    cats = {category['slug']: category for category in DEMO_CATEGORIES}
    author = {
        'id': 1,
        'display_name': 'Factly Editorial Team',
        'bio': 'Independent fact-checking and verification team dedicated to fighting misinformation through evidence-based analysis.',
        'avatar': '',
        'position': 'Senior Verification Analyst',
        'twitter': '',
        'linkedin': '',
        'website': '',
    }

    articles = [
        {
            'id': 1001,
            'title': 'Did CO2 levels really hit a record high in 2025?',
            'slug': 'co2-levels-record-high-2025-verification',
            'excerpt': 'Multiple news outlets reported that atmospheric CO2 reached an all-time high. We verified the data against NOAA and Scripps measurements.',
            'content': (
                'In May 2025, several news organizations reported that atmospheric carbon dioxide levels had reached a new record high of 427 ppm. '
                'FACTLY verified this claim by cross-referencing data from NOAAs Global Monitoring Laboratory and the Scripps Institution of Oceanographys '
                'Keeling Curve. Both sources confirm that the monthly average at Mauna Loa Observatory peaked at 427.3 ppm in May 2025, consistent with the '
                'long-term upward trend driven by fossil fuel emissions and deforestation. The claim is accurate, though seasonal fluctuations mean CO2 levels '
                'dip slightly in summer months due to plant growth. The underlying trend remains clear: atmospheric CO2 has risen by over 50% since '
                'pre-industrial levels of approximately 280 ppm.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&w=1200&q=80',
            'category': cats['news'],
            'tags': [],
            'author': author,
            'is_featured': True,
            'is_trending': True,
            'read_time': 6,
            'published_at': now,
            'verdict': 'Verified: True',
            'credibility_score': 94,
        },
        {
            'id': 1002,
            'title': 'Can a new AI model actually detect deepfake videos with 99% accuracy?',
            'slug': 'ai-deepfake-detection-99-percent-claim',
            'excerpt': 'A startup claims their AI can spot deepfakes with near-perfect accuracy. We examined the methodology, dataset, and independent evaluations.',
            'content': (
                'A San Francisco-based startup recently announced an AI system capable of detecting deepfake videos with 99% accuracy. '
                'Our investigation reveals this claim is partially true but requires important context. The model achieves 99% accuracy on the '
                'startups own test dataset, heavily weighted toward older deepfake generation methods (FaceSwap, DeepFaceLab from 2022-2023). '
                'When tested against more recent deepfake techniques from 2024-2025, including diffusion-based video synthesis, accuracy drops '
                'to approximately 87%. Independent researchers at MIT Media Lab were unable to replicate the 99% result with newer deepfake samples. '
                'The claim does not disclose these limitations. We rate this as Mostly True with significant caveats.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1200&q=80',
            'category': cats['deep-dive'],
            'tags': [],
            'author': author,
            'is_featured': True,
            'is_trending': True,
            'read_time': 8,
            'published_at': now,
            'verdict': 'Mostly True',
            'credibility_score': 72,
        },
        {
            'id': 1003,
            'title': 'Did smartphone sales in Africa grow 15% despite global decline?',
            'slug': 'africa-smartphone-sales-growth-2025',
            'excerpt': 'Counterpoint Research reported that African smartphone shipments grew while global markets shrank. We verified the data and methodology.',
            'content': (
                'Counterpoint Researchs Q1 2025 report indicates that African smartphone shipments grew 15.3% year-over-year, contrasting with a '
                '2.1% global decline. FACTLY verified this claim by examining the full report methodology. Growth was driven primarily by Nigeria (+28%), '
                'Kenya (+22%), and Egypt (+18%), with Transsion brands (Tecno, Infinix, Itel) maintaining 48% market share. The research uses manufacturer '
                'shipment data, retail channel checks, and customs data across 12 African markets. Note: the report covers only 12 of 54 African countries, '
                'representing approximately 75% of the continents smartphone market. The 15% figure is accurate for the covered markets.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1526470498-9ae73c665de8?auto=format&fit=crop&w=1200&q=80',
            'category': cats['startups'],
            'tags': [],
            'author': author,
            'is_featured': True,
            'is_trending': False,
            'read_time': 5,
            'published_at': now,
            'verdict': 'Verified: True',
            'credibility_score': 88,
        },
        {
            'id': 1004,
            'title': 'Do electric vehicles produce more lifetime emissions than gas cars?',
            'slug': 'ev-lifetime-emissions-vs-gas-verification',
            'excerpt': 'A viral social media post claims EVs are worse for the environment. We examined the full lifecycle analysis.',
            'content': (
                'A widely shared post on X claims electric vehicles produce more emissions over their lifetime than gasoline-powered cars due to '
                'battery manufacturing and electricity generation. FACTLY investigated using lifecycle assessment data from the International Council '
                'on Clean Transportation (ICCT), Argonne National Laboratory, and the European Environment Agency. The claim is false. While EV battery '
                'manufacturing produces 15-68% more upstream emissions than producing a gas car engine, this deficit is offset after 18-24 months of '
                'typical driving in most regions. Over a 15-year lifespan, EVs produce 50-70% fewer total emissions in regions with average grid '
                'electricity. In coal-heavy grids, the breakeven point extends to 3-4 years but EVs still produce fewer lifetime emissions. '
                'The viral post selectively cited only manufacturing emissions while ignoring the operational phase.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1544636331-e26879cd4d9b?auto=format&fit=crop&w=1200&q=80',
            'category': cats['opinion'],
            'tags': [],
            'author': author,
            'is_featured': False,
            'is_trending': True,
            'read_time': 10,
            'published_at': now,
            'verdict': 'False',
            'credibility_score': 95,
        },
        {
            'id': 1005,
            'title': 'Is 5G radiation actually harmful? Analyzing the scientific consensus',
            'slug': '5g-radiation-health-effects-scientific-consensus',
            'excerpt': 'Claims about 5G health risks continue to circulate online. We reviewed studies from WHO, ICNIRP, and national health agencies.',
            'content': (
                'Recurring claims about 5G radiation causing everything from headaches to cancer persist across social media. FACTLY analyzed the '
                'scientific consensus by reviewing over 50 studies from WHO, ICNIRP, the American Cancer Society, and national health agencies in '
                'the EU, UK, Australia, and Japan. The consistent conclusion is that 5G operates within non-ionizing radiofrequency ranges that '
                'do not have sufficient energy to damage DNA directly. Current evidence does not establish causal links between 5G exposure and '
                'adverse health effects when operating within regulatory limits. However, WHO notes research gaps exist for long-term exposure and '
                'calls for continued monitoring. Claims that 5G causes COVID-19 are demonstrably false and have been repeatedly debunked.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?auto=format&fit=crop&w=1200&q=80',
            'category': cats['news'],
            'tags': [],
            'author': author,
            'is_featured': False,
            'is_trending': True,
            'read_time': 12,
            'published_at': now,
            'verdict': 'Mostly False',
            'credibility_score': 91,
        },
        {
            'id': 1006,
            'title': 'Do megapixels actually matter in budget phones in 2025?',
            'slug': 'budget-phone-camera-megapixels-2025-review',
            'excerpt': 'Phone manufacturers keep increasing megapixel counts. We tested whether higher MP means better photos in budget devices.',
            'content': (
                'Multiple budget phone manufacturers advertise 108MP and 200MP cameras in devices under $300. FACTLY conducted a controlled test '
                'comparing six budget phones ($150-$300 range) with 50MP, 64MP, 108MP, and 200MP sensors. Results: Higher megapixel counts provided '
                'marginal benefits in bright daylight (approximately 8% more resolvable detail) but performed worse in low light due to smaller '
                'individual pixel sizes. The 50MP and 64MP sensors with larger individual pixels (1.0-1.4 microns) produced better overall image '
                'quality. Software processing quality was a stronger predictor of final image quality than raw megapixel count. Claims that more '
                'megapixels always mean better photos are misleading.'
            ),
            'featured_image': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80',
            'category': cats['reviews'],
            'tags': [],
            'author': author,
            'is_featured': False,
            'is_trending': True,
            'read_time': 9,
            'published_at': now,
            'verdict': 'Buying Guide',
            'credibility_score': 90,
        },
    ]

    return articles


def demo_article_detail(slug):
    for article in demo_articles():
        if article['slug'] == slug:
            detail = article.copy()
            detail['created_at'] = detail['published_at']
            detail['updated_at'] = detail['published_at']
            return detail
    return None


def demo_homepage():
    articles = demo_articles()
    sections = {}
    for category in DEMO_CATEGORIES:
        category_articles = [
            article for article in articles
            if article['category']['slug'] == category['slug']
        ]
        if category_articles:
            sections[category['slug']] = {
                'category': category,
                'articles': category_articles,
            }

    return {
        'featured': [article for article in articles if article['is_featured']],
        'trending': [article for article in articles if article['is_trending']],
        'latest': articles,
        'sections': sections,
        'data_source': 'editorial_fallback',
    }
