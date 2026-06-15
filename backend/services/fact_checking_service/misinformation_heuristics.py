"""
Known Misinformation Patterns Heuristics

Provides instant verdict for well-documented false claims when
external APIs are unavailable.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MisinformationMatch:
    """Result of matching a claim against known patterns."""
    claim_type: str
    score: int
    classification: str
    confidence: str
    verdict: str
    source_note: str
    evidence: List[str]


class MisinformationHeuristics:
    """
    Heuristics for detecting well-known misinformation patterns.
    Used as fallback when API keys are not configured.
    """

    KNOWN_PATTERNS: List[Tuple] = [
        (
            r'earth is flat',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: The Earth is an oblate spheroid, confirmed by NASA and centuries of scientific evidence.',
            'NASA, global scientific consensus',
            ['NASA satellite imagery shows Earth curvature', 'GPS systems depend on Earth spherical shape', 'Ship hulls disappear bottom-first over horizon']
        ),
        (
            r'vaccines cause autism',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: No causal link between vaccines and autism. The Wakefield study was fraudulent and retracted.',
            'CDC, WHO, Lancet retraction',
            ['Wakefield study was fraudulent and retracted', '10+ studies with millions of children find no link', 'Vaccines save millions of lives annually']
        ),
        (
            r'5g (causes|caused|spread) covid',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: COVID-19 is caused by a virus (SARS-CoV-2), not 5G radiation.',
            'WHO, scientific consensus',
            ['Viruses cannot be transmitted via electromagnetic waves', 'COVID spread in areas without 5G', 'WHO states 5G does not spread COVID']
        ),
        (
            r'5g.*(harmful|dangerous|radiation|cancer|health risk)',
            'mostly false', 3, 'Misleading', 'Medium',
            'MOSTLY FALSE: 5G operates within non-ionizing radiofrequency ranges that do not have sufficient energy to damage DNA directly.',
            'WHO, ICNIRP, American Cancer Society',
            ['5G uses non-ionizing radiation which cannot damage DNA', 'Regulatory limits are set well below harmful levels', 'WHO: no established health effects from 5G within limits']
        ),
        (
            r'moon landing (is |was )?(fake|hoax)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: Moon landings (1969-1972) are documented historical facts with overwhelming evidence.',
            'NASA, physical samples, independent verification',
            ['382 kg of lunar rocks returned to Earth', 'Retroreflectors on Moon still used for laser ranging', 'Soviet Luna probes independently tracked Apollo missions']
        ),
        (
            r'(covid|corona|coronavirus).*(bioweapon|lab leak|manufactured|man made|artificial)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: SARS-CoV-2 is a naturally occurring coronavirus, not a bioweapon. The lab leak theory remains unproven.',
            'WHO, NIH, scientific consensus',
            ['Genetic analysis shows natural evolutionary origin', 'No evidence of genetic engineering in SARS-CoV-2', 'Most scientists support natural zoonotic origin']
        ),
        (
            r'(covid|corona).*(mask|face mask).*(doesn\'t work|useless|harmful|oxygen)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Masks significantly reduce respiratory droplet transmission when properly worn.',
            'CDC, WHO, multiple peer-reviewed studies',
            ['Systematic reviews show masks reduce transmission', 'N95 masks filter 95% of airborne particles', 'Surgical masks reduce droplet spread by 70%+']
        ),
        (
            r'(covid|corona|vaccine).*(microchip|tracking|nanobots|bill gates)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: COVID-19 vaccines do not contain microchips, tracking devices, or nanobots.',
            'FDA, CDC, fact-checking organizations',
            ['Vaccine ingredients are publicly listed by manufacturers', 'No microchip technology is small enough for needles', 'Bill Gates has no involvement in vaccine microchip technology']
        ),
        (
            r'(climate change|global warming).*(hoax|fake|not real|doesn\'t exist|natural cycle)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: Human-caused climate change is real and supported by overwhelming scientific evidence.',
            'NASA, NOAA, IPCC, 99%+ scientific consensus',
            ['97-99.9% of climate scientists agree on human-caused warming', 'Global average temperature has risen 1.2C since pre-industrial', 'CO2 levels highest in at least 800,000 years']
        ),
        (
            r'(solar|wind|renewable).*(don\'t work|too expensive|unreliable|can\'t power)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Renewable energy is increasingly cost-competitive and reliable with modern grid technology.',
            'IEA, Lazard, multiple energy agencies',
            ['Solar and wind are now cheapest electricity sources in many regions', 'Grid-scale battery storage solves intermittency', 'Renewables powered 30%+ of global electricity in 2023']
        ),
        (
            r'(election|voter).*(fraud|rigged|stolen|illegal)',
            'false', 5, 'Likely Fake', 'Medium',
            'FALSE: Claims of widespread election fraud have been repeatedly dismissed by courts and investigations.',
            'US courts, Department of Justice, election security experts',
            ['60+ court cases found no evidence of widespread fraud', 'Audits and recounts confirmed election results', 'Bipartisan election officials verified vote counts']
        ),
        (
            r'(ivermectin|hydroxychloroquine).*(cure|treatment|effective).*(covid|corona)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Ivermectin and hydroxychloroquine have not been proven effective for treating or preventing COVID-19.',
            'FDA, WHO, NIH, multiple clinical trials',
            ['Large randomized trials showed no significant benefit', 'FDA revoked emergency use authorization', 'WHO recommends against use outside clinical trials']
        ),
        (
            r'chemtrails',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Condensation trails (contrails) from aircraft are just ice crystals, not chemical spraying.',
            'NASA, EPA, scientific consensus',
            ['Contrails are composed of ice crystals from engine exhaust', 'Satellite imagery shows contrails dissipate normally', 'No evidence of large-scale chemical spraying programs']
        ),
        (
            r'(drinking|using).*bleach.*(cure|treatment|kill virus)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: Drinking or injecting bleach is extremely dangerous and can be fatal.',
            'FDA, poison control centers',
            ['Bleach is a toxic chemical not for human consumption', 'CDC warns against ingesting disinfectants', 'Multiple deaths reported from bleach consumption']
        ),
        (
            r'(fluoride|fluoridation).*(poison|dangerous|harmful|toxic|communist)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Water fluoridation at recommended levels is safe and prevents tooth decay.',
            'CDC, WHO, American Dental Association',
            ['Fluoridation reduces cavities by 25% in children and adults', 'Recommended levels (0.7 mg/L) are well below toxic thresholds', 'CDC named fluoridation one of 10 great public health achievements']
        ),
        (
            r'(gmo|genetically modified).*(dangerous|cancer|harmful|unsafe|toxic)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: GMOs approved for consumption are safe and rigorously tested.',
            'WHO, FDA, National Academies of Sciences',
            ['Thousands of studies confirm GMO safety', 'National Academies found no health risks from approved GMOs', 'GMOs reduce pesticide use and increase crop yields']
        ),
        (
            r'(alien|extraterrestrial|ufo).*(area 51|roswell|government cover|crash)',
            'unverified', 1, 'Unverified', 'Low',
            'UNVERIFIED: Many UFO claims lack verifiable evidence and official confirmation.',
            'Various sources',
            ['Most UFO sightings have conventional explanations', 'Government reports find no evidence of extraterrestrial technology', 'Extraordinary claims require extraordinary evidence']
        ),
        (
            r'(hiv|aids).*(doesn\'t cause|hoax|not real|man made|manufactured)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: HIV causes AIDS and the virus is well-documented in scientific literature.',
            'WHO, CDC, NIH',
            ['HIV is a well-characterized retrovirus', '34+ million people have died from AIDS-related illnesses', 'Antiretroviral therapy effectively manages HIV']
        ),
        (
            r'(911|9/11).*(inside job|controlled demo|bush did|thermite|never happened)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: The 9/11 attacks were carried out by Al-Qaeda, as confirmed by extensive investigations.',
            '9/11 Commission Report, NIST investigations',
            ['NIST investigation explained building collapses scientifically', '9/11 Commission Report documented hijackers and planning', 'Multiple independent investigations confirmed official account']
        ),
        (
            r'(school shooting|mass shooting).*(false flag|crisis actor|hoax)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: School shootings are real tragedies, not staged events. Crisis actor claims are baseless.',
            'FBI, local law enforcement, verified journalism',
            ['Multiple independent sources confirm shootings occurred', 'Victim identities and funerals are publicly documented', 'Crisis actor claims have been repeatedly debunked']
        ),
        (
            r'(holocaust|auschwitz|nazi).*(hoax|fake|never happened|exaggerated)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: The Holocaust is one of the best-documented genocides in history.',
            'Historical archives, survivor testimony, war crime trials',
            ['Extensive Nazi documentation of the genocide exists', 'Liberated camps were documented by Allied forces', 'Survivor testimony and physical evidence are overwhelming']
        ),
        (
            r'(sandy hook|parkland|las vegas shooting).*(false flag|crisis actor|hoax|staged)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: Mass shootings are real tragedies with verified victims and evidence.',
            'FBI, local police, medical examiner reports',
            ['Autopsy reports confirm victims and cause of death', 'Surveillance footage and 911 calls are documented', 'Perpetrators are identified and their histories verified']
        ),
        (
            r'(obama|biden|clinton).*(born in|birth certificate|not american|kenya)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: President Obama was born in Hawaii, confirmed by his birth certificate.',
            'Hawaii Department of Health, fact-checkers',
            ['Obamas birth certificate was released and verified by Hawaii officials', 'Newspaper birth announcements from 1961 exist', 'Birther claims have been debunked by multiple investigations']
        ),
        (
            r'(pizzagate|wayfair|adrenochrome|satanic panic)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: Pizzagate and similar conspiracy theories have been thoroughly debunked.',
            'FBI, fact-checking organizations, multiple investigations',
            ['Pizzagate originated from hacked and leaked emails taken out of context', 'No evidence supports human trafficking conspiracy claims', 'Shooter investigated Comet Pizza, found no evidence']
        ),
        (
            r'(qanon|q anon|digital soldier|great awakening|storm is coming)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: QAnon conspiracy theories are baseless and have no factual foundation.',
            'FBI, fact-checkers, multiple investigations',
            ['QAnon predictions have consistently failed to materialize', 'FBI designated QAnon as a potential domestic terror threat', 'No anonymous online posts have proven credible']
        ),
        (
            r'(flat earth|flat-earth)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: The Earth is a sphere, as proven by centuries of scientific observation.',
            'NASA, global scientific consensus',
            ['Earth photographed from space by multiple space agencies', 'Circumnavigation proves spherical Earth', 'Gravity and physics depend on Earths spherical shape']
        ),
        (
            r'vaccines? (are|is) unsafe',
            'mostly false', 3, 'Misleading', 'Medium',
            'MOSTLY FALSE: Vaccines are rigorously tested for safety and are one of the safest medical interventions.',
            'FDA, CDC, WHO',
            ['Vaccines undergo years of clinical trials before approval', 'VAERS tracks adverse events transparently', 'Serious vaccine side effects are extremely rare']
        ),
        (
            r'(covid|corona).*(death.?toll|mortality|death rate).*(exaggerated|fake|overcount|inflated)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: COVID-19 death tolls may actually be undercounted in many regions.',
            'WHO, CDC, Lancet studies',
            ['Multiple studies suggest actual deaths exceed reported counts', 'Excess mortality analysis confirms pandemic severity', 'Under-counting is more common than over-counting']
        ),
        (
            r'(sandy hook|parkland|tree of life).*(survivor|victim).*(actor|paid)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: Shooting survivors are real people, not paid actors.',
            'Verified media reports, public records',
            ['Survivors have spoken publicly with documentation', 'Funeral records and obituaries confirm victims', 'Crisis actor claims have been successfully sued for defamation']
        ),
        (
            r'(trump|biden|obama).*(impeach|impeachment).*(illegal|invalid|unconstitutional)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Impeachment is a constitutional process defined in the US Constitution.',
            'US Constitution, Congressional Record',
            ['Impeachment is explicitly outlined in Article II of the Constitution', 'House has sole power of impeachment, Senate has sole power to try', 'Historical precedent exists from multiple presidential impeachments']
        ),
        (
            r'(immigrant|migrant|refugee).*(crime wave|violent|dangerous|rapist)',
            'mostly false', 3, 'Misleading', 'Medium',
            'MOSTLY FALSE: Studies consistently show immigrants commit crimes at lower rates than native-born citizens.',
            'Cato Institute, Brennan Center, academic research',
            ['Multiple studies show lower incarceration rates for immigrants', 'No evidence of immigrant crime waves', 'Communities with more immigration see crime reductions']
        ),
        (
            r'(minimum wage|min wage).*(hurts|kills|destroys|bad for).*(job|economy|business)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Research on minimum wage effects is mixed, but moderate increases do not cause significant job loss.',
            'Economic research, CBO, academic studies',
            ['CBO estimates small job loss but significant poverty reduction', 'Seattle and other city studies found minimal employment effects', 'Many studies find no significant negative employment impact']
        ),
        (
            r'china.*(created|manufactured|released|originated).*(covid|corona|virus|pandemic)',
            'false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: COVID-19 is a naturally occurring virus, not deliberately created by China.',
            'WHO, NIH, scientific consensus',
            ['No evidence of deliberate creation or release', 'Genetic analysis shows natural evolutionary origins', 'Lab leak theory is unproven and different from deliberate creation']
        ),
        (
            r'(drink|consume|take).*(colloidal silver|turpentine|chlorine dioxide|MMS).*(cure|treatment|health)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: These substances are dangerous and not approved for medical treatment.',
            'FDA, poison control',
            ['Colloidal silver can cause permanent skin discoloration', 'MMS (bleach) has caused poisonings and deaths', 'No evidence these substances treat any disease']
        ),
        (
            r'(reptilian|reptile|shape.?shift|lizard person)',
            'false', 8, 'Likely Fake', 'High',
            'FALSE: Reptilian humanoid conspiracy theories have no basis in reality.',
            'Scientific consensus',
            ['No evidence of shape-shifting reptilian humanoids', 'Conspiracy theory originated from fringe fiction', 'No credible sources support these claims']
        ),
        (
            r'(new world order|nwo|globalist|one world government)',
            'unverified', 1, 'Unverified', 'Low',
            'UNVERIFIED: Claims of a secret world government conspiracy lack credible evidence.',
            'Various sources',
            ['No verified evidence of a secret world government', 'International organizations operate transparently', 'Conspiracy theory has evolved over decades without proof']
        ),
        (
            r'(vaccine|vaccination).*(shedding|shed).*(dangerous|harmful|unvaccinated)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: While some vaccine shedding occurs with live attenuated vaccines, it is not dangerous to others under normal circumstances.',
            'CDC, FDA, peer-reviewed research',
            ['mRNA vaccines (COVID-19) do not cause shedding', 'Live vaccines can shed but typically cause mild or no symptoms', 'Herd immunity benefits outweigh minimal shedding risks']
        ),
        (
            r'covid.*(delta|omicron|variant).*(mild|just a cold|no worse than flu)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: While some variants cause milder illness in some populations, COVID-19 remains more severe than influenza.',
            'CDC, WHO, Lancet studies',
            ['COVID-19 hospitalization rates higher than flu even with variants', 'Long COVID affects a significant percentage of cases', 'COVID-19 mortality remains higher than seasonal influenza']
        ),
        (
            r'(abortion|terminate pregnancy).*(cause|lead to).*(breast cancer|infertility|mental illness)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Abortion does not cause breast cancer, infertility, or mental illness.',
            'WHO, American Cancer Society, American College of OB/GYN',
            ['No causal link between abortion and breast cancer', 'Abortion does not affect future fertility', 'Most women experience relief, not mental health problems']
        ),
        (
            r'(sugar|candy|soda|soft drink).*(cause|causes).*(cancer|cancerous)',
            'mostly false', 1, 'Misleading', 'Low',
            'MISLEADING: While excessive sugar consumption contributes to obesity (a cancer risk factor), sugar itself is not directly carcinogenic.',
            'American Cancer Society, WHO, scientific studies',
            ['Obesity from excess sugar increases cancer risk', 'Sugar itself is not a direct carcinogen', 'Moderate sugar consumption is not linked to cancer']
        ),
        (
            r'(organic|non-gmo|natural).*(better|healthier|more nutritious) than',
            'mostly false', 1, 'Misleading', 'Medium',
            'MOSTLY FALSE: Organic food is not necessarily more nutritious than conventional food.',
            'Stanford University, Mayo Clinic, scientific reviews',
            ['Large meta-analyses find no significant nutritional difference', 'Organic produce has lower pesticide residues but similar nutrients', '"Natural" labeling is not regulated and can be misleading']
        ),
        (
            r'(cell phone|mobile phone).*(cause|causes).*(cancer|brain tumor|brain tumour)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Current scientific evidence does not establish a causal link between cell phone use and cancer.',
            'WHO, ICNIRP, National Cancer Institute',
            ['Cell phones emit non-ionizing radiation, not DNA-damaging radiation', 'Large studies found no consistent link to brain tumors', 'WHO classifies RF as "possibly carcinogenic" (same as pickled vegetables)']
        ),
        (
            r'(wifi|wireless|router|bluetooth).*(cancer|harmful|dangerous|radiation)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: WiFi and Bluetooth use low-power non-ionizing radiation well within safety limits.',
            'WHO, FCC, scientific consensus',
            ['WiFi radiation is thousands of times below safety limits', 'Non-ionizing radiation cannot damage DNA', 'No established health effects from WiFi exposure']
        ),
        (
            r'ginger.*(cure|treat|heal).*(cancer|tumor|tumour|disease)',
            'false', 3, 'Likely Fake', 'Medium',
            'FALSE: While ginger has anti-inflammatory properties, it cannot cure cancer or serious diseases.',
            'Medical consensus, cancer research organizations',
            ['No clinical evidence ginger cures any disease', 'Anti-cancer claims are based on preliminary lab studies only', 'Relying on ginger instead of medical treatment is dangerous']
        ),
        (
            r'(alkaline|alkalize|ph balance).*(diet|water|cure|prevent).*(cancer|disease)',
            'false', 4, 'Likely Fake', 'High',
            'FALSE: The alkaline diet/water claim that you can change your blood pH to prevent disease is false.',
            'Medical consensus, cancer research',
            ['Body tightly regulates blood pH regardless of diet', 'Food cannot significantly change blood pH', 'Cancer cells create acidity; acidity does not create cancer']
        ),
        (
            r'(detox|cleanse|toxin flush|colon cleanse).*(cure|treatment|health)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: The body has its own detoxification systems (liver, kidneys) and most detox products are unnecessary.',
            'Medical consensus, NHS, poison control',
            ['Liver and kidneys effectively remove toxins without help', 'Most detox products have no scientific backing', 'Colon cleanses can be harmful and disrupt gut microbiome']
        ),
        (
            r'(essential oil|essential oils).*(cure|treat|heal).*(cancer|infection|serious)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Essential oils may provide symptom relief but do not cure serious diseases.',
            'Medical consensus, poison control',
            ['Essential oils are not FDA-approved for disease treatment', 'Some oils can cause allergic reactions or skin burns', 'Using oils instead of medical treatment is dangerous']
        ),
        (
            r'(carrots|carrot juice).*(cure|reverse|heal).*(cancer)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Claims that carrots or carrot juice can cure cancer are false and dangerous.',
            'Cancer Research UK, American Cancer Society',
            ['Carrots contain beneficial nutrients but no cancer cure', 'No clinical evidence supports cancer cure claims', 'Relying on diet alone instead of treatment is dangerous']
        ),
        (
            r'(sunscreen|sun block).*(cause|causes).*(cancer|harmful|dangerous|toxic)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Sunscreen prevents skin cancer and is safe for regular use.',
            'FDA, American Academy of Dermatology, Cancer Council',
            ['Sunscreen prevents UV damage that causes skin cancer', 'Ingredients are FDA-approved and tested for safety', 'Benefits of sun protection far outweigh any theoretical risks']
        ),
        (
            r'(cbd|cannabis|marijuana|weed|pot).*(cure|cures).*(cancer)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: While CBD has medical uses for pain and seizure disorders, it is not proven as a cancer cure.',
            'FDA, National Cancer Institute, clinical research',
            ['FDA has approved CBD for seizure disorders, not cancer', 'Some cannabinoids show anti-tumor effects in lab studies but not clinical trials', 'No cannabis-based cancer cures have been approved']
        ),
        (
            r'(homeschool|homeschooling).*(lower|worse|bad).*(education|social|outcome)',
            'mostly false', 1, 'Misleading', 'Low',
            'MISLEADING: Homeschooling outcomes vary widely based on approach and resources.',
            'Academic research, NHERI',
            ['Homeschool students often score above average on standardized tests', 'Social outcomes depend on community involvement', 'Quality varies widely between different homeschooling approaches']
        ),
        (
            r'(social media|instagram|tiktok|facebook|twitter).*(cause|causes).*(depression|anxiety|mental health)',
            'mostly true', 1, 'Partially Accurate', 'Medium',
            'PARTIALLY TRUE: Research shows correlations between heavy social media use and mental health issues, though causation is complex.',
            'Academic research, APA, Surgeon General',
            ['Correlational studies show links to anxiety and depression', 'Effects vary significantly by age and usage patterns', 'Causation remains debated; multiple factors involved']
        ),
        (
            r'(video game|gaming|violent game).*(cause|causes).*(violence|aggression|shooting)',
            'mostly false', 2, 'Misleading', 'High',
            'MOSTLY FALSE: Research does not support that video games cause real-world violence.',
            'APA, Supreme Court, multiple meta-analyses',
            ['Meta-analyses find no causal link to serious violence', 'Violent crime has declined as gaming has become more popular', 'APA statement acknowledges lack of evidence for causation']
        ),
        (
            r'(breakfast|skip breakfast).*(cause|causes|lead to).*(obesity|weight gain|fat)',
            'mostly false', 1, 'Misleading', 'Medium',
            'MOSTLY FALSE: Research on breakfast and weight is mixed; skipping breakfast does not directly cause obesity.',
            'Academic research, NIH, nutrition studies',
            ['Randomized trials show no clear effect on weight', 'Calorie balance, not meal timing, determines weight change', 'Some studies suggest intermittent fasting may have benefits']
        ),
        (
            r'(cracking|pop|crack).*(knuckles|joints|fingers).*(arthritis|joint damage)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Cracking knuckles does not cause arthritis.',
            'Medical research, peer-reviewed studies',
            ['Multiple studies find no link between knuckle cracking and arthritis', 'Sound comes from gas bubbles in joint fluid', 'One doctor won Ig Nobel Prize for 60-year self-experiment']
        ),
        (
            r'(swallow|chew).*(gum).*(stomach|digest|seven years|7 years)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Swallowing gum does not stay in your stomach for 7 years.',
            'Medical consensus, gastroenterology',
            ['Gum passes through the digestive system normally', 'Body cannot digest gum base but it passes within days', 'No documented cases of gum staying for 7 years']
        ),
        (
            r'(we only use|we use only).*10%.*brain',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: The claim that humans only use 10% of their brain is a myth.',
            'Neuroscience, brain imaging studies',
            ['Brain scans show activity throughout the brain during daily tasks', 'Brain damage to any area causes specific deficits', 'Evolution would not support a 90% useless organ']
        ),
        (
            r'(shave|shaving|hair cut|trim).*(grow|grows).*(thicker|darker|faster|coarser)',
            'false', 3, 'Likely Fake', 'High',
            'FALSE: Shaving does not make hair grow back thicker, darker, or faster.',
            'Dermatology research, clinical studies',
            ['Shaving cuts hair at blunt angle, creating illusion of thickness', 'Hair growth rate and color are determined by genetics and hormones', 'Multiple clinical studies confirm no effect on regrowth']
        ),
        (
            r'(cold weather|cold air|cold temperature|being cold).*(cause|causes).*(cold|flu|sick|illness)',
            'mostly false', 2, 'Misleading', 'Medium',
            'MOSTLY FALSE: Cold weather does not directly cause illness, though it may contribute to conditions for virus transmission.',
            'Medical consensus, NIH, CDC',
            ['Colds and flu are caused by viruses, not temperature', 'People gather indoors more in cold weather, increasing transmission', 'Cold air may slightly impair immune response but does not directly cause illness']
        ),
        (
            r'(vitamin c|vitamin c megadose|high dose vitamin c).*(cure|prevent).*(cold|flu|common cold)',
            'mostly false', 1, 'Misleading', 'Medium',
            'MOSTLY FALSE: Vitamin C does not prevent colds but may slightly shorten duration.',
            'Cochrane Review, NIH, multiple clinical trials',
            ['Large trials show no prevention effect for general population', 'Slight reduction in cold duration (8% in adults)', 'Megadoses may cause digestive upset and kidney stones']
        ),
        (
            r'(antibiotic|antibiotics).*(cure|treat|kill).*(virus|viral|cold|flu)',
            'false', 5, 'Likely Fake', 'High',
            'FALSE: Antibiotics kill bacteria, not viruses, and are ineffective against colds and flu.',
            'CDC, WHO, medical consensus',
            ['Antibiotics target bacterial cell walls and processes', 'Viruses have different structure and replication mechanism', 'Misuse of antibiotics contributes to antimicrobial resistance']
        ),
        (
            r'(fat.?free|low.?fat|nonfat).*(healthy|better|good for you)',
            'mostly false', 1, 'Misleading', 'Medium',
            'MISLEADING: Fat-free does not automatically mean healthy; many products add sugar to compensate for flavor.',
            'Nutrition research, Harvard School of Public Health',
            ['Fat-free products often contain added sugars', 'Healthy fats (avocado, nuts, olive oil) are beneficial', 'Total calorie and nutrient density matter more than fat content']
        ),
        (
            r'(green tea|matcha).*(cure|cures|prevents|fights).*(cancer)',
            'mostly false', 1, 'Misleading', 'Medium',
            'MISLEADING: Green tea contains antioxidants but is not proven to prevent or cure cancer.',
            'National Cancer Institute, clinical research',
            ['Lab studies show antioxidant properties', 'Epidemiological studies show mixed results in humans', 'No evidence green tea can treat existing cancer']
        ),
    ]

    def __init__(self):
        """Compile regex patterns for efficiency."""
        self._compiled_patterns = []
        for pattern_data in self.KNOWN_PATTERNS:
            pattern = pattern_data[0]
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._compiled_patterns.append((compiled,) + pattern_data[1:])
            except re.error as e:
                print(f"Warning: Failed to compile pattern '{pattern}': {e}")

    def check_claim(self, claim: str) -> Optional[MisinformationMatch]:
        """
        Check if a claim matches known misinformation patterns.
        """
        if not claim:
            return None

        claim_lower = claim.lower()

        for compiled_pattern in self._compiled_patterns:
            pattern = compiled_pattern[0]
            if pattern.search(claim_lower):
                return MisinformationMatch(
                    claim_type=compiled_pattern[1],
                    score=compiled_pattern[2],
                    classification=compiled_pattern[3],
                    confidence=compiled_pattern[4],
                    verdict=compiled_pattern[5],
                    source_note=compiled_pattern[6],
                    evidence=compiled_pattern[7]
                )

        return None

    def get_heuristic_verdict(self, claim: str) -> Optional[Dict]:
        """
        Get a complete heuristic verdict for a claim.
        """
        match = self.check_claim(claim)

        if match:
            return {
                'matched': True,
                'claim_type': match.claim_type,
                'score': match.score,
                'classification': match.classification,
                'confidence': match.confidence,
                'verdict': match.verdict,
                'source_note': match.source_note,
                'evidence': match.evidence,
                'is_heuristic': True,
                'api_used': False
            }

        return None


_heuristics_instance = None


def get_misinformation_heuristics() -> MisinformationHeuristics:
    """Get the global MisinformationHeuristics instance."""
    global _heuristics_instance
    if _heuristics_instance is None:
        _heuristics_instance = MisinformationHeuristics()
    return _heuristics_instance