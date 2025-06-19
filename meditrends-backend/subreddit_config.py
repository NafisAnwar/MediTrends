"""
Comprehensive subreddit configuration for MediTrends
Organized by categories with priority levels for intelligent search
"""

# Massively expanded subreddit coverage for comprehensive health search
SUBREDDIT_CATEGORIES = {
    
    # HIGHEST PRIORITY - Core Medical Communities
    'medical_primary': {
        'subreddits': [
            'AskDocs', 'medical_advice', 'Health', 'HealthAnxiety', 'medical',
            'DiagnoseMe', 'AskMedical', 'MedicalAdvice', 'medical_questions',
            'medicine', 'healthcare', 'AskHealthcare', 'medical_school',
            'nursing', 'pharmacy', 'AskPharmacists', 'pharmacology'
        ],
        'priority': 10,
        'description': 'Primary medical advice and professional communities'
    },
    
    # HIGH PRIORITY - Chronic Conditions & Specific Health Issues
    'chronic_conditions': {
        'subreddits': [
            'diabetes', 'diabetes_t1', 'diabetes_t2', 'Hypothyroidism', 'Hyperthyroidism',
            'PCOS', 'Celiac', 'IBD', 'IBS', 'CrohnsDisease', 'UlcerativeColitis',
            'Gastroparesis', 'Epilepsy', 'MultipleSclerosis', 'lupus', 'rheumatoid',
            'Psoriasis', 'eczema', 'Allergies', 'asthma', 'COPD', 'Hashimotos',
            'thyroid', 'endometriosis', 'adenomyosis', 'fibroids', 'Fibromyalgia',
            'ChronicIllness', 'autoimmune', 'chronicpain', 'migraine', 'Migraines'
        ],
        'priority': 9,
        'description': 'Chronic conditions and autoimmune disorders'
    },
    
    # HIGH PRIORITY - Mental Health (Expanded)
    'mental_health': {
        'subreddits': [
            'mentalhealth', 'depression', 'Anxiety', 'bipolar', 'ADHD',
            'autism', 'OCD', 'PTSD', 'socialanxiety', 'therapy', 'BetterMentality',
            'getting_over_it', 'decidingtobebetter', 'selfimprovement', 'BPD',
            'schizophrenia', 'eating_disorders', 'addiction', 'stopdrinking',
            'leaves', 'getmotivated', 'suicidewatch', 'depression_help',
            'BipolarReddit', 'AdultChildren', 'CPTSD', 'raisedbynarcissists',
            'emotionalabuse', 'MentalHealthSupport', 'panicattack', 'Agoraphobia'
        ],
        'priority': 8,
        'description': 'Mental health, therapy, and psychological support'
    },
    
    # HIGH PRIORITY - Pain Management & Physical Issues
    'pain_management': {
        'subreddits': [
            'ChronicPain', 'backpain', 'neckpain', 'migraine', 'Migraines',
            'headaches', 'Fibromyalgia', 'sciatica', 'scoliosis', 'spinalfusion',
            'herniateddiscs', 'DDD', 'stenosis', 'PainManagement', 'nerve_pain',
            'TMJ', 'shoulder_pain', 'knee_pain', 'hip_pain', 'joint_pain',
            'carpaltunnel', 'RSI', 'physicaltherapy', 'Physiotherapy',
            'OccupationalTherapy', 'massagetherapy', 'Chiropractic'
        ],
        'priority': 8,
        'description': 'Pain management and musculoskeletal issues'
    },
    
    # MEDIUM-HIGH PRIORITY - Lifestyle & Wellness
    'lifestyle_wellness': {
        'subreddits': [
            'LifeProTips', 'YouShouldKnow', 'todayilearned', 'explainlikeimfive',
            'productivity', 'getmotivated', 'selfimprovement', 'decidingtobebetter',
            'ZeroWaste', 'BuyItForLife', 'frugal', 'minimalism', 'meditation',
            'mindfulness', 'sleep', 'insomnia', 'nutrition', 'HealthyFood',
            'intermittentfasting', 'loseit', 'fitness', 'bodyweightfitness',
            'yoga', 'running', 'cycling', 'Swimming', 'hiking'
        ],
        'priority': 6,
        'description': 'Lifestyle, wellness, and general health optimization'
    },
    
    # MEDIUM PRIORITY - Large General Communities (High Volume)
    'general_large': {
        'subreddits': [
            'AskReddit', 'NoStupidQuestions', 'TooAfraidToAsk', 'OutOfTheLoop',
            'casualconversation', 'self', 'offmychest', 'relationship_advice',
            'AmItheAsshole', 'tifu', 'confessions', 'advice', 'needadvice',
            'Vent', 'UnethicalLifeProTips', 'LifeProTips', 'YouShouldKnow'
        ],
        'priority': 5,
        'description': 'Large general communities with diverse health discussions'
    },
    
    # MEDIUM PRIORITY - Work & Occupational Health
    'work_occupational': {
        'subreddits': [
            'jobs', 'careeradvice', 'WorkReform', 'antiwork', 'ITCareerQuestions',
            'cscareerquestions', 'sales', 'Entrepreneur', 'smallbusiness',
            'nursing', 'medicine', 'engineering', 'Teachers', 'LegalAdvice',
            'WorkplaceOrganizing', 'recruitinghell', 'careerguidance',
            'ITCareerQuestions', 'sysadmin', 'cscareerquestions'
        ],
        'priority': 4,
        'description': 'Work-related health issues and occupational concerns'
    },
    
    # MEDIUM PRIORITY - Demographics & Life Stages
    'demographics_lifestyle': {
        'subreddits': [
            'teenagers', 'college', 'StudentLoans', 'personalfinance',
            'AskOldPeople', 'RedditForGrownups', 'AskMenOver30', 'AskWomenOver30',
            'Parenting', 'Mommit', 'daddit', 'beyondthebump', 'pregnant',
            'BabyBumps', 'TryingForABaby', 'infertility', 'Menopause',
            'TwoXChromosomes', 'MensLib', 'AskMen', 'AskWomen'
        ],
        'priority': 4,
        'description': 'Age and gender-specific health discussions'
    },
    
    # MEDIUM PRIORITY - Hobbies That Cause Health Issues
    'hobby_health_related': {
        'subreddits': [
            'gaming', 'pcmasterrace', 'buildapc', 'MechanicalKeyboards',
            'Guitar', 'piano', 'singing', 'photography', 'crafts', 'sewing',
            'woodworking', 'metalworking', '3Dprinting', 'DMAcademy',
            'WeightTraining', 'powerlifting', 'bodybuilding', 'crossfit',
            'MartialArts', 'climbing', 'skiing', 'motorcycles', 'bicycling'
        ],
        'priority': 3,
        'description': 'Hobbies and activities that commonly cause health issues'
    },
    
    # MEDIUM PRIORITY - Specialized Health Areas
    'specialized_health': {
        'subreddits': [
            'SkincareAddiction', 'acne', 'Rosacea', 'dermatology', 'tretinoin',
            'SleepApnea', 'Narcolepsy', 'sleep_disorders', 'ChronicFatigue',
            'heartdisease', 'hypertension', 'cardiology', 'bloodpressure',
            'WomensHealth', 'MensHealth', 'testosterone', 'birthcontrol',
            'malegrooming', 'bald', 'HairLoss', 'tressless'
        ],
        'priority': 3,
        'description': 'Specialized health areas and body systems'
    },
    
    # LOWER PRIORITY - Tech & Modern Life
    'tech_modern': {
        'subreddits': [
            'technology', 'privacy', 'cybersecurity', 'buildapc', 'techsupport',
            'androidapps', 'iphone', 'gadgets', 'cordcutters', 'HomeNetworking',
            'dataisbeautiful', 'science', 'askscience', 'COVID19',
            'coronavirus', 'medicine', 'epidemiology'
        ],
        'priority': 2,
        'description': 'Technology-related health issues and modern life impacts'
    },
    
    # LOWER PRIORITY - General Health Discussion
    'general_health': {
        'subreddits': [
            'coolguides', 'dataisbeautiful', 'science', 'askscience',
            'explainlikeimfive', 'todayilearned', 'interestingasfuck',
            'YouShouldKnow', 'LifeProTips', 'UnethicalLifeProTips'
        ],
        'priority': 2,
        'description': 'General health information and educational content'
    }
}

