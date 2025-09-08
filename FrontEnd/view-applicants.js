
const postedJobs = JSON.parse(localStorage.getItem('jobs')) || [];
const postedJobsContainer = document.getElementById('postedJobs');
postedJobs.forEach(job => {
  const col = document.createElement('div');
  col.className = 'col-md-6';
  col.innerHTML = `
    <div class="job-card p-4">
      <h5 class="fw-bold">${job.title || 'Untitled'}</h5>
      <p><strong>Company:</strong> ${job.company || 'No Company Name'}</p>
      <p><strong>Type:</strong> ${job.type || 'N/A'}</p>
      <p><strong>Experience:</strong> ${job.experience || 'N/A'}</p>
      <p><strong>Skills:</strong> ${job.skills || 'N/A'}</p>

      <button class="btn btn-view me-2" onclick="toggleApplicants(${job.id})">View Applicants</button>
      <button class="btn btn-close" onclick="closeJob(${job.id})">Close</button>
      <div id="applicants-${job.id}" class="applicant-list d-none"></div>
    </div>
  `;
  postedJobsContainer.appendChild(col);
});
function toggleApplicants(jobId) {
  const jobs = JSON.parse(localStorage.getItem('jobs')) || [];
  const job = jobs.find(j => j.id === jobId);
  const container = document.getElementById(`applicants-${jobId}`);
  container.classList.toggle('d-none');
  if (!container.classList.contains('d-none')) {
    if (job.applicants && job.applicants.length > 0) {
      container.innerHTML = job.applicants.map(applicant => `
        <div>
          <strong>${applicant.name}</strong> - 
          <a href="${applicant.resume}" target="_blank">${applicant.resume}</a>
        </div>
      `).join('');
    } else {
      container.innerHTML = `<p>No applicants yet.</p>`;
    }
  }
}
function closeJob(jobId) {
  if (confirm('Are you sure you want to close this job?')) {
    let jobs = JSON.parse(localStorage.getItem('jobs')) || [];
    jobs = jobs.filter(j => j.id !== jobId);
    localStorage.setItem('jobs', JSON.stringify(jobs));
    alert('Job closed.');
    location.reload();
  }
}
