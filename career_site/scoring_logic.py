import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug: Print all environment variables from .env
print("Loaded environment variables:")
# print(f"SPREADSHEET_ID: '{os.getenv('SPREADSHEET_ID')}'")
print(f"SENDER_EMAIL: '{os.getenv('SENDER_EMAIL')}'")
print(f"APP_PASSWORD: '{os.getenv('APP_PASSWORD')}'")
print(f"GOOGLESHEET_ID: '{os.getenv('GOOGLESHEET_ID')}'")

# Configuration
GOOGLESHEET_ID = "1lCuSSm8KsVHpe0fi-axTUuoUnw3zWhuncAuOM52eUbk"
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
EMAIL_SUBJECT = "Your Personality Test Results"

# Initialize Google Sheets API
def init_gsheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    
    try:
        print("Service account email:", creds.service_account_email)
        print("Trying to access spreadsheet with ID:", GOOGLESHEET_ID)
        
        # List all accessible spreadsheets
        available_sheets = list(client.openall())
        print("\nAvailable spreadsheets:")
        for sheet in available_sheets:
            print(f"- {sheet.title} (ID: {sheet.id})")
        
        # If the ID from .env is wrong but there is only one accessible spreadsheet, use that instead
        if not GOOGLESHEET_ID and len(available_sheets) == 1:
            print(f"\nNo spreadsheet ID provided in .env, using the only available spreadsheet: {available_sheets[0].title}")
            return available_sheets[0].sheet1
            
        # Check if the target spreadsheet is in the available sheets
        sheet_ids = [sheet.id for sheet in available_sheets]
        if GOOGLESHEET_ID not in sheet_ids:
            print(f"\nERROR: The spreadsheet ID '{GOOGLESHEET_ID}' from your .env file was not found in the list of accessible spreadsheets.")
            print("Please either:")
            print(f"1. Share the spreadsheet with your service account email ({creds.service_account_email})")
            print(f"2. Update your .env file with one of the available spreadsheet IDs listed above")
            
            # Ask if user wants to use an available spreadsheet instead
            if available_sheets:
                use_alternative = input("\nWould you like to use one of the available spreadsheets instead? (y/n): ")
                if use_alternative.lower() == 'y':
                    if len(available_sheets) == 1:
                        print(f"Using the only available spreadsheet: {available_sheets[0].title}")
                        return available_sheets[0].sheet1
                    else:
                        print("Available options:")
                        for i, sheet in enumerate(available_sheets):
                            print(f"{i+1}. {sheet.title}")
                        choice = int(input("Enter the number of the spreadsheet to use: ")) - 1
                        if 0 <= choice < len(available_sheets):
                            print(f"Using spreadsheet: {available_sheets[choice].title}")
                            return available_sheets[choice].sheet1
            
            raise Exception("Spreadsheet access error - see details above")
        
        # Test access to the target spreadsheet
        return client.open_by_key(GOOGLESHEET_ID).sheet1
    except Exception as e:
        if isinstance(e, gspread.exceptions.SpreadsheetNotFound):
            print("\nERROR: Spreadsheet not found!")
            print(f"The spreadsheet ID '{GOOGLESHEET_ID}' from your .env file cannot be accessed.")
            print(f"Please make sure you've shared the spreadsheet with: {creds.service_account_email}")
        else:
            print("\nERROR DETAILS:")
            print(f"Service account: {creds.service_account_email}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
        raise

def extract_responses(record):
    """Extract and map responses from the record dictionary"""
    # Debug record keys
    print("DEBUG: Available record keys:")
    for key in list(record.keys())[:10]:  # Show first 10 keys
        print(f"  - {key}")
    
    # Find keys that look like questions
    responses = []
    question_keys = []
    
    # Look for question keys with various formats
    for key in record.keys():
        # Try to extract question number from the key
        key_stripped = key.strip()  # Remove leading/trailing spaces
        
        # Check different question formats
        for pattern in [
            r'^(\d+)\.',  # "1. Question text"
            r'^Q(\d+)',   # "Q1"
            r'^Question (\d+)',  # "Question 1"
            r'^\s*(\d+)\.',  # " 1. Question text" (with leading spaces)
            r'^\s*Q(\d+)',  # " Q1" (with leading spaces)
            r'^\s*Question (\d+)'  # " Question 1" (with leading spaces)
        ]:
            import re
            match = re.match(pattern, key_stripped)
            if match:
                try:
                    question_num = int(match.group(1))
                    if 1 <= question_num <= 50:
                        question_keys.append((question_num, key))
                        break
                except (ValueError, IndexError):
                    pass
    
    if question_keys:
        print(f"Found {len(question_keys)} potential question keys")
        # Sort by question number
        question_keys.sort()
        
        # Debug first few found questions
        for i, (num, key) in enumerate(question_keys[:5]):
            print(f"Question {num}: '{key}' = '{record.get(key, 'N/A')}'")
        
        # Map each question to its response
        question_map = {num: key for num, key in question_keys}
        
        # Extract responses in order
        for i in range(1, 51):
            if i in question_map:
                key = question_map[i]
                try:
                    # Try to extract numeric value from response
                    value_str = str(record.get(key, '')).strip()
                    
                    # Map text responses to numeric values
                    if 'strongly disagree' in value_str.lower():
                        value = 1
                    elif 'disagree' in value_str.lower() and 'slightly' not in value_str.lower():
                        value = 2
                    elif 'slightly disagree' in value_str.lower():
                        value = 2
                    elif 'neutral' in value_str.lower():
                        value = 3
                    elif 'slightly agree' in value_str.lower():
                        value = 4
                    elif 'agree' in value_str.lower() and 'strongly' not in value_str.lower():
                        value = 5
                    elif 'strongly agree' in value_str.lower():
                        value = 5
                    else:
                        # Try to parse a numeric value if text parsing failed
                        try:
                            if ' - ' in value_str:
                                value_str = value_str.split(' - ')[0]
                            value = int(value_str)
                        except:
                            value = 3  # Default to neutral
                            print(f"Warning: Could not parse response for question {i}: '{value_str}', defaulting to 3")
                            
                    responses.append(value)
                    print(f"Found response for question {i}: {value}")
                except (ValueError, TypeError):
                    responses.append(3)  # Default to neutral
                    print(f"Warning: Invalid response for question {i}: '{record.get(key, '')}', defaulting to 3")
            else:
                responses.append(3)  # Default to neutral
                print(f"Warning: Question {i} not found in record, defaulting to 3")
    else:
        # No question keys found
        print("WARNING: Could not detect question columns. Using default neutral values (3) for all responses.")
        responses = [3] * 50
    
    return responses

def calculate_scores(responses):
    # Each trait has 10 questions associated with it
    # Some questions are reverse-scored (marked with negative signs below)
    
    raw_scores = {
        'E': 20 + responses[0] - responses[5] + responses[10] - responses[15] + 
             responses[20] - responses[25] + responses[30] - responses[35] + 
             responses[40] - responses[45],
        'A': 14 - responses[1] + responses[6] - responses[11] + responses[16] - 
             responses[21] + responses[26] - responses[31] + responses[36] + 
             responses[41] + responses[46],
        'C': 14 + responses[2] - responses[7] + responses[12] - responses[17] + 
             responses[22] - responses[27] + responses[32] - responses[37] + 
             responses[42] + responses[47],
        'N': 38 - responses[3] + responses[8] - responses[13] + responses[18] - 
             responses[23] - responses[28] - responses[33] - responses[38] - 
             responses[43] - responses[48],
        'O': 8 + responses[4] - responses[9] + responses[14] - responses[19] + 
             responses[24] - responses[29] + responses[34] + responses[39] + 
             responses[44] + responses[49]
    }
    
    # Convert raw scores to 0-40 scale (no normalization needed)
    # We'll work directly with these raw scores for simplicity
    print(f"Raw scores calculated: {raw_scores}")
    return raw_scores

def get_level(score, trait=None):
    """Get level based on raw score ranges for a given trait"""
    # Different traits have different score ranges
    if trait == 'E':
        if score < 15:
            return "Low"
        elif score < 25:
            return "Medium"
        else:
            return "High"
    elif trait == 'A':
        if score < 10:
            return "Low"
        elif score < 20:
            return "Medium"
        else:
            return "High"
    elif trait == 'C':
        if score < 10:
            return "Low"
        elif score < 20:
            return "Medium" 
        else:
            return "High"
    elif trait == 'N':
        if score < 15:
            return "Low"
        elif score < 25:
            return "Medium"
        else:
            return "High"
    elif trait == 'O':
        if score < 10:
            return "Low"
        elif score < 20:
            return "Medium"
        else:
            return "High"
    else:
        # Generic ranges if trait is unknown
        if score < 15:
            return "Low"
        elif score < 25:
            return "Medium"
        else:
            return "High"

# Get trait names
def get_trait_name(trait_code):
    names = {
        'O': 'Openness',
        'C': 'Conscientiousness',
        'E': 'Extraversion',
        'A': 'Agreeableness',
        'N': 'Neuroticism'
    }
    return names.get(trait_code, trait_code)

def generate_personality_profile(scores, grade):
    # Create a profile key based on Low/Medium/High for each trait
    # In generate_personality_profile function:
    levels = {trait: get_level(score, trait) for trait, score in scores.items()}
    
    # Define trait descriptions based on levels
    trait_descriptions = {
        'O': {
            'High': "Highly creative, imaginative, and open to new experiences",
            'Medium': "Balanced between traditional and new ideas",
            'Low': "Prefers conventional approaches and concrete facts"
        },
        'C': {
            'High': "Highly organized, disciplined, and goal-oriented",
            'Medium': "Moderately organized but flexible",
            'Low': "Prefers flexibility and spontaneity over structure"
        },
        'E': {
            'High': "Outgoing, energetic, and social",
            'Medium': "Moderately social, comfortable in groups and alone",
            'Low': "Reserved, prefers solitary activities"
        },
        'A': {
            'High': "Cooperative, compassionate, and considerate",
            'Medium': "Balances cooperation with assertiveness",
            'Low': "Direct, competitive, and focused on own goals"
        },
        'N': {
            'High': "Emotionally sensitive and responsive to stress",
            'Medium': "Experiences normal emotional ups and downs",
            'Low': "Emotionally stable and resilient to stress"
        }
    }
    
    # Grade-specific recommendations
    if grade == "10":
        # 10th grade stream recommendations for 11th standard subjects
        recommendations = {
            'O': {
                'High': "11th Standard Groups: Science with Computer Applications, Humanities with Literature and Fine Arts, Design Studies",
                'Medium': "11th Standard Groups: Commerce with Economics, Science with Biology, Arts with Psychology",
                'Low': "11th Standard Groups: Pure Science (PCM), Commerce with Accountancy, Computer Applications"
            },
            'C': {
                'High': "11th Standard Groups: Science with Mathematics and Physics, Commerce with Accountancy, Computer Science",
                'Medium': "11th Standard Groups: Science with Biology, Commerce with Business Studies, Economics",
                'Low': "11th Standard Groups: Humanities with Psychology, Fine Arts, Creative subjects"
            },
            'E': {
                'High': "11th Standard Groups: Commerce with Business Studies, Humanities with Psychology and Sociology, Mass Media",
                'Medium': "11th Standard Groups: Science with Biology, Commerce with Marketing, Arts with Communication",
                'Low': "11th Standard Groups: Pure Science (PCM), Computer Science and Mathematics, Physics with Electronics"
            },
            'A': {
                'High': "11th Standard Groups: Humanities with Psychology and Sociology, Science with Biology, Arts with Literature",
                'Medium': "11th Standard Groups: Commerce with Business Studies, Science with Environmental Science, Home Science",
                'Low': "11th Standard Groups: Pure Science (PCM), Computer Science with Mathematics, Commerce with Accounting"
            },
            'N': {
                'High': "11th Standard Groups: Humanities with Fine Arts and Creative Writing, Commerce with Business Studies",
                'Medium': "11th Standard Groups: Science with Biology, Commerce with Economics, Arts with Design",
                'Low': "11th Standard Groups: Pure Science (PCM), Commerce with Mathematics and Accounting, Computer Science"
            }
        }
        
        # Define profile for 10th grade
        if levels['O'] == 'High' and levels['C'] == 'High':
            profile = {
                'primary': "Science (PCM) with Research Focus",
                'secondary': "Computer Science with Creative Programming",
                'confidence': "85%",
                'description': "Your combination of high Openness and Conscientiousness suggests you would excel in structured creative fields. For 11th grade, consider Science (PCM) or Computer Science streams where you can apply both creativity and analytical thinking."
            }
        elif levels['C'] == 'High' and levels['E'] == 'Low':
            profile = {
                'primary': "Pure Science or Computer Science",
                'secondary': "Mathematics with Physics",
                'confidence': "80%",
                'description': "Your disciplined and focused nature makes you well-suited for technical streams where attention to detail is important. For 11th grade, consider Pure Science or Computer Science where you can work independently on complex problems."
            }
        elif levels['E'] == 'High' and levels['A'] == 'High':
            profile = {
                'primary': "Commerce with Business Studies",
                'secondary': "Humanities with Psychology/Sociology",
                'confidence': "85%",
                'description': "Your social and cooperative nature suggests you would do well in people-oriented streams. For 11th grade, consider Commerce with Business Studies or Humanities with focus on social sciences."
            }
        else:
            # Generic profile based on most prominent traits
            primary_traits = [t for t, l in levels.items() if l == 'High']
            if primary_traits:
                traits_str = ', '.join([get_trait_name(t) for t in primary_traits])
                profile = {
                    'primary': "Personalized Stream Selection",
                    'secondary': "Multiple Subject Exploration",
                    'confidence': "75%",
                    'description': f"Your primary strengths are in {traits_str}. For 11th grade, consider streams that align with these traits based on the individual recommendations below."
                }
            else:
                profile = {
                    'primary': "Mixed Stream Approach",
                    'secondary': "Balanced Subject Selection",
                    'confidence': "70%",
                    'description': "Your balanced profile suggests you could succeed in multiple streams. For 11th grade, consider your academic strengths and interests when choosing your stream."
                }
    else:
        # 12th grade college major recommendations
        recommendations = {
            'O': {
                'High': "College Majors: Psychology, Fine Arts, Research fields",
                'Medium': "College Majors: Business, Architecture, Data Science",
                'Low': "College Majors: Accounting, Engineering, IT fields"
            },
            'C': {
                'High': "College Majors: Medicine, Engineering, Finance",
                'Medium': "College Majors: Business, Law, Healthcare",
                'Low': "College Majors: Creative fields, Flexible careers"
            },
            'E': {
                'High': "College Majors: Marketing, HR, Mass Communication",
                'Medium': "College Majors: Most people-oriented careers",
                'Low': "College Majors: Technical or research-oriented fields"
            },
            'A': {
                'High': "College Majors: Psychology, Counseling, Social Work",
                'Medium': "College Majors: Healthcare, Teaching, Business",
                'Low': "College Majors: Analytical or technical fields"
            },
            'N': {
                'High': "College Majors: Creative fields, Supportive roles",
                'Medium': "College Majors: Most careers with balanced stress",
                'Low': "College Majors: High-pressure careers like Medicine"
            }
        }
        
        # Define profile for 12th grade
        if levels['O'] == 'High' and levels['C'] == 'High':
            profile = {
                'primary': "Research-Oriented STEM Majors",
                'secondary': "Data Science, Biotechnology, Architecture",
                'confidence': "85%",
                'description': "Your combination of creativity and discipline makes you well-suited for fields requiring both innovation and structure. Consider majors in Research Sciences, Data Science, or Architecture that leverage your analytical and creative abilities."
            }
        elif levels['C'] == 'High' and levels['E'] == 'Low':
            profile = {
                'primary': "Technical and Analytical Fields",
                'secondary': "Engineering, Finance, Computer Science",
                'confidence': "80%",
                'description': "Your methodical and focused approach suggests technical fields would be good fits. Consider majors in Engineering, Computer Science, or Finance where attention to detail and independent work are valued."
            }
        elif levels['E'] == 'High' and levels['A'] == 'High':
            profile = {
                'primary': "People-Oriented Careers",
                'secondary': "HR, Marketing, Counseling, Healthcare",
                'confidence': "85%",
                'description': "Your people skills and empathy suggest careers involving human interaction would be rewarding. Consider majors in Human Resources, Marketing, Counseling, or Healthcare that leverage your interpersonal abilities."
            }
        else:
            # Generic profile based on most prominent traits
            primary_traits = [t for t, l in levels.items() if l == 'High']
            if primary_traits:
                traits_str = ', '.join([get_trait_name(t) for t in primary_traits])
                profile = {
                    'primary': "Personalized Major Selection",
                    'secondary': "Interdisciplinary Programs",
                    'confidence': "75%",
                    'description': f"Your primary strengths are in {traits_str}. Consider college majors that align with these traits based on the individual recommendations below."
                }
            else:
                profile = {
                    'primary': "Flexible Degree Programs",
                    'secondary': "Liberal Arts or General Studies",
                    'confidence': "70%",
                    'description': "Your balanced profile suggests you could succeed in many fields. Consider your academic strengths and interests when choosing your college major."
                }
    
    # Create trait_info structure as expected by create_pdf_report
    trait_info = {}
    for trait in ['O', 'C', 'E', 'A', 'N']:
        level = levels[trait]
        trait_info[trait] = {
            'level': level,
            'description': trait_descriptions[trait][level],
            'recommendations': recommendations[trait][level]
        }
    
    # Format the results in the structure expected by create_pdf_report
    result = {
        'profile': profile,
        'trait_info': trait_info,
        'levels': levels
    }
    
    return result

def get_career_suggestions(scores, grade):
    """Generate a dynamic summary based on the scores and grade"""
    # Convert to levels first
    levels = {trait: get_level(score, trait) for trait, score in scores.items()}
    
    o = levels['O']
    c = levels['C']
    e = levels['E']
    a = levels['A']
    n = levels['N']
    
    # Get top two traits
    trait_scores = list(scores.items())
    trait_scores.sort(key=lambda x: x[1], reverse=True)
    top_traits = trait_scores[:2]
    
    if grade == "10":
        # 10th grade summaries focused on 11th standard subject groups
        if o == 'High' and c == 'High':
            return ("With your creativity and strong organizational skills, you would excel in Science stream with Computer Applications or Design studies for 11th standard. This combination allows you to use your creative abilities within structured environments. You could also consider Humanities with Literature and Psychology if you prefer more creative expression.")
        elif c == 'High' and e == 'Low':
            return ("Your conscientious nature and preference for independent work suggest Pure Science (PCM) or Computer Science would be excellent subject groups for 11th standard. These streams reward your attention to detail, disciplined approach, and ability to work on complex problems without requiring extensive social interaction.")
        elif e == 'High' and a == 'High':
            return ("With your outgoing and cooperative nature, you would thrive in Commerce with Business Studies or Humanities with Psychology and Sociology in 11th standard. These subject groups involve group discussions, presentations, and understanding people - all areas where your social skills and helpfulness will be valuable assets.")
        else:
            # Generic recommendation based on top traits
            top_trait = top_traits[0][0]
            if top_trait == 'O':
                return ("For 11th standard, your creativity and openness to new ideas suggest you would enjoy Humanities with Literature and Fine Arts, or Science with Design studies. These subject groups will nurture your imagination and give you opportunities to explore diverse perspectives and creative problem-solving.")
            elif top_trait == 'C':
                return ("For 11th standard, your conscientiousness makes you well-suited for Pure Science (PCM) or Commerce with Accountancy and Mathematics. These subject groups reward organization, persistence, and attention to detail - qualities that come naturally to you. You'll excel in structured environments with clear objectives.")
            elif top_trait == 'E':
                return ("For 11th standard, your extraverted nature suggests you would thrive in subject groups with interactive learning like Commerce with Business Studies or Humanities with Mass Communication. These streams involve discussions, presentations, and group projects that will engage your social energy and communication skills.")
            elif top_trait == 'A':
                return ("For 11th standard, your agreeable nature suggests subject groups focused on understanding people and helping others - like Humanities with Psychology and Sociology, or Science with Biology. These subjects align with your cooperative nature and will develop your natural empathy and people skills.")
            elif top_trait == 'N':
                return ("For 11th standard, channel your emotional sensitivity into expressive subjects like Humanities with Literature and Creative Writing, or Arts with Fine Arts. These subjects provide opportunities for emotional expression while developing academic skills that align with your natural emotional awareness.")
            else:
                return ("For 11th standard, with your balanced personality profile, consider Commerce with Business Studies and Economics or Science with Computer Applications. These versatile subject groups provide a solid foundation while keeping your future options open.")
    else:
        # 12th grade summaries for college majors (keep your existing code)
        if o == 'High' and c == 'High':
            return ("Your combination of creativity and discipline makes you well-suited for research-oriented fields. Consider college majors like Biotechnology, Data Science, Architecture, or Product Design that require both innovative thinking and structured approaches. Your ability to think outside the box while maintaining organization will be valuable in these fields.")
        elif c == 'High' and e == 'Low':
            return ("Your methodical, focused approach and preference for independent work make you well-suited for technical and analytical fields. Consider college majors in Engineering, Computer Science, Finance, or Actuarial Science. These fields reward your attention to detail and ability to work persistently on complex problems.")
        elif e == 'High' and a == 'High':
            return ("Your people skills and cooperative nature make you perfect for careers centered around human interaction. Consider college majors in Human Resources, Marketing, Counseling, Education, or Healthcare Administration. These fields leverage your social abilities and natural empathy, offering fulfilling opportunities to help others.")
        else:
            # Generic college major recommendation based on top traits
            top_trait = top_traits[0][0]
            if top_trait == 'O':
                return ("Your creativity and openness to new ideas suggest you would thrive in innovative fields. Consider college majors in Design, Architecture, Creative Writing, Liberal Arts, or Research Sciences that value original thinking and exploration of new concepts. These fields will allow you to express your creativity while developing specialized knowledge.")
            elif top_trait == 'C':
                return ("Your conscientious nature makes you well-suited for structured and demanding fields. Consider college majors in Engineering, Medicine, Law, Finance, or Business Administration. These disciplines reward your organization, attention to detail, and ability to work systematically toward long-term goals.")
            elif top_trait == 'E':
                return ("Your extraverted nature suggests you would excel in fields with substantial human interaction. Consider college majors in Marketing, Public Relations, Hospitality Management, Sales, or Politics. These areas leverage your social energy, verbal communication skills, and ability to build networks and relationships.")
            elif top_trait == 'A':
                return ("Your agreeable nature suggests you would find fulfillment in helping professions. Consider college majors in Nursing, Social Work, Counseling, Psychology, Teaching, or Healthcare. These fields value your empathy, cooperation, and desire to positively impact others' lives.")
            elif top_trait == 'N':
                return ("Your emotional sensitivity can be channeled effectively in fields that value emotional expression and understanding. Consider college majors in Fine Arts, Creative Writing, Psychology, Counseling, or Sociology, where emotional intelligence and self-awareness are considered strengths rather than liabilities.")
            else:
                return ("With your balanced personality profile, you would adapt well to various fields. Consider versatile college majors like Business Administration, Communications, Information Technology, or Interdisciplinary Studies that provide broad skill sets and multiple career paths. Your adaptability will be an asset in these fields.")
# Create PDF report
def create_pdf_report(name, grade, scores, profile_results, test_date=None):
    from fpdf import FPDF
    
    pdf = FPDF()
    pdf.add_page()
    
    # Set the test date to current date if not provided
    if not test_date:
        test_date = datetime.now().strftime("%B %d, %Y")
    
    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Personality Assessment Results', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Date: {test_date}', 0, 1, 'C')
    pdf.ln(5)
    
    # Student information
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Student Information', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Name: {name}', 0, 1)
    pdf.cell(0, 10, f'Grade: {grade}', 0, 1)
    pdf.ln(5)
    
    # Big Five Scores
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Big Five Personality Traits Assessment', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    # Add scores table
    trait_names = {
        'O': 'Openness to Experience',
        'C': 'Conscientiousness',
        'E': 'Extraversion',
        'A': 'Agreeableness',
        'N': 'Neuroticism'
    }
    
    # Define raw score ranges for scaling
    max_scores = {
        'O': 40,
        'C': 40, 
        'E': 40,
        'A': 40,
        'N': 40
    }
    
    pdf.ln(2)
    for trait in ['O', 'C', 'E', 'A', 'N']:
        trait_name = trait_names[trait]
        raw_score = scores[trait]
        level = profile_results['levels'][trait]
        
        # Calculate percentage score (0-100) for display
        max_score = max_scores[trait]
        percentage_score = int((raw_score / max_score) * 100)
        
        # Trait name and score
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(80, 10, f"{trait_name}: ", 0, 0)
        pdf.set_font('Arial', '', 12)
        pdf.cell(30, 10, f"{raw_score}/{max_score}", 0, 0)  # Show raw score out of max
        pdf.cell(30, 10, f"({level})", 0, 1)
        
        # Description
        pdf.set_font('Arial', 'I', 10)
        description = profile_results['trait_info'][trait]['description']
        
        # Handle multi-line descriptions
        pdf.multi_cell(0, 5, description)
        pdf.ln(3)
        
    # Stream/Major recommendations based on this trait
    pdf.set_font('Arial', '', 10)
    if grade == "10":
        pdf.cell(0, 5, f"Recommended 11th standard subject groups:", 0, 1)
    else:
        pdf.cell(0, 5, f"Recommended college majors:", 0, 1)
        
    recommendations = profile_results['trait_info'][trait]['recommendations']
    pdf.multi_cell(0, 5, recommendations)
    pdf.ln(5)
    
    # Profile Match
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    if grade == "10":
        pdf.cell(0, 10, '11th Standard Subject Group Recommendation', 0, 1)
    else:
        pdf.cell(0, 10, 'College Major Recommendation', 0, 1)
    
    # Profile match details
    profile = profile_results['profile']
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Primary Recommendation: {profile['primary']}", 0, 1)
    pdf.cell(0, 8, f"Secondary Recommendation: {profile['secondary']}", 0, 1)
    pdf.cell(0, 8, f"Confidence Level: {profile['confidence']}", 0, 1)
    
    # Top alternative matches (if available)
    if 'all_matches' in profile_results and len(profile_results['all_matches']) > 1:
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "Alternative Paths to Consider:", 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for i, match in enumerate(profile_results['all_matches'][1:3]):  # Show 2nd and 3rd matches
            alt_profile = match['profile']
            pdf.cell(0, 6, f"{i+1}. {alt_profile['primary']} ({match['percentage']}% match)", 0, 1)
    
    # Profile description
    pdf.set_font('Arial', '', 11)
    pdf.ln(5)
    pdf.multi_cell(0, 5, profile['description'])
    
    # Career suggestions
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Potential Career Paths', 0, 1)
    pdf.set_font('Arial', '', 11)
    career_suggestions = get_career_suggestions(scores, grade)
    pdf.multi_cell(0, 5, career_suggestions)
    
    # Additional information
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 10)
    if grade == "10":
        pdf.multi_cell(0, 5, "This assessment is designed to help guide educational stream choices as you enter Grade 11. It is based on your personality traits and potential academic interests. The recommendations should be considered alongside your academic performance, personal interests, and future goals.")
    else:  # grade 12
        pdf.multi_cell(0, 5, "This assessment is designed to help guide college major and career path choices as you prepare for higher education. It is based on your personality traits and potential career interests. The recommendations should be considered alongside your academic strengths, personal interests, and future aspirations.")
    
    # Disclaimer
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 8)
    pdf.multi_cell(0, 4, "Disclaimer: This assessment is meant to be a guiding tool and not a definitive career decision maker. Always consider consulting with career counselors, teachers, and parents before making academic or career decisions.")
    
    return pdf

