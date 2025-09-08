let currentStep = 1;
const totalSteps = 4;
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupDragAndDrop();
});
function initializeEventListeners() {
    document.getElementById('resumeInput').addEventListener('change', handleFileSelect);
    document.getElementById('resumeForm').addEventListener('submit', handleFormSubmit);
}
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    uploadArea.addEventListener('drop', handleDrop, false);
}
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}
function highlight(e) {
    document.getElementById('uploadArea').classList.add('drag-over');
}
function unhighlight(e) {
    document.getElementById('uploadArea').classList.remove('drag-over');
}
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        document.getElementById('resumeInput').files = files;
        handleFileSelect({ target: { files: files } });
    }
}
function handleFileSelect(event) {
    const file = event.target.files[0];
    const scanBtn = document.getElementById('scanBtn');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    
    if (file) {
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!validTypes.includes(file.type)) {
            showError('Please select a PDF or DOCX file only.');
            return;
        }
        const maxSize = 10 * 1024 * 1024; 
        if (file.size > maxSize) {
            showError('File size must be less than 10MB.');
            return;
        }
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
        scanBtn.classList.remove('d-none');
        hideError();
    } else {
        fileInfo.classList.add('d-none');
        scanBtn.classList.add('d-none');
    }
}
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('resumeInput');
    const roleSelect = document.getElementById('roleSelect');
    
    if (!fileInput.files[0]) {
        showError('Please select a resume file.');
        return;
    }
    showLoadingScreen();
    animateProgress();
    
    try {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('role', roleSelect.value);
        const response = await fetch('http://localhost:8001/api/upload-resume', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            setTimeout(() => {
                showResults(result.analysis);
            }, 1000);
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
        showUploadScreen();
    }
}
function showLoadingScreen() {
    document.getElementById('uploadSection').classList.add('d-none');
    document.getElementById('loadingSection').classList.remove('d-none');
    document.getElementById('resultsSection').classList.add('d-none');
}
function showUploadScreen() {
    document.getElementById('uploadSection').classList.remove('d-none');
    document.getElementById('loadingSection').classList.add('d-none');
    document.getElementById('resultsSection').classList.add('d-none');
}
function showResults(analysis) {
    document.getElementById('uploadSection').classList.add('d-none');
    document.getElementById('loadingSection').classList.add('d-none');
    document.getElementById('resultsSection').classList.remove('d-none');
    populateATSScore(analysis.ats_score);
    populateStats(analysis);
    populateSkills(analysis.skills);
    populateJobRecommendations(analysis.job_recommendations);
    populateContactInfo(analysis.contact_info);
}
function animateProgress() {
    const progressBar = document.getElementById('progressBar');
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
            clearInterval(interval);
        }
        progressBar.style.width = progress + '%';
    }, 300);
}
function populateATSScore(score) {
    const atsScoreElement = document.getElementById('atsScore');
    const scoreMessage = document.getElementById('scoreMessage');
    const atsScoreCard = document.getElementById('atsScoreCard');
    animateNumber(atsScoreElement, 0, score, 2000);
    if (score >= 80) {
        scoreMessage.textContent = "Excellent! Your resume is well-optimized for ATS systems.";
        atsScoreCard.classList.add('border-success');
        atsScoreElement.classList.add('text-success');
    } else if (score >= 60) {
        scoreMessage.textContent = "Good score! Consider some improvements for better ATS compatibility.";
        atsScoreCard.classList.add('border-warning');
        atsScoreElement.classList.add('text-warning');
    } else {
        scoreMessage.textContent = "Your resume needs optimization for better ATS performance.";
        atsScoreCard.classList.add('border-danger');
        atsScoreElement.classList.add('text-danger');
    }
}
function populateStats(analysis) {
    document.getElementById('experience').textContent = `${analysis.experience_years} years`;
    document.getElementById('education').textContent = analysis.education_level;
    document.getElementById('skillsCount').textContent = analysis.skills.length;
    document.getElementById('experienceLevel').textContent = analysis.analysis_details.experience_level;
}
function populateSkills(skills) {
    const skillsList = document.getElementById('skillsList');
    const noSkillsMessage = document.getElementById('noSkillsMessage');
    
    skillsList.innerHTML = '';
    
    if (skills.length === 0) {
        noSkillsMessage.classList.remove('d-none');
        return;
    }
    
    noSkillsMessage.classList.add('d-none');
    
    skills.forEach((skill, index) => {
        const skillBadge = document.createElement('span');
        skillBadge.className = 'badge bg-primary fs-6 skill-badge';
        skillBadge.textContent = skill;
        skillBadge.style.animationDelay = `${index * 0.1}s`;
        skillsList.appendChild(skillBadge);
    });
}
function populateJobRecommendations(recommendations) {
    const jobRecommendations = document.getElementById('jobRecommendations');
    jobRecommendations.innerHTML = '';
    
    recommendations.forEach((job, index) => {
        const jobCard = document.createElement('div');
        jobCard.className = 'card mb-3 job-card';
        jobCard.style.animationDelay = `${index * 0.2}s`;
        
        const matchClass = job.match >= 80 ? 'success' : job.match >= 60 ? 'warning' : 'secondary';
        
        jobCard.innerHTML = `
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h5 class="card-title mb-2">${job.title}</h5>
                        <p class="card-text text-muted mb-2">
                            <i class="fas fa-dollar-sign me-1"></i>
                            Salary Range: ${job.salary_range}
                        </p>
                        <div class="mb-2">
                            <small class="text-muted">Required Skills:</small><br>
                            ${job.requirements.map(req => 
                                `<span class="badge bg-outline-secondary me-1 mb-1">${req}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="col-md-4 text-center">
                        <div class="badge bg-${matchClass} fs-5 p-3 rounded-circle">
                            ${job.match}%<br>
                            <small>Match</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        jobRecommendations.appendChild(jobCard);
    });
}
function populateContactInfo(contactInfo) {
    const contactInfoElement = document.getElementById('contactInfo');
    const contactSection = document.getElementById('contactSection');
    
    contactInfoElement.innerHTML = '';
    
    if (Object.keys(contactInfo).length === 0) {
        contactSection.classList.add('d-none');
        return;
    }
    
    contactSection.classList.remove('d-none');
    
    if (contactInfo.email) {
        const emailDiv = document.createElement('div');
        emailDiv.className = 'col-md-4 mb-3';
        emailDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-envelope text-primary fs-4 me-3"></i>
                <div>
                    <small class="text-muted">Email</small><br>
                    <span>${contactInfo.email}</span>
                </div>
            </div>
        `;
        contactInfoElement.appendChild(emailDiv);
    }
    
    if (contactInfo.phone) {
        const phoneDiv = document.createElement('div');
        phoneDiv.className = 'col-md-4 mb-3';
        phoneDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-phone text-success fs-4 me-3"></i>
                <div>
                    <small class="text-muted">Phone</small><br>
                    <span>${contactInfo.phone}</span>
                </div>
            </div>
        `;
        contactInfoElement.appendChild(phoneDiv);
    }
    
    if (contactInfo.linkedin) {
        const linkedinDiv = document.createElement('div');
        linkedinDiv.className = 'col-md-4 mb-3';
        linkedinDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fab fa-linkedin text-info fs-4 me-3"></i>
                <div>
                    <small class="text-muted">LinkedIn</small><br>
                    <span>${contactInfo.linkedin}</span>
                </div>
            </div>
        `;
        contactInfoElement.appendChild(linkedinDiv);
    }
}
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentValue = Math.floor(start + (end - start) * progress);
        
        element.textContent = currentValue;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}
function showError(message) {
    const existingAlert = document.querySelector('.alert-danger');
    if (existingAlert) {
        existingAlert.remove();
    }
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show mt-3';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    const uploadBox = document.querySelector('.upload-box');
    uploadBox.insertAdjacentElement('afterend', alert);
}
function hideError() {
    const existingAlert = document.querySelector('.alert-danger');
    if (existingAlert) {
        existingAlert.remove();
    }
}
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