def get_all_subreddits():
    """Get all subreddits as a flat list"""
    all_subreddits = []
    for category_data in SUBREDDIT_CATEGORIES.values():
        all_subreddits.extend(category_data['subreddits'])
    return list(set(all_subreddits))  # Remove duplicates

def get_subreddits_by_priority(min_priority=1):
    """Get subreddits filtered by minimum priority level"""
    filtered_subreddits = []
    for category_data in SUBREDDIT_CATEGORIES.values():
        if category_data['priority'] >= min_priority:
            filtered_subreddits.extend(category_data['subreddits'])
    return list(set(filtered_subreddits))

def get_category_by_keywords(keywords):
    """Get relevant categories based on query keywords"""
    keyword_mapping = {
        # Medical terms
        'pain': ['pain_management', 'chronic_conditions'],
        'depression': ['mental_health'],
        'anxiety': ['mental_health'],
        'diabetes': ['chronic_conditions'],
        'work': ['work_occupational'],
        'computer': ['hobby_health_related', 'tech_modern'],
        'gaming': ['hobby_health_related'],
        'sleep': ['specialized_health', 'lifestyle_wellness'],
        'skin': ['specialized_health'],
        'heart': ['specialized_health', 'chronic_conditions'],
        'headache': ['pain_management', 'chronic_conditions'],
        'back': ['pain_management'],
        'neck': ['pain_management'],
        'pregnancy': ['demographics_lifestyle'],
        'teenager': ['demographics_lifestyle'],
        'elderly': ['demographics_lifestyle'],
        'fitness': ['lifestyle_wellness'],
        'diet': ['lifestyle_wellness'],
        'nutrition': ['lifestyle_wellness']
    }
    
    relevant_categories = set()
    query_lower = ' '.join(keywords).lower()
    
    for keyword, categories in keyword_mapping.items():
        if keyword in query_lower:
            relevant_categories.update(categories)
    
    return list(relevant_categories)

