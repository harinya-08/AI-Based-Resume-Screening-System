
from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv 
from starlette.middleware.cors import CORSMiddleware  
from motor.motor_asyncio import AsyncIOMotorClient 
import os  
import logging  
from pathlib import Path 
from pydantic import BaseModel, Field 
from typing import List, Optional, Dict, Any  
import uuid 
from datetime import datetime 
import aiofiles  
import PyPDF2  
import docx  
import re 
import json  
from io import BytesIO 
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')

client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'resume_scanner')]

app = FastAPI()

api_router = APIRouter(prefix="/api")

UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True) 
class ResumeUpload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  
    filename: str 
    file_path: str  
    role: str  
    upload_time: datetime = Field(default_factory=datetime.utcnow)  
    analysis_status: str = "pending"  
    extracted_text: Optional[str] = None  
class ResumeAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))  
    resume_id: str 
    ats_score: int 
    skills: List[str]  
    experience_years: int  
    education_level: str  
    contact_info: Dict[str, str]  
    job_recommendations: List[Dict[str, Any]] 
    analysis_details: Dict[str, Any]  
    created_at: datetime = Field(default_factory=datetime.utcnow)  
class AnalysisResponse(BaseModel):
    resume_id: str  
    status: str  
    message: str  
    analysis: Optional[ResumeAnalysis] = None 
