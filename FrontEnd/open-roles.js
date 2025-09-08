
const jobsContainer = document.getElementById('jobs');
const jobs = JSON.parse(localStorage.getItem('jobs')) || [];
jobs.forEach(job => {
  const col = document.createElement('div');
  col.className = 'col-md-4 mb-4';
  col.innerHTML = `
    <div class="card shadow-sm p-3">
      <h5>${job.title || 'Untitled Role'}</h5>
      <p>${job.company || 'No Company Name'}</p>
      <p><strong>Type:</strong> ${job.type || 'N/A'} | <strong>Experience:</strong> ${job.experience || 'N/A'} | <strong>Skills:</strong> ${job.skills || 'N/A'}</p>
      <button class="btn btn-primary" onclick="applyJob(${job.id})" data-bs-toggle="modal" data-bs-target="#applyModal">Apply</button>
    </div>
  `;
  jobsContainer.appendChild(col);
});

function applyJob(jobId) {
  document.getElementById('applyJobId').value = jobId;
}
document.getElementById('applyForm').addEventListener('submit', function(e) {
  
  e.preventDefault();
  const jobId = Number(document.getElementById('applyJobId').value);
  const applicantName = document.getElementById('applicantName').value.trim();
  const resumeName = document.getElementById('resumeName').value.trim();
  if (!applicantName || !resumeName) {
    alert('Please fill all fields!');
    return;
  }
  const jobs = JSON.parse(localStorage.getItem('jobs')) || [];
  const jobIndex = jobs.findIndex(j => j.id === jobId);
  if (jobIndex === -1) {
    alert('Job not found!');
    return;
  }
  if (!jobs[jobIndex].applicants) {
    jobs[jobIndex].applicants = [];
  }
  jobs[jobIndex].applicants.push({
    name: applicantName,
    resume: resumeName
  });
  localStorage.setItem('jobs', JSON.stringify(jobs));
  alert('Application submitted successfully!');
  this.reset();
  const applyModal = bootstrap.Modal.getInstance(document.getElementById('applyModal'));
  applyModal.hide();
});