# Medical terms for enhanced search
MEDICAL_TERMS = {
    'symptoms': [
        'headache', 'pain', 'fatigue', 'nausea', 'dizziness', 'fever',
        'cough', 'shortness of breath', 'chest pain', 'abdominal pain',
        'back pain', 'joint pain', 'muscle pain', 'burning', 'tingling',
        'numbness', 'swelling', 'rash', 'itching', 'bleeding'
    ],
    'conditions': [
        'diabetes', 'hypertension', 'depression', 'anxiety', 'arthritis',
        'asthma', 'COPD', 'heart disease', 'stroke', 'cancer', 'lupus',
        'fibromyalgia', 'migraine', 'epilepsy', 'thyroid', 'PCOS'
    ],
    'medications': [
        'ibuprofen', 'acetaminophen', 'aspirin', 'prednisone', 'metformin',
        'lisinopril', 'atorvastatin', 'omeprazole', 'sertraline', 'lexapro',
        'adderall', 'synthroid', 'metoprolol', 'gabapentin', 'tramadol'
    ],
    'body_parts': [
        'head', 'neck', 'shoulder', 'arm', 'hand', 'chest', 'back',
        'abdomen', 'hip', 'leg', 'knee', 'foot', 'heart', 'lung',
        'stomach', 'liver', 'kidney', 'brain', 'spine', 'joint'
    ]
}

def get_medical_terms():
    """Get all medical terms as a flat list"""
    all_terms = []
    for category_terms in MEDICAL_TERMS.values():
        all_terms.extend(category_terms)
    return all_terms