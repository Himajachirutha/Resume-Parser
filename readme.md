# AI-Based Resume Screening

## Overview
The AI-Based Resume Screening tool helps recruiters efficiently screen and shortlist candidates based on job descriptions and uploaded resumes. Utilizing Mistral AI, the system analyzes resumes and provides a ranked shortlist of the best-matching candidates.

## Features
- **Job Posting & Resume Upload**
  - Recruiters can input job descriptions, including role, required skills, and experience.
  - Recruiters can upload a ZIP file containing resumes (PDF/DOCX).
  - Resume processing limits based on subscription plans:
    - Basic: 10 resumes
    - Medium: 25 resumes
    - Premium: 50 resumes
- **AI-Based Resume Processing**
  - Extracts key details (skills, experience, education) from resumes.
  - Mistral AI compares resumes against job criteria.
  - Generates a shortlist of 5-10 best-matching resumes.
- **Results & Insights**
  - Provides a ranked list of shortlisted candidates.
  - AI-generated insights explaining why candidates were shortlisted.
  - Recruiters can view and download resumes.

## Workflow
1. **Job Description Input** → Recruiters enter job details.
2. **Resume Upload** → Recruiters upload resumes (limited by package).
3. **AI Processing** → Mistral AI analyzes and ranks resumes.
4. **Shortlist Generation** → The system displays top-matching resumes.
5. **Recruiter Review** → Recruiters view/download shortlisted resumes.

## Acceptance Criteria & Definitions of Done
### SC1.1: Job Description & Resume Upload
- **Acceptance Criteria:**
  - Recruiters can enter job role, required skills, experience, and industry details.
  - The system allows ZIP file upload containing resumes.
  - Resume limit is enforced based on subscription plan.
- **Definition of Done:**
  - Job description fields are functional.
  - ZIP files are accepted and processed correctly.
  - Resume limits are enforced.
- **Estimated Effort:** 10-15 person-hours
- **Subtasks:**
  1. Create job description input fields in the UI (2h)
  2. Implement ZIP file upload functionality (3h)
  3. Validate and extract resumes from ZIP files (3h)
  4. Enforce subscription-based resume limits (3h)
  5. Write unit tests for file upload and validation (2h)

### SC1.2: AI Resume Processing & Shortlisting
- **Acceptance Criteria:**
  - AI extracts candidate details (skills, experience, education).
  - AI compares resumes against job criteria and ranks candidates.
  - Shortlist includes 5-10 best-matching resumes.
- **Definition of Done:**
  - AI processes resumes accurately.
  - The system generates a ranked list of best matches.
  - Shortlist results appear in the recruiter’s dashboard.
- **Estimated Effort:** 20-25 person-hours
- **Subtasks:**
  1. Integrate Mistral AI for resume parsing and analysis (5h)
  2. Develop a matching algorithm for job criteria comparison (6h)
  3. Implement ranking logic based on best fit (5h)
  4. Optimize AI performance for faster processing (4h)
  5. Unit testing for AI processing and ranking accuracy (5h)

### SC1.3: Shortlist Display & Recruiter Dashboard
- **Acceptance Criteria:**
  - The system displays shortlisted resumes in an organized format.
  - Recruiters can view/download shortlisted resumes.
  - AI-generated insights explain selections.
- **Definition of Done:**
  - Shortlisted resumes appear with match scores.
  - AI insights are displayed in a user-friendly way.
  - Recruiters can easily download selected resumes.
- **Estimated Effort:** 15-20 person-hours
- **Subtasks:**
  1. Design and develop recruiter dashboard UI (4h)
  2. Implement shortlisted resume display logic (5h)
  3. Develop AI insights generation feature (5h)
  4. Enable resume download functionality (3h)
  5. Conduct UI/UX testing and improvements (3h)

### SC1.4: Subscription-Based Access Control
- **Acceptance Criteria:**
  - Recruiters can choose a package (Basic, Medium, Premium).
  - Resume upload limits are enforced based on package selection.
  - The system restricts access if limits are exceeded.
- **Definition of Done:**
  - Subscription packages are implemented correctly.
  - Resume processing limits function as expected.
  - The system notifies recruiters if they exceed their limit.
- **Estimated Effort:** 10-12 person-hours
- **Subtasks:**
  1. Implement subscription-based authentication (3h)
  2. Enforce resume upload limits per package (3h)
  3. Create UI notifications for subscription restrictions (3h)
  4. Test subscription access and restrictions (3h)
