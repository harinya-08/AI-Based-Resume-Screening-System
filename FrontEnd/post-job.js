
document.getElementById('jobForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const jobTitle = document.getElementById('jobTitle').value.trim();
  const companyName = document.getElementById('companyName').value.trim();
  const jobType = document.getElementById('jobType').value.trim();
  const experience = document.getElementById('experience').value.trim();
  const skills = document.getElementById('skills').value.trim();
  const newJob = {
    id: Date.now(),
    title: jobTitle,           
    company: companyName,     
    type: jobType,             
    experience: experience,
    skills: skills,
    applicants: []
  };
  const jobs = JSON.parse(localStorage.getItem('jobs')) || [];
  jobs.push(newJob);
  localStorage.setItem('jobs', JSON.stringify(jobs));
  alert('Job posted successfully!');
  this.reset();
});