ROLE_SKILLS = {
    "Software Engineer": [
        "python", "java", "javascript", "react", "node.js", "sql", "git", "aws", "docker", 
        "kubernetes", "mongodb", "postgresql", "rest api", "microservices", "agile", "scrum",
        "html", "css", "typescript", "angular", "vue.js", "spring", "django", "flask"
    ],
    "Data Scientist": [
        "python", "r", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", 
        "numpy", "matplotlib", "seaborn", "sql", "statistics", "data visualization", "jupyter",
        "scikit-learn", "keras", "natural language processing", "computer vision", "big data",
        "spark", "hadoop", "tableau", "power bi", "excel"
    ],
    "Product Manager": [
        "product strategy", "roadmap", "user research", "analytics", "a/b testing", "agile",
        "scrum", "jira", "figma", "wireframing", "user experience", "market research", "sql",
        "excel", "google analytics", "mixpanel", "stakeholder management", "project management",
        "competitive analysis", "go-to-market", "product launch"
    ],
    "Software Engineer": [
        "python", "java", "javascript", "react", "node.js", "sql", "git", "aws", "docker", 
        "kubernetes", "mongodb", "postgresql", "rest api", "microservices", "agile", "scrum",
        "html", "css", "typescript", "angular", "vue.js", "spring", "django", "flask"
    ],
    "Frontend Developer": [
        "html", "css", "javascript", "react", "angular", "vue.js", "typescript", "sass", "webpack",
        "bootstrap", "tailwind css", "figma", "adobe xd", "responsive design", "jquery", "git"
    ],
    "Backend Developer": [
        "python", "java", "node.js", "express", "django", "flask", "spring boot", "sql", "mongodb",
        "postgresql", "redis", "docker", "aws", "rest api", "microservices", "git", "linux"
    ],
    "Full Stack Developer": [
        "html", "css", "javascript", "react", "node.js", "python", "sql", "mongodb", "git",
        "docker", "aws", "rest api", "typescript", "express", "django", "postgresql"
    ],
    "Mobile App Developer": [
        "react native", "flutter", "swift", "kotlin", "java", "dart", "firebase", "ios", "android",
        "xcode", "android studio", "git", "rest api", "sqlite", "realm"
    ],
    "DevOps Engineer": [
        "docker", "kubernetes", "aws", "jenkins", "terraform", "ansible", "git", "linux", "bash",
        "python", "ci/cd", "monitoring", "prometheus", "grafana", "nginx", "apache"
    ],
    "QA Engineer": [
        "selenium", "automation testing", "manual testing", "jira", "testng", "junit", "postman",
        "api testing", "regression testing", "agile", "scrum", "bug tracking", "test planning"
    ],
    "UI/UX Designer": [
        "figma", "sketch", "adobe xd", "photoshop", "illustrator", "wireframing", "prototyping",
        "user research", "usability testing", "design thinking", "html", "css", "responsive design"
    ],
    "System Administrator": [
        "linux", "windows server", "networking", "bash", "powershell", "docker", "vmware",
        "active directory", "dns", "dhcp", "firewall", "backup", "monitoring", "troubleshooting"
    ],
    "Database Administrator": [
        "sql", "mysql", "postgresql", "oracle", "sql server", "mongodb", "database design",
        "performance tuning", "backup", "recovery", "replication", "indexing", "stored procedures"
    ],
    "Cloud Architect": [
        "aws", "azure", "google cloud", "terraform", "cloudformation", "kubernetes", "docker",
        "microservices", "serverless", "lambda", "ec2", "s3", "vpc", "security", "cost optimization"
    ],
    "Cybersecurity Analyst": [
        "penetration testing", "vulnerability assessment", "network security", "incident response",
        "siem", "firewall", "ids/ips", "risk assessment", "compliance", "ethical hacking", "kali linux"
    ],
    "Network Engineer": [
        "cisco", "routing", "switching", "bgp", "ospf", "tcp/ip", "dns", "dhcp", "vpn", "firewall",
        "network troubleshooting", "wireshark", "network design", "wan", "lan"
    ],
    "Technical Writer": [
        "technical writing", "documentation", "api documentation", "markdown", "confluence", "jira",
        "html", "css", "user manuals", "process documentation", "content management", "editing"
    ],
    "Data Scientist": [
        "python", "r", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", 
        "numpy", "matplotlib", "seaborn", "sql", "statistics", "data visualization", "jupyter",
        "scikit-learn", "keras", "natural language processing", "computer vision", "big data"
    ],
    "Data Analyst": [
        "sql", "excel", "tableau", "power bi", "python", "r", "statistics", "data visualization",
        "google analytics", "looker", "data cleaning", "reporting", "dashboard", "pivot tables"
    ],
    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch", "scikit-learn", "machine learning", "deep learning",
        "mlops", "docker", "kubernetes", "aws", "model deployment", "feature engineering", "sql"
    ],
    "AI Engineer": [
        "python", "tensorflow", "pytorch", "machine learning", "deep learning", "nlp", "computer vision",
        "neural networks", "ai algorithms", "model optimization", "data preprocessing", "research"
    ],
    "Business Intelligence Analyst": [
        "sql", "tableau", "power bi", "looker", "data warehousing", "etl", "reporting", "dashboards",
        "data modeling", "business analysis", "excel", "statistics", "data visualization"
    ],
    "Research Scientist": [
        "python", "r", "matlab", "statistics", "machine learning", "research methodology", "data analysis",
        "publications", "academic writing", "experimental design", "peer review", "grant writing"
    ],
    "Product Manager": [
        "product strategy", "roadmap", "user research", "analytics", "a/b testing", "agile",
        "scrum", "jira", "figma", "wireframing", "user experience", "market research", "sql",
        "excel", "google analytics", "mixpanel", "stakeholder management", "project management"
    ],
    "Project Manager": [
        "project management", "agile", "scrum", "jira", "confluence", "risk management", "stakeholder management",
        "gantt charts", "budget management", "resource planning", "communication", "leadership", "pmp"
    ],
    "Business Analyst": [
        "business analysis", "requirements gathering", "process improvement", "sql", "excel", "visio",
        "uml", "data analysis", "stakeholder management", "documentation", "user stories", "testing"
    ],
    "Operations Manager": [
        "operations management", "process improvement", "lean", "six sigma", "project management",
        "supply chain", "inventory management", "budgeting", "team leadership", "kpi tracking"
    ],
    "Strategy Consultant": [
        "strategic planning", "business strategy", "market analysis", "financial modeling", "excel",
        "powerpoint", "data analysis", "problem solving", "client management", "presentation skills"
    ],
    "Business Development Manager": [
        "business development", "sales", "lead generation", "crm", "salesforce", "market research",
        "negotiation", "partnership", "revenue growth", "client relationship", "networking"
    ],
    "Scrum Master": [
        "scrum", "agile", "jira", "confluence", "facilitation", "coaching", "team leadership",
        "sprint planning", "retrospectives", "kanban", "scaled agile", "servant leadership"
    ],
    "Product Owner": [
        "product ownership", "user stories", "backlog management", "agile", "scrum", "jira",
        "stakeholder management", "requirements analysis", "acceptance criteria", "prioritization"
    ],
    "Digital Marketing Specialist": [
        "digital marketing", "google ads", "facebook ads", "seo", "sem", "google analytics", "email marketing",
        "content marketing", "social media", "conversion optimization", "a/b testing", "marketing automation"
    ],
    "Marketing Manager": [
        "marketing strategy", "campaign management", "brand management", "content marketing", "seo",
        "social media", "google analytics", "marketing automation", "budget management", "team leadership"
    ],
    "Sales Manager": [
        "sales management", "lead generation", "crm", "salesforce", "sales strategy", "team leadership",
        "forecasting", "negotiation", "client relationship", "pipeline management", "revenue growth"
    ],
    "Account Manager": [
        "account management", "client relationship", "crm", "salesforce", "communication", "negotiation",
        "upselling", "cross-selling", "customer retention", "project coordination", "problem solving"
    ],
    "Customer Success Manager": [
        "customer success", "client relationship", "account management", "crm", "customer retention",
        "onboarding", "training", "support", "upselling", "customer advocacy", "problem solving"
    ],
    "Social Media Manager": [
        "social media marketing", "content creation", "facebook", "instagram", "twitter", "linkedin",
        "social media analytics", "community management", "influencer marketing", "paid social", "copywriting"
    ],
    "Content Marketing Manager": [
        "content marketing", "content strategy", "copywriting", "seo", "blogging", "email marketing",
        "social media", "analytics", "content management", "editorial calendar", "brand voice"
    ],
    "Financial Analyst": [
        "financial analysis", "excel", "financial modeling", "budgeting", "forecasting", "valuation",
        "financial reporting", "variance analysis", "investment analysis", "risk assessment", "sql"
    ],
    "Accountant": [
        "accounting", "bookkeeping", "financial reporting", "tax preparation", "excel", "quickbooks",
        "gaap", "accounts payable", "accounts receivable", "reconciliation", "auditing", "budgeting"
    ],
    "Investment Analyst": [
        "investment analysis", "financial modeling", "valuation", "excel", "bloomberg", "market research",
        "portfolio management", "risk analysis", "due diligence", "financial reporting", "economics"
    ],
    "Risk Analyst": [
        "risk management", "risk assessment", "financial modeling", "excel", "statistics", "data analysis",
        "regulatory compliance", "stress testing", "credit analysis", "market risk", "operational risk"
    ],
    "Auditor": [
        "auditing", "internal audit", "risk assessment", "compliance", "financial analysis", "excel",
        "gaap", "sox compliance", "process improvement", "documentation", "testing", "reporting"
    ],
    "HR Manager": [
        "human resources", "recruitment", "employee relations", "performance management", "compensation",
        "benefits", "hr policies", "training", "hris", "compliance", "conflict resolution", "leadership"
    ],
    "Recruiter": [
        "recruitment", "talent acquisition", "interviewing", "sourcing", "ats", "linkedin recruiter",
        "candidate screening", "job posting", "networking", "relationship building", "negotiation"
    ],
    "HR Business Partner": [
        "hr business partnering", "strategic hr", "change management", "employee relations", "performance management",
        "talent development", "succession planning", "hr analytics", "coaching", "consulting", "leadership"
    ],
    "Talent Acquisition Specialist": [
        "talent acquisition", "recruitment", "sourcing", "interviewing", "ats", "linkedin recruiter",
        "employer branding", "candidate experience", "recruiting metrics", "diversity recruiting", "networking"
    ],
    "Graphic Designer": [
        "graphic design", "photoshop", "illustrator", "indesign", "branding", "logo design", "print design",
        "web design", "typography", "color theory", "layout", "creative suite", "figma"
    ],
    "Web Designer": [
        "web design", "html", "css", "javascript", "responsive design", "ui design", "ux design",
        "photoshop", "figma", "wordpress", "bootstrap", "user experience", "wireframing"
    ],
    "Video Editor": [
        "video editing", "premiere pro", "after effects", "final cut pro", "motion graphics", "color correction",
        "audio editing", "storytelling", "video production", "youtube", "social media", "creative suite"
    ],
    "Content Writer": [
        "content writing", "copywriting", "seo writing", "blogging", "research", "editing", "proofreading",
        "content strategy", "social media writing", "email marketing", "wordpress", "cms"
    ],
    "Copywriter": [
        "copywriting", "advertising", "marketing copy", "email marketing", "social media", "web copy",
        "brand voice", "persuasive writing", "a/b testing", "conversion optimization", "creative writing"
    ],
    "Teacher": [
        "teaching", "curriculum development", "lesson planning", "classroom management", "assessment",
        "educational technology", "student engagement", "differentiated instruction", "communication", "patience"
    ],
    "Nurse": [
        "nursing", "patient care", "medical terminology", "healthcare", "clinical skills", "documentation",
        "medication administration", "infection control", "communication", "empathy", "critical thinking"
    ],
    "Lawyer": [
        "legal research", "legal writing", "litigation", "contract law", "negotiation", "client counseling",
        "case management", "legal analysis", "court procedures", "compliance", "ethics"
    ],
    "Doctor": [
        "medical diagnosis", "patient care", "medical terminology", "clinical skills", "surgery", "emergency medicine",
        "medical research", "healthcare", "communication", "empathy", "critical thinking", "medical ethics"
    ],
    "Pharmacist": [
        "pharmacy", "medication management", "pharmaceutical care", "drug interactions", "patient counseling",
        "clinical pharmacy", "healthcare", "medical terminology", "quality assurance", "compliance"
    ]
}
JOB_REQUIREMENTS = {
    "Software Engineer": {
        "required_skills": ["programming", "software development", "coding"],
        "preferred_skills": ["python", "javascript", "react", "sql", "git"],
        "min_experience": 0,
        "education": ["bachelor", "master", "computer science", "engineering"]
    },
    "Data Scientist": {
        "required_skills": ["data analysis", "machine learning", "statistics"],
        "preferred_skills": ["python", "r", "tensorflow", "pandas", "sql"],
        "min_experience": 1,
        "education": ["bachelor", "master", "phd", "statistics", "mathematics", "computer science"]
    },
    "Product Manager": {
        "required_skills": ["product management", "strategy", "analytics"],
        "preferred_skills": ["roadmap", "user research", "agile", "sql"],
        "min_experience": 2,
        "education": ["bachelor", "master", "mba", "business", "engineering"]
    },
    "Frontend Developer": {
        "required_skills": ["html", "css", "javascript"],
        "preferred_skills": ["react", "angular", "vue.js", "typescript", "responsive design"],
        "min_experience": 0,
        "education": ["bachelor", "associate", "computer science", "web development"]
    },
    "Backend Developer": {
        "required_skills": ["programming", "database", "api"],
        "preferred_skills": ["python", "java", "node.js", "sql", "rest api"],
        "min_experience": 1,
        "education": ["bachelor", "master", "computer science", "engineering"]
    },
    "Full Stack Developer": {
        "required_skills": ["frontend", "backend", "database"],
        "preferred_skills": ["html", "css", "javascript", "python", "sql"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "computer science", "engineering"]
    },
    "Mobile App Developer": {
        "required_skills": ["mobile development", "programming"],
        "preferred_skills": ["react native", "flutter", "swift", "kotlin", "ios", "android"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "computer science", "engineering"]
    },
    "DevOps Engineer": {
        "required_skills": ["automation", "deployment", "infrastructure"],
        "preferred_skills": ["docker", "kubernetes", "aws", "jenkins", "ci/cd"],
        "min_experience": 2,
        "education": ["bachelor", "master", "computer science", "engineering"]
    },
    "QA Engineer": {
        "required_skills": ["testing", "quality assurance"],
        "preferred_skills": ["automation testing", "selenium", "manual testing", "jira"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "computer science", "engineering"]
    },
    "UI/UX Designer": {
        "required_skills": ["design", "user experience"],
        "preferred_skills": ["figma", "sketch", "wireframing", "prototyping", "user research"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "design", "hci", "art"]
    },
    "Data Scientist": {
        "required_skills": ["data analysis", "machine learning", "statistics"],
        "preferred_skills": ["python", "r", "tensorflow", "pandas", "sql"],
        "min_experience": 1,
        "education": ["bachelor", "master", "phd", "statistics", "mathematics", "computer science"]
    },
    "Data Analyst": {
        "required_skills": ["data analysis", "excel", "sql"],
        "preferred_skills": ["tableau", "power bi", "python", "statistics"],
        "min_experience": 0,
        "education": ["bachelor", "associate", "business", "mathematics", "statistics"]
    },
    "Machine Learning Engineer": {
        "required_skills": ["machine learning", "programming", "data"],
        "preferred_skills": ["python", "tensorflow", "pytorch", "mlops", "aws"],
        "min_experience": 2,
        "education": ["bachelor", "master", "computer science", "engineering", "mathematics"]
    },
    "Product Manager": {
        "required_skills": ["product management", "strategy", "analytics"],
        "preferred_skills": ["roadmap", "user research", "agile", "sql"],
        "min_experience": 2,
        "education": ["bachelor", "master", "mba", "business", "engineering"]
    },
    "Project Manager": {
        "required_skills": ["project management", "leadership", "planning"],
        "preferred_skills": ["agile", "scrum", "pmp", "jira", "risk management"],
        "min_experience": 2,
        "education": ["bachelor", "master", "business", "engineering", "management"]
    },
    "Business Analyst": {
        "required_skills": ["business analysis", "requirements", "documentation"],
        "preferred_skills": ["sql", "excel", "process improvement", "stakeholder management"],
        "min_experience": 1,
        "education": ["bachelor", "master", "business", "economics", "engineering"]
    },
    "Digital Marketing Specialist": {
        "required_skills": ["digital marketing", "online advertising"],
        "preferred_skills": ["google ads", "facebook ads", "seo", "analytics", "email marketing"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "marketing", "business", "communications"]
    },
    "Marketing Manager": {
        "required_skills": ["marketing", "campaign management", "strategy"],
        "preferred_skills": ["digital marketing", "brand management", "analytics", "leadership"],
        "min_experience": 3,
        "education": ["bachelor", "master", "mba", "marketing", "business"]
    },
    "Sales Manager": {
        "required_skills": ["sales", "leadership", "customer relationship"],
        "preferred_skills": ["crm", "salesforce", "negotiation", "team management"],
        "min_experience": 3,
        "education": ["bachelor", "master", "business", "sales", "marketing"]
    },
    "Financial Analyst": {
        "required_skills": ["financial analysis", "excel", "modeling"],
        "preferred_skills": ["budgeting", "forecasting", "valuation", "sql"],
        "min_experience": 1,
        "education": ["bachelor", "master", "finance", "accounting", "economics", "business"]
    },
    "Accountant": {
        "required_skills": ["accounting", "bookkeeping", "financial reporting"],
        "preferred_skills": ["excel", "quickbooks", "tax preparation", "gaap"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "accounting", "finance", "business"]
    },
    "HR Manager": {
        "required_skills": ["human resources", "employee relations", "recruitment"],
        "preferred_skills": ["performance management", "compensation", "hris", "leadership"],
        "min_experience": 3,
        "education": ["bachelor", "master", "hr", "business", "psychology"]
    },
    "Recruiter": {
        "required_skills": ["recruitment", "interviewing", "sourcing"],
        "preferred_skills": ["ats", "linkedin recruiter", "candidate screening"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "hr", "business", "psychology"]
    },
    "Graphic Designer": {
        "required_skills": ["graphic design", "design software"],
        "preferred_skills": ["photoshop", "illustrator", "branding", "typography"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "design", "art", "visual arts"]
    },
    "Content Writer": {
        "required_skills": ["writing", "content creation"],
        "preferred_skills": ["seo writing", "copywriting", "research", "cms"],
        "min_experience": 1,
        "education": ["bachelor", "associate", "english", "journalism", "communications"]
    }
}
def get_job_requirements(role):
    if role in JOB_REQUIREMENTS:
        return JOB_REQUIREMENTS[role]
    else:
        return {
            "required_skills": ["professional skills", "communication"],
            "preferred_skills": ["teamwork", "problem solving", "leadership"],
            "min_experience": 1,
            "education": ["bachelor", "associate", "relevant degree"]
        }
