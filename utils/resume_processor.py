import io
import json
import os
import re
import zipfile
from typing import Dict, List, Tuple

import PyPDF2
import requests
from docx import Document

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

class ResumeProcessor:
    def __init__(self, mistral_api_key: str):
        self.mistral_api_key = mistral_api_key
        self.upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(self.upload_folder, exist_ok=True)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def extract_text(self, file_path: str) -> str:
        """Extract text from either PDF or DOCX file."""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

    def analyze_resume(self, resume_text: str, job_requirements: Dict) -> Tuple[float, str]:
        """Analyze resume using Mistral AI and return match score and insights."""
        prompt = f"""
        Analyze this resume against the job requirements and provide a JSON response with the following structure:
        {{
            "score": <number between 0-100>,
            "insights": {{
                "skills_match": {{
                    "matched_skills": [<list of matched skills>],
                    "unmatched_skills": [<list of missing skills>],
                    "comment": "<detailed comment about skills match>"
                }},
                "experience_match": {{
                    "comment": "<detailed comment about experience match>"
                }},
                "education_match": {{
                    "comment": "<detailed comment about education match>"
                }},
                "strengths": [<list of candidate's strengths>],
                "areas_for_improvement": [<list of areas for improvement>]
            }}
        }}

        Job Requirements:
        Title: {job_requirements['title']}
        Required Skills: {job_requirements['skills']}
        Experience Required: {job_requirements['experience']}
        Industry: {job_requirements['industry']}

        Resume Text:
        {resume_text}

        Provide ONLY the JSON response, no additional text.
        """

        headers = {
            "Authorization": f"Bearer {self.mistral_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistral-small",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes resumes against job requirements. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(MISTRAL_API_URL, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                # Get the response content
                content = response.json()["choices"][0]["message"]["content"]
                
                # Try to find JSON in the response
                try:
                    # First try to parse the entire response as JSON
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # If that fails, try to find JSON-like content between curly braces
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            # If still fails, create a basic result structure
                            result = {
                                "score": 0,
                                "insights": {
                                    "skills_match": {
                                        "matched_skills": [],
                                        "unmatched_skills": [],
                                        "comment": "Error analyzing skills match"
                                    },
                                    "experience_match": {
                                        "comment": "Error analyzing experience match"
                                    },
                                    "education_match": {
                                        "comment": "Error analyzing education match"
                                    },
                                    "strengths": ["Error analyzing strengths"],
                                    "areas_for_improvement": ["Error analyzing areas for improvement"]
                                }
                            }
                    else:
                        # If no JSON-like content found, create a basic result structure
                        result = {
                            "score": 0,
                            "insights": {
                                "skills_match": {
                                    "matched_skills": [],
                                    "unmatched_skills": [],
                                    "comment": "Error analyzing skills match"
                                },
                                "experience_match": {
                                    "comment": "Error analyzing experience match"
                                },
                                "education_match": {
                                    "comment": "Error analyzing education match"
                                },
                                "strengths": ["Error analyzing strengths"],
                                "areas_for_improvement": ["Error analyzing areas for improvement"]
                            }
                        }
                
                return result['score'], result['insights']
            else:
                return 0.0, f"Error analyzing resume: {response.status_code} - {response.text}"
        except Exception as e:
            return 0.0, f"Error analyzing resume: {str(e)}"

    def process_resume(self, file_path: str, job_requirements: Dict) -> Tuple[float, str]:
        """Process a resume file and return match score and insights."""
        try:
            resume_text = self.extract_text(file_path)
            return self.analyze_resume(resume_text, job_requirements)
        except Exception as e:
            return 0.0, f"Error processing resume: {str(e)}"

    def save_resume(self, file_content: bytes, filename: str) -> str:
        """Save uploaded resume file and return the file path."""
        file_path = os.path.join(self.upload_folder, filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return file_path

    def clean_filename(self, filename: str) -> str:
        """Clean filename to prevent security issues."""
        # Remove any path traversal attempts
        filename = os.path.basename(filename)
        # Remove any non-alphanumeric characters except dots and hyphens
        filename = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
        return filename

    def process_resumes(self, zip_file, job_requirements: Dict) -> List[Dict]:
        """Process multiple resumes from a ZIP file and return a list of processed resumes."""
        processed_resumes = []
        
        try:
            # Read the ZIP file
            zip_data = io.BytesIO(zip_file.read())
            
            with zipfile.ZipFile(zip_data) as zip_file:
                for filename in zip_file.namelist():
                    if filename.lower().endswith(('.pdf', '.docx')):
                        try:
                            # Extract file content
                            file_content = zip_file.read(filename)
                            # Clean filename
                            clean_filename = self.clean_filename(filename)
                            # Save file
                            file_path = self.save_resume(file_content, clean_filename)
                            
                            # Process resume with AI
                            match_score, ai_insights = self.process_resume(file_path, job_requirements)
                            
                            processed_resumes.append({
                                'filename': clean_filename,
                                'file_path': file_path,
                                'match_score': match_score,
                                'ai_insights': ai_insights
                            })
                            
                        except Exception as e:
                            print(f"Error processing {filename}: {str(e)}")
                            continue
                            
        except Exception as e:
            print(f"Error processing ZIP file: {str(e)}")
            
        return processed_resumes 