# Send email with PDF report
def send_email_with_report(receiver_email, student_name, pdf_bytes, test_date=None, filename=None):
    if not test_date:
        test_date = datetime.now().strftime("%B %d, %Y")
    
    # Use provided filename or generate a default one
    if not filename:
        filename = f"{student_name} - Personality Assessment.pdf"
        
    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = EMAIL_SUBJECT
    
    # Email body
    body = f"""
Dear Parent/Guardian of {student_name},

We are pleased to share the results of {student_name}'s personality assessment conducted on {test_date}. The attached PDF report provides insights into their personality traits and potential academic/career paths that align with their natural tendencies.

This assessment is designed to help guide educational and career choices based on personality traits. The recommendations should be considered alongside academic performance, personal interests, and future goals.

Please review the attached report, and feel free to schedule a meeting with our counseling department if you would like to discuss these results further.

Best regards,
Career Counseling Department
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF with custom filename
    attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
    attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(attachment)
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Main function to process record and generate report

# Update the process_record function to explicitly extract the grade

def process_record(record):
    """
    Process a single record from the Google Sheet.
    This is the main entry point called by the monitor.
    """
    try:
        print("Processing form submission record:")
        # Print available keys for debugging
        print(f"DEBUG: Available record keys:")
        for key in list(record.keys())[:10]:  # Show first 10 keys
            print(f"  - {key}")
        
        # Extract key information
        name = record.get('Name', '')
        
        # Get email from various possible field names
        email = None
        email_keys = ['email', 'email address', 'email id', 'e-mail', 'mail']
        for key in record.keys():
            key_lower = key.lower().strip()
            if any(email_key in key_lower for email_key in email_keys):
                if record[key]:  # Check if the value is not empty
                    email = record[key]
                    print(f"Found email in field '{key}': {email}")
                    break
        
        # If still no email, try direct keys
        if not email:
            for direct_key in ['Email Address', 'Email', 'Email ID', 'email']:
                if direct_key in record and record[direct_key]:
                    email = record[direct_key]
                    print(f"Found email in direct field '{direct_key}': {email}")
                    break
        
        # Get grade - explicitly look for 10 or 12, default to 12 if not found
        grade = record.get('Grade', '')
        # Clean up the grade value
        if grade:
            # Extract just the numbers if there's text like "Grade 10" or "10th"
            import re
            grade_match = re.search(r'(\d+)', str(grade))
            if grade_match:
                grade = grade_match.group(1)
            
            # Validate that grade is either 10 or 12, default to 12 otherwise
            if grade not in ['10', '12']:
                print(f"Unrecognized grade: '{grade}', defaulting to 12")
                grade = '12'
        else:
            print("No grade specified, defaulting to 12")
            grade = '12'
        
        print(f"Processing record for {name}")
        print(f"Email found: '{email}'")
        print(f"Grade: {grade}")
        
        # Extract responses from the record
        responses = extract_responses(record)
        
        # Calculate Big Five scores
        scores = calculate_scores(responses)
        
        # Generate personality profile with the correct grade
        profile_results = generate_personality_profile(scores, grade)
        
        # Create PDF report with grade-specific recommendations
        pdf = create_pdf_report(name, grade, scores, profile_results)
        
        # Create directory for reports if it doesn't exist
        reports_dir = "generated_reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Create a timestamp string for unique filenames
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save PDF to file
        base_name = name.replace(' ', '_')
        local_filename = os.path.join(reports_dir, f"{base_name}_personality_assessment_{current_time}.pdf")
        pdf.output(local_filename)
        
        print(f"Generated report for {name} at {local_filename}")
        
        # Send email if email address is provided
        if email:
            # For email attachment, use a clean filename without timestamp
            email_filename = f"{name} - Personality Assessment Report.pdf"
            
            # We need to have the PDF in memory for email
            with open(local_filename, 'rb') as f:
                pdf_bytes = f.read()
            
            # Send email with the PDF attachment
            if send_email_with_report(email, name, pdf_bytes, None, email_filename):
                print(f"Email sent to {email} with attachment named '{email_filename}'")
            else:
                print(f"Failed to send email to {email}")
        else:
            print("No email address provided, skipping email")
        
        return True
    except Exception as e:
        print(f"ERROR processing record: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Main function to process the spreadsheet
def main():
    try:
        # Initialize Google Sheets
        sheet = init_gsheets()
        
        print("Accessing spreadsheet data...")
        try:
            # Get all values (not records) to handle the duplicate headers issue
            all_values = sheet.get_all_values()
            
            if not all_values or len(all_values) <= 1:  # Check if there's data and headers
                print("No data found in the spreadsheet.")
                return
                
            # Extract headers (first row)
            headers = all_values[0]
            print(f"Found {len(headers)} columns in the spreadsheet")
            
            # Create unique headers automatically
            unique_headers = []
            seen_headers = {}
            
            for h in headers:
                if h in seen_headers:
                    seen_headers[h] += 1
                    unique_headers.append(f"{h}_{seen_headers[h]}")
                else:
                    seen_headers[h] = 0
                    unique_headers.append(h)
            
            print(f"Created {len(unique_headers)} unique headers")
            
            # Create records with unique headers
            all_data = []
            for row in all_values[1:]:  # Skip the header row
                if len(row) < len(unique_headers):
                    # Pad the row if it's shorter than the headers
                    row = row + [''] * (len(unique_headers) - len(row))
                elif len(row) > len(unique_headers):
                    # Truncate if row is longer than headers
                    row = row[:len(unique_headers)]
                
                record = {unique_headers[i]: row[i] for i in range(len(unique_headers))}
                all_data.append(record)
                
            print(f"Found {len(all_data)} records in the spreadsheet.")
            
            if len(all_data) == 0:
                print("No records to process.")
                return
            
            # Find records that haven't been processed yet
            # Assuming there's a column that indicates processing status
            new_records = []
            for record in all_data:
                # Check various possible column names for processed status
                processed = (
                    record.get('Processed', '').lower() == 'yes' or
                    record.get('Status', '').lower() == 'processed' or
                    record.get('Sent', '').lower() == 'yes'
                )
                
                if not processed:
                    new_records.append(record)
            
            print(f"Found {len(new_records)} new records to process.")
            
            if len(new_records) == 0:
                print("No new records to process.")
                return
                
            # Ask user if they want to process all new records
            process_all = input(f"Process all {len(new_records)} new records? (y/n): ")
            if process_all.lower() != 'y':
                # Allow selecting specific records
                print("Available new records:")
                for i, record in enumerate(new_records):
                    name = record.get('Name', f'Person {i+1}')
                    email = record.get('Email Address', record.get('Email', ''))
                    print(f"{i+1}. {name} ({email})")
                
                indices = input("Enter record numbers to process (comma-separated, e.g. 1,3): ")
                try:
                    indices = [int(idx.strip()) - 1 for idx in indices.split(',')]
                    selected_data = [new_records[i] for i in indices if 0 <= i < len(new_records)]
                except:
                    print("Invalid input, processing all new records.")
                    selected_data = new_records
            else:
                selected_data = new_records
            
            # Process selected records
            print(f"\nProcessing {len(selected_data)} records...")
            for i, record in enumerate(selected_data):
                print(f"\nProcessing record {i+1}/{len(selected_data)}...")
                try:
                    # Get name and email for better error reporting
                    name = record.get('Name', f'Record {i+1}')
                    email = record.get('Email Address', record.get('Email', ''))
                    
                    if not email:
                        print(f"Warning: No email address found for {name}, report will be generated but not sent")
                    
                    process_record(record)
                    
                    # Mark record as processed in the spreadsheet
                    if 'Timestamp' in record:
                        timestamp = record['Timestamp']
                        try:
                            # Find the row with this timestamp
                            cell = sheet.find(timestamp)
                            if cell:
                                # Add 'Yes' in the "Processed" column (add a new column if needed)
                                # Check if Processed column exists
                                if 'Processed' in headers:
                                    processed_col = headers.index('Processed') + 1
                                else:
                                    # Add a new column
                                    processed_col = len(headers) + 1
                                    sheet.update_cell(1, processed_col, 'Processed')
                                
                                # Mark as processed
                                sheet.update_cell(cell.row, processed_col, 'Yes')
                                print(f"Marked record for {name} as processed in the spreadsheet")
                        except Exception as e:
                            print(f"Could not mark record as processed: {e}")
                    
                except Exception as e:
                    print(f"Error processing record for {name}: {e}")
                    import traceback
                    print(traceback.format_exc())
            
            print("\nProcessing complete.")
            
        except Exception as e:
            print(f"Error processing spreadsheet: {e}")
            import traceback
            print(traceback.format_exc())
            
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        print(traceback.format_exc())

def process_single_submission(email=None, name=None, grade=None, timestamp=None):
    """Process the most recent form submission or a specific submission.
    
    Args:
        email (str, optional): Email to match in the submission
        name (str, optional): Name to match in the submission
        grade (str, optional): Grade to match in the submission
        timestamp (str, optional): Timestamp of the submission to process
        
    Returns:
        bool: True if processed successfully, False otherwise
    """
    try:
        print("Starting automated processing of new submission...")
        
        # Initialize Google Sheets
        sheet = init_gsheets()
        
        # Get all values including headers
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) <= 1:
            print("No data found in the spreadsheet.")
            return False
            
        # Extract headers (first row)
        headers = all_values[0]
        
        # Find the processed column or prepare to create it
        processed_col_idx = None
        for i, header in enumerate(headers):
            if header.lower() == 'processed':
                processed_col_idx = i
                break
        
        # If processed column doesn't exist, we'll create it
        if processed_col_idx is None:
            processed_col_idx = len(headers)
            headers.append('Processed')
            sheet.update_cell(1, processed_col_idx + 1, 'Processed')  # +1 for 1-indexed
            print("Created 'Processed' column")
        
        # Create records with original headers (no need for unique headers for a single record)
        # We reverse to prioritize newest submissions (assuming they're added at the bottom)
        target_row_idx = None
        target_record = None
        
        for row_idx, row in enumerate(reversed(all_values[1:]), 2):
            actual_idx = len(all_values) - row_idx + 1  # Convert back to actual row index
            
            # Ensure row has enough cells
            while len(row) <= processed_col_idx:
                row.append('')
                
            # Check if already processed
            if row[processed_col_idx].lower() == 'yes':
                continue
                
            # Create record from row
            record = {headers[i]: value for i, value in enumerate(row) if i < len(headers)}
            
            # Check if this record matches our criteria (if provided)
            if timestamp and record.get('Timestamp', '') != timestamp:
                continue
            if email and record.get('Email', '').lower() != email.lower():
                continue
            if name and record.get('Name', '').lower() != name.lower():
                continue
            if grade and record.get('Grade', '') != grade:
                continue
                
            # Found a match!
            target_row_idx = actual_idx
            target_record = record
            break
        
        if not target_record:
            print("No matching unprocessed records found.")
            return False
            
        # Process the record
        print(f"Processing record for {target_record.get('Name', 'Unknown')} (Row {target_row_idx})")
        result = process_record(target_record)
        
        # Mark as processed
        sheet.update_cell(target_row_idx, processed_col_idx + 1, 'Yes')
        print(f"Marked row {target_row_idx} as processed")
        
        print("Automated processing complete.")
        return True
        
    except Exception as e:
        print(f"Error in automated processing: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # Original main function still available when script is run directly
    main()