class ResumeAnalyzer:
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting PDF text: {e}")
            return ""

    def extract_text_from_docx(self, file_content: bytes) -> str:
        try:
            doc = docx.Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logging.error(f"Error extracting DOCX text: {e}")
            return ""

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        contact_info = {}
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info["email"] = emails[0]
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info["phone"] = phones[0]
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            contact_info["linkedin"] = linkedin[0]
        
        return contact_info

    def extract_skills(self, text: str, role: str) -> List[str]:
        text_lower = text.lower()
        role_skills = ROLE_SKILLS.get(role, [])
        found_skills = []
        
        for skill in role_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills

    def calculate_experience_years(self, text: str) -> int:
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:?\s*(\d+)',
            r'(\d+)\s*years?\s*in',
            r'(\d+)\s*years?\s*with'
        ]
        
        years = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches])
        
        date_patterns = [
            r'(\d{4})\s*-\s*(\d{4})',
            r'(\d{4})\s*to\s*(\d{4})',
            r'(\d{4})\s*–\s*(\d{4})'
        ]
        
        job_years = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for start, end in matches:
                job_years.append(int(end) - int(start))
        
        all_years = years + job_years
        return max(all_years) if all_years else 0

    def extract_education_level(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(term in text_lower for term in ["phd", "ph.d", "doctorate", "doctoral"]):
            return "PhD"
        elif any(term in text_lower for term in ["master", "m.s", "m.a", "mba", "m.tech", "m.sc"]):
            return "Master's"
        elif any(term in text_lower for term in ["bachelor", "b.s", "b.a", "b.tech", "b.sc", "b.e"]):
            return "Bachelor's"
        elif any(term in text_lower for term in ["associate", "diploma", "certificate"]):
            return "Associate/Diploma"
        else:
            return "High School"

    def calculate_ats_score(self, text: str, role: str, skills: List[str], 
                          experience_years: int, education_level: str) -> int:
        score = 0
        requirements = JOB_REQUIREMENTS.get(role, {})
        required_skills = requirements.get("required_skills", [])
        preferred_skills = requirements.get("preferred_skills", [])
        
        text_lower = text.lower()
        required_found = sum(1 for skill in required_skills if skill.lower() in text_lower)
        preferred_found = len(skills)
        
        skills_score = (required_found / len(required_skills) * 30) if required_skills else 0
        skills_score += (preferred_found / len(preferred_skills) * 20) if preferred_skills else 0
        score += min(skills_score, 50)
        min_exp = requirements.get("min_experience", 0)
        if experience_years >= min_exp:
            exp_score = min(25, 15 + (experience_years - min_exp) * 2)
        else:
            exp_score = (experience_years / min_exp) * 15 if min_exp > 0 else 15
        score += exp_score
        education_scores = {
            "PhD": 15, "Master's": 12, "Bachelor's": 10, 
            "Associate/Diploma": 7, "High School": 5
        }
        score += education_scores.get(education_level, 5)
        structure_score = 0
        if any(section in text_lower for section in ["experience", "work", "employment"]):
            structure_score += 3
        if any(section in text_lower for section in ["education", "qualification"]):
            structure_score += 3
        if any(section in text_lower for section in ["skills", "technical"]):
            structure_score += 2
        if any(section in text_lower for section in ["contact", "email", "phone"]):
            structure_score += 2
        score += structure_score
        
        return min(int(score), 100)

    def generate_job_recommendations(self, skills: List[str], role: str, 
                                   experience_years: int) -> List[Dict[str, Any]]:
        recommendations = []
        if role == "Software Engineer":
            base_jobs = [
                {"title": "Senior Software Engineer", "match": 85, "requirements": ["3+ years experience", "Python/Java", "System Design"]},
                {"title": "Full Stack Developer", "match": 80, "requirements": ["React/Angular", "Node.js/Python", "Database"]},
                {"title": "Backend Developer", "match": 75, "requirements": ["API Development", "Database Design", "Cloud Services"]},
                {"title": "Frontend Developer", "match": 70, "requirements": ["React/Vue/Angular", "JavaScript", "CSS/HTML"]},
                {"title": "DevOps Engineer", "match": 65, "requirements": ["Docker/Kubernetes", "AWS/Cloud", "CI/CD"]}
            ]
        elif role == "Data Scientist":
            base_jobs = [
                {"title": "Senior Data Scientist", "match": 85, "requirements": ["ML/AI", "Python/R", "Statistics"]},
                {"title": "Machine Learning Engineer", "match": 80, "requirements": ["TensorFlow/PyTorch", "MLOps", "Cloud ML"]},
                {"title": "Data Analyst", "match": 75, "requirements": ["SQL", "Data Visualization", "Excel/Tableau"]},
                {"title": "Research Scientist", "match": 70, "requirements": ["PhD preferred", "Research experience", "Publications"]},
                {"title": "Business Analyst", "match": 65, "requirements": ["Business Intelligence", "Analytics", "SQL"]}
            ]
        else:  
            base_jobs = [
                {"title": "Senior Product Manager", "match": 85, "requirements": ["5+ years PM experience", "Strategy", "Analytics"]},
                {"title": "Product Owner", "match": 80, "requirements": ["Agile/Scrum", "Stakeholder Management", "Roadmap"]},
                {"title": "Business Analyst", "match": 75, "requirements": ["Requirements Analysis", "Process Improvement", "Documentation"]},
                {"title": "Project Manager", "match": 70, "requirements": ["Project Management", "Team Leadership", "Communication"]},
                {"title": "Growth Product Manager", "match": 65, "requirements": ["A/B Testing", "Analytics", "Growth Strategy"]}
            ]
        for job in base_jobs:
            if experience_years >= 5:
                job["match"] = min(job["match"] + 10, 100)
            elif experience_years >= 3:
                job["match"] = min(job["match"] + 5, 100)
            relevant_skills = [skill for skill in skills if any(req_skill.lower() in skill.lower() for req_skill in job["requirements"])]
            if len(relevant_skills) >= 3:
                job["match"] = min(job["match"] + 10, 100)
            
            job["salary_range"] = self.estimate_salary_range(job["title"], experience_years)
        
        return sorted(base_jobs, key=lambda x: x["match"], reverse=True)[:5]

    def estimate_salary_range(self, job_title: str, experience_years: int) -> str:
        base_salaries = {
            "Senior Software Engineer": (90000, 150000),
            "Software Engineer": (70000, 120000),
            "Full Stack Developer": (80000, 130000),
            "Backend Developer": (75000, 125000),
            "Frontend Developer": (70000, 120000),
            "DevOps Engineer": (85000, 140000),
            "Senior Data Scientist": (100000, 160000),
            "Data Scientist": (80000, 140000),
            "Machine Learning Engineer": (95000, 155000),
            "Data Analyst": (60000, 100000),
            "Research Scientist": (90000, 150000),
            "Business Analyst": (65000, 110000),
            "Senior Product Manager": (110000, 180000),
            "Product Manager": (90000, 150000),
            "Product Owner": (85000, 135000),
            "Project Manager": (75000, 125000),
            "Growth Product Manager": (95000, 160000)
        }
        
        base_min, base_max = base_salaries.get(job_title, (50000, 100000))
        exp_multiplier = 1 + (experience_years * 0.05)
        adj_min = int(base_min * exp_multiplier)
        adj_max = int(base_max * exp_multiplier)
        
        return f"${adj_min:,} - ${adj_max:,}"

    async def analyze_resume(self, text: str, role: str) -> Dict[str, Any]:
        skills = self.extract_skills(text, role)
        experience_years = self.calculate_experience_years(text)
        education_level = self.extract_education_level(text)
        contact_info = self.extract_contact_info(text)
        ats_score = self.calculate_ats_score(text, role, skills, experience_years, education_level)
        job_recommendations = self.generate_job_recommendations(skills, role, experience_years)
        
        return {
            "skills": skills,
            "experience_years": experience_years,
            "education_level": education_level,
            "contact_info": contact_info,
            "ats_score": ats_score,
            "job_recommendations": job_recommendations,
            "analysis_details": {
                "total_skills_found": len(skills),
                "role_specific_skills": len([s for s in skills if s in ROLE_SKILLS.get(role, [])]),
                "resume_length": len(text),
                "has_contact_info": len(contact_info) > 0,
                "experience_level": "Senior" if experience_years >= 5 else "Mid-level" if experience_years >= 2 else "Entry-level"
            }
        }

analyzer = ResumeAnalyzer()
@api_router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...)
):
    try:
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
        file_content = await file.read()
        if file.filename.lower().endswith('.pdf'):
            extracted_text = analyzer.extract_text_from_pdf(file_content)
        else:
            extracted_text = analyzer.extract_text_from_docx(file_content)
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file")
        file_id = str(uuid.uuid4())
        file_path = UPLOADS_DIR / f"{file_id}_{file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        resume_record = ResumeUpload(
            id=file_id,
            filename=file.filename,
            file_path=str(file_path),
            role=role,
            analysis_status="processing",
            extracted_text=extracted_text
        )
        await db.resumes.insert_one(resume_record.dict())
        analysis_result = await analyzer.analyze_resume(extracted_text, role)
        analysis_record = ResumeAnalysis(
            resume_id=file_id,
            ats_score=analysis_result["ats_score"],
            skills=analysis_result["skills"],
            experience_years=analysis_result["experience_years"],
            education_level=analysis_result["education_level"],
            contact_info=analysis_result["contact_info"],
            job_recommendations=analysis_result["job_recommendations"],
            analysis_details=analysis_result["analysis_details"]
        )
        await db.analyses.insert_one(analysis_record.dict())
        await db.resumes.update_one(
            {"id": file_id},
            {"$set": {"analysis_status": "completed"}}
        )
        
        return AnalysisResponse(
            resume_id=file_id,
            status="completed",
            message="Resume analyzed successfully",
            analysis=analysis_record
        )
        
    except Exception as e:
        logging.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@api_router.get("/analysis/{resume_id}")
async def get_analysis(resume_id: str):
    try:
        analysis = await db.analyses.find_one({"resume_id": resume_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        analysis["_id"] = str(analysis["_id"])
        
        return ResumeAnalysis(**analysis)
        
    except Exception as e:
        logging.error(f"Error retrieving analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@api_router.get("/resume/{resume_id}/status")
async def get_resume_status(resume_id: str):
    try:
        resume = await db.resumes.find_one({"id": resume_id})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {"resume_id": resume_id, "status": resume["analysis_status"]}
        
    except Exception as e:
        logging.error(f"Error retrieving resume status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving resume status: {str(e)}")
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
