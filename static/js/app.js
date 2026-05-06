/* ═══════════════════════════════════════════════════════════
   CV Generator — App Logic
   ═══════════════════════════════════════════════════════════ */

// ── STATE ────────────────────────────────────────────────────
let cvData = {
  template: 'classic',
  personal: { name: '', email: '', phone: '', location: '', linkedin: '', website: '' },
  summary: '',
  experience: [],
  education: [],
  skills: [],
  skill_categories: {},
  certifications: [],
  projects: [],
  languages: [],
};
let skillMode = 'flat';
let currentStep = 1;

// ── STEP NAVIGATION ──────────────────────────────────────────
function goStep(n) {
  if (n === 2 || n === 3 || n === 4) collectFormData();
  if (n === 4) renderFinalPreview();
  if (n === 3 || n === 2) renderPreview();

  document.querySelectorAll('.step-content').forEach(s => s.classList.remove('active'));
  document.getElementById(`step-${n}`).classList.add('active');

  document.querySelectorAll('.step').forEach(s => {
    const sn = parseInt(s.dataset.step);
    s.classList.remove('active', 'done');
    if (sn === n) s.classList.add('active');
    else if (sn < n) s.classList.add('done');
  });

  currentStep = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── FORM DATA COLLECTION ─────────────────────────────────────
function collectFormData() {
  cvData.personal = {
    name:     val('name'),
    email:    val('email'),
    phone:    val('phone'),
    location: val('location'),
    linkedin: val('linkedin'),
    website:  val('website'),
  };
  cvData.summary = val('summary');
  updateSummaryCount();

  // Experience
  cvData.experience = [];
  document.querySelectorAll('.exp-card').forEach(card => {
    const bullets = [];
    card.querySelectorAll('.bullet-text').forEach(b => {
      if (b.value.trim()) bullets.push(b.value.trim());
    });
    cvData.experience.push({
      title:      card.querySelector('.exp-title').value.trim(),
      company:    card.querySelector('.exp-company').value.trim(),
      location:   card.querySelector('.exp-location').value.trim(),
      start_date: card.querySelector('.exp-start').value.trim(),
      end_date:   card.querySelector('.exp-end').value.trim(),
      current:    card.querySelector('.exp-current').checked,
      bullets,
    });
  });

  // Education
  cvData.education = [];
  document.querySelectorAll('.edu-card').forEach(card => {
    cvData.education.push({
      school:     card.querySelector('.edu-school').value.trim(),
      degree:     card.querySelector('.edu-degree').value.trim(),
      field:      card.querySelector('.edu-field').value.trim(),
      start_date: card.querySelector('.edu-start').value.trim(),
      end_date:   card.querySelector('.edu-end').value.trim(),
      gpa:        card.querySelector('.edu-gpa').value.trim(),
      activities: card.querySelector('.edu-activities').value.trim(),
    });
  });

  // Skills (flat)
  if (skillMode === 'flat') {
    cvData.skill_categories = {};
  } else {
    cvData.skills = [];
    cvData.skill_categories = {};
    document.querySelectorAll('.cat-block').forEach(block => {
      const catName = block.querySelector('.cat-name-input').value.trim();
      const catSkills = [];
      block.querySelectorAll('.cat-skill-tag').forEach(t => {
        catSkills.push(t.dataset.skill);
      });
      if (catName && catSkills.length) cvData.skill_categories[catName] = catSkills;
    });
  }

  // Certifications
  cvData.certifications = [];
  document.querySelectorAll('.cert-card').forEach(card => {
    cvData.certifications.push({
      name:      card.querySelector('.cert-name').value.trim(),
      authority: card.querySelector('.cert-authority').value.trim(),
      date:      card.querySelector('.cert-date').value.trim(),
    });
  });

  // Projects
  cvData.projects = [];
  document.querySelectorAll('.proj-card').forEach(card => {
    cvData.projects.push({
      name:         card.querySelector('.proj-name').value.trim(),
      technologies: card.querySelector('.proj-tech').value.trim(),
      description:  card.querySelector('.proj-desc').value.trim(),
    });
  });

  // Languages
  cvData.languages = [];
  document.querySelectorAll('.lang-card').forEach(card => {
    cvData.languages.push({
      name:        card.querySelector('.lang-name').value.trim(),
      proficiency: card.querySelector('.lang-prof').value.trim(),
    });
  });
}

function val(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : '';
}

// ── POPULATE FORM FROM DATA ───────────────────────────────────
function populateForm(data) {
  cvData = { ...cvData, ...data };

  if (data.personal) {
    for (const [k, v] of Object.entries(data.personal)) {
      const el = document.getElementById(k);
      if (el) el.value = v || '';
    }
  }
  if (data.summary) {
    document.getElementById('summary').value = data.summary;
    updateSummaryCount();
  }

  // Clear & rebuild lists
  document.getElementById('experience-list').innerHTML = '';
  (data.experience || []).forEach(exp => addExperience(exp));

  document.getElementById('education-list').innerHTML = '';
  (data.education || []).forEach(edu => addEducation(edu));

  document.getElementById('certifications-list').innerHTML = '';
  (data.certifications || []).forEach(cert => addCertification(cert));

  document.getElementById('projects-list').innerHTML = '';
  (data.projects || []).forEach(proj => addProject(proj));

  document.getElementById('languages-list').innerHTML = '';
  (data.languages || []).forEach(lang => addLanguage(lang));

  // Skills
  cvData.skills = data.skills || [];
  renderSkillTags();

  renderPreview();
}

// ── EXPERIENCE ───────────────────────────────────────────────
function addExperience(data = {}) {
  const idx = Date.now();
  const card = document.createElement('div');
  card.className = 'item-card exp-card';
  card.innerHTML = `
    <div class="item-card-header">
      <span class="item-card-title">Pengalaman Kerja</span>
      <button class="btn-remove" onclick="this.closest('.item-card').remove(); renderPreview();">×</button>
    </div>
    <div class="item-form-grid">
      <div class="form-group">
        <label>Jabatan / Posisi *</label>
        <input class="exp-title" type="text" placeholder="Software Engineer" value="${esc(data.title || '')}">
      </div>
      <div class="form-group">
        <label>Nama Perusahaan *</label>
        <input class="exp-company" type="text" placeholder="PT Contoh Indonesia" value="${esc(data.company || '')}">
      </div>
      <div class="form-group">
        <label>Lokasi</label>
        <input class="exp-location" type="text" placeholder="Jakarta, Indonesia" value="${esc(data.location || '')}">
      </div>
      <div class="form-group">
        <label>Tanggal Mulai</label>
        <input class="exp-start" type="text" placeholder="Jan 2022" value="${esc(data.start_date || '')}">
      </div>
      <div class="form-group">
        <label>Tanggal Selesai</label>
        <input class="exp-end" type="text" placeholder="Des 2023" value="${esc(data.end_date === 'Present' ? '' : (data.end_date || ''))}">
      </div>
      <div class="form-group" style="padding-top:22px">
        <label class="checkbox-row">
          <input type="checkbox" class="exp-current" ${data.current ? 'checked' : ''}> Masih bekerja di sini
        </label>
      </div>
    </div>
    <div class="bullets-section">
      <div class="bullets-label">Deskripsi Pekerjaan (bullet points)</div>
      <div class="bullets-list" id="bullets-${idx}"></div>
      <button class="btn-add-bullet" onclick="addBullet('bullets-${idx}')">+ Tambah bullet point</button>
    </div>`;
  document.getElementById('experience-list').appendChild(card);

  const bulletsContainer = document.getElementById(`bullets-${idx}`);
  const bullets = data.bullets && data.bullets.length ? data.bullets : [''];
  bullets.forEach(b => addBullet(`bullets-${idx}`, b));

  card.querySelectorAll('input, textarea, select').forEach(el => {
    el.addEventListener('input', () => renderPreview());
  });
}

function addBullet(containerId, text = '') {
  const container = document.getElementById(containerId);
  if (!container) return;
  const row = document.createElement('div');
  row.className = 'bullet-row';
  row.innerHTML = `
    <textarea class="bullet-text" rows="2" placeholder="Contoh: Memimpin tim 5 engineer dalam membangun fitur X, meningkatkan performa 40%">${esc(text)}</textarea>
    <button class="btn-remove-bullet" onclick="this.parentNode.remove(); renderPreview();">×</button>`;
  row.querySelector('textarea').addEventListener('input', () => renderPreview());
  container.appendChild(row);
}

// ── EDUCATION ────────────────────────────────────────────────
function addEducation(data = {}) {
  const card = document.createElement('div');
  card.className = 'item-card edu-card';
  card.innerHTML = `
    <div class="item-card-header">
      <span class="item-card-title">Pendidikan</span>
      <button class="btn-remove" onclick="this.closest('.item-card').remove(); renderPreview();">×</button>
    </div>
    <div class="item-form-grid">
      <div class="form-group item-form-full">
        <label>Nama Institusi *</label>
        <input class="edu-school" type="text" placeholder="Universitas Indonesia" value="${esc(data.school || '')}">
      </div>
      <div class="form-group">
        <label>Gelar</label>
        <input class="edu-degree" type="text" placeholder="S1 / Bachelor of Science" value="${esc(data.degree || '')}">
      </div>
      <div class="form-group">
        <label>Bidang Studi</label>
        <input class="edu-field" type="text" placeholder="Teknik Informatika" value="${esc(data.field || '')}">
      </div>
      <div class="form-group">
        <label>Tahun Masuk</label>
        <input class="edu-start" type="text" placeholder="2018" value="${esc(data.start_date || '')}">
      </div>
      <div class="form-group">
        <label>Tahun Lulus</label>
        <input class="edu-end" type="text" placeholder="2022" value="${esc(data.end_date || '')}">
      </div>
      <div class="form-group">
        <label>IPK / GPA</label>
        <input class="edu-gpa" type="text" placeholder="3.75" value="${esc(data.gpa || '')}">
      </div>
      <div class="form-group item-form-full">
        <label>Kegiatan / Organisasi</label>
        <input class="edu-activities" type="text" placeholder="Ketua BEM, HIMAKOM" value="${esc(data.activities || '')}">
      </div>
    </div>`;
  document.getElementById('education-list').appendChild(card);
  card.querySelectorAll('input').forEach(el => el.addEventListener('input', () => renderPreview()));
}

// ── CERTIFICATIONS ───────────────────────────────────────────
function addCertification(data = {}) {
  const card = document.createElement('div');
  card.className = 'item-card cert-card';
  card.innerHTML = `
    <div class="item-card-header">
      <span class="item-card-title">Sertifikasi</span>
      <button class="btn-remove" onclick="this.closest('.item-card').remove();">×</button>
    </div>
    <div class="item-form-grid">
      <div class="form-group item-form-full">
        <label>Nama Sertifikasi *</label>
        <input class="cert-name" type="text" placeholder="AWS Certified Solutions Architect" value="${esc(data.name || '')}">
      </div>
      <div class="form-group">
        <label>Penerbit</label>
        <input class="cert-authority" type="text" placeholder="Amazon Web Services" value="${esc(data.authority || '')}">
      </div>
      <div class="form-group">
        <label>Tanggal</label>
        <input class="cert-date" type="text" placeholder="Mar 2023" value="${esc(data.date || '')}">
      </div>
    </div>`;
  document.getElementById('certifications-list').appendChild(card);
}

// ── PROJECTS ─────────────────────────────────────────────────
function addProject(data = {}) {
  const card = document.createElement('div');
  card.className = 'item-card proj-card';
  card.innerHTML = `
    <div class="item-card-header">
      <span class="item-card-title">Proyek</span>
      <button class="btn-remove" onclick="this.closest('.item-card').remove();">×</button>
    </div>
    <div class="item-form-grid">
      <div class="form-group item-form-full">
        <label>Nama Proyek *</label>
        <input class="proj-name" type="text" placeholder="E-Commerce Platform" value="${esc(data.name || '')}">
      </div>
      <div class="form-group item-form-full">
        <label>Teknologi yang Digunakan</label>
        <input class="proj-tech" type="text" placeholder="Python, Django, PostgreSQL, Docker" value="${esc(data.technologies || '')}">
      </div>
      <div class="form-group item-form-full">
        <label>Deskripsi</label>
        <textarea class="proj-desc" rows="3" placeholder="Deskripsi singkat tentang proyek dan dampaknya">${esc(data.description || '')}</textarea>
      </div>
    </div>`;
  document.getElementById('projects-list').appendChild(card);
}

// ── LANGUAGES ────────────────────────────────────────────────
function addLanguage(data = {}) {
  const card = document.createElement('div');
  card.className = 'item-card lang-card';
  card.innerHTML = `
    <div class="item-card-header">
      <span class="item-card-title">Bahasa</span>
      <button class="btn-remove" onclick="this.closest('.item-card').remove();">×</button>
    </div>
    <div class="item-form-grid">
      <div class="form-group">
        <label>Bahasa *</label>
        <input class="lang-name" type="text" placeholder="Bahasa Inggris" value="${esc(data.name || '')}">
      </div>
      <div class="form-group">
        <label>Kemampuan</label>
        <select class="lang-prof">
          ${['Native', 'Fluent', 'Professional', 'Intermediate', 'Basic'].map(p =>
            `<option value="${p}" ${data.proficiency === p ? 'selected' : ''}>${p}</option>`
          ).join('')}
        </select>
      </div>
    </div>`;
  document.getElementById('languages-list').appendChild(card);
}

// ── SKILLS (flat mode) ───────────────────────────────────────
function renderSkillTags() {
  const container = document.getElementById('skill-tags');
  container.innerHTML = '';
  cvData.skills.forEach((skill, i) => {
    const tag = document.createElement('div');
    tag.className = 'skill-tag';
    tag.innerHTML = `${esc(skill)}<button class="remove-tag" onclick="removeSkill(${i})">×</button>`;
    container.appendChild(tag);
  });
}

function removeSkill(idx) {
  cvData.skills.splice(idx, 1);
  renderSkillTags();
  renderPreview();
}

function setSkillMode(mode) {
  skillMode = mode;
  document.getElementById('mode-flat').classList.toggle('active', mode === 'flat');
  document.getElementById('mode-category').classList.toggle('active', mode === 'category');
  document.getElementById('skill-flat-mode').style.display = mode === 'flat' ? 'block' : 'none';
  document.getElementById('skill-category-mode').style.display = mode === 'category' ? 'block' : 'none';
}

function addSkillCategory() {
  const block = document.createElement('div');
  block.className = 'skill-cat-block cat-block';
  const catId = `cat-${Date.now()}`;
  block.innerHTML = `
    <div class="skill-cat-header">
      <input class="cat-name-input" type="text" placeholder="Nama Kategori (mis. Technical Skills)" style="flex:1">
      <button class="btn-remove" onclick="this.closest('.cat-block').remove();" style="margin-top:0">×</button>
    </div>
    <div class="skill-cat-tags-row" id="${catId}"></div>
    <div class="skill-input-row">
      <input type="text" placeholder="Ketik skill lalu Enter..." class="cat-skill-input" data-container="${catId}">
    </div>`;
  document.getElementById('skill-categories').appendChild(block);

  block.querySelector('.cat-skill-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      const skill = this.value.replace(/,/g, '').trim();
      if (skill) {
        addCategorySkillTag(document.getElementById(this.dataset.container), skill);
        this.value = '';
      }
    }
  });
}

function addCategorySkillTag(container, skill) {
  const tag = document.createElement('div');
  tag.className = 'skill-tag cat-skill-tag';
  tag.dataset.skill = skill;
  tag.innerHTML = `${esc(skill)}<button class="remove-tag" onclick="this.parentNode.remove();">×</button>`;
  container.appendChild(tag);
}

// ── TEMPLATE SELECTION ───────────────────────────────────────
function selectTemplate(tpl) {
  cvData.template = tpl;
  document.querySelectorAll('.template-card').forEach(c => c.classList.remove('selected'));
  document.querySelector(`[data-template="${tpl}"]`).classList.add('selected');
}

// ── CV PREVIEW (HTML) ─────────────────────────────────────────
function renderPreview() {
  collectFormData();
  const html = buildCVHtml(cvData);
  const el = document.getElementById('cv-preview');
  if (el) el.innerHTML = html || '<p class="preview-empty">Isi form untuk melihat preview</p>';
}

function renderFinalPreview() {
  collectFormData();
  const html = buildCVHtml(cvData);
  const el = document.getElementById('cv-preview-final');
  if (el) el.innerHTML = html || '<p class="preview-empty">Preview tidak tersedia</p>';
}

function buildCVHtml(d) {
  const tpl = d.template || 'classic';
  const p = d.personal || {};
  if (!p.name && !p.email) return '';

  const contactParts = [p.email, p.phone, p.location].filter(Boolean);
  const li = (p.linkedin || '').replace('https://www.linkedin.com/in/', '').replace('https://linkedin.com/in/', '').replace(/\/$/, '');
  if (li) contactParts.push(`linkedin.com/in/${li}`);
  if (p.website) contactParts.push(p.website);

  let html = `<div class="cv-name ${tpl}">${esc(p.name)}</div>`;
  if (contactParts.length) html += `<div class="cv-contact">${contactParts.map(esc).join(' | ')}</div>`;
  html += `<hr class="cv-hr ${tpl}">`;

  if (d.summary) {
    html += section('Professional Summary', tpl) + `<div class="cv-body">${esc(d.summary)}</div>`;
  }

  if ((d.experience || []).length) {
    html += section('Work Experience', tpl);
    d.experience.forEach(exp => {
      const end = exp.current ? 'Present' : (exp.end_date || 'Present');
      const dateRange = [exp.start_date, end].filter(Boolean).join(' – ');
      html += `<div class="cv-entry">
        <div class="cv-job-title">${esc(exp.title)} <span class="cv-job-date">${esc(dateRange)}</span></div>
        <div class="cv-company">${esc([exp.company, exp.location].filter(Boolean).join(' · '))}</div>
        ${(exp.bullets || []).filter(b => b.trim()).map(b => `<div class="cv-bullet">${esc(b)}</div>`).join('')}
      </div>`;
    });
  }

  if ((d.education || []).length) {
    html += section('Education', tpl);
    d.education.forEach(edu => {
      const degree = [edu.degree, edu.field ? `in ${edu.field}` : ''].filter(Boolean).join(' ');
      const dateRange = [edu.start_date, edu.end_date].filter(Boolean).join(' – ');
      html += `<div class="cv-entry">
        <div class="cv-job-title">${esc(degree)} <span class="cv-job-date">${esc(dateRange)}</span></div>
        <div class="cv-company">${esc(edu.school)}</div>
        ${edu.gpa ? `<div class="cv-body">GPA: ${esc(edu.gpa)}</div>` : ''}
      </div>`;
    });
  }

  const skills = d.skills || [];
  const skillCats = d.skill_categories || {};
  if (skills.length || Object.keys(skillCats).length) {
    html += section('Skills', tpl);
    if (Object.keys(skillCats).length) {
      for (const [cat, catSkills] of Object.entries(skillCats)) {
        if (catSkills.length) html += `<div class="cv-skills-text"><strong>${esc(cat)}:</strong> ${catSkills.map(esc).join(' · ')}</div>`;
      }
    } else {
      html += `<div class="cv-skills-text">${skills.map(esc).join(' · ')}</div>`;
    }
  }

  if ((d.certifications || []).length) {
    html += section('Certifications', tpl);
    d.certifications.forEach(c => {
      const line = [c.name, c.authority ? `– ${c.authority}` : '', c.date ? `(${c.date})` : ''].filter(Boolean).join(' ');
      html += `<div class="cv-bullet">${esc(line)}</div>`;
    });
  }

  if ((d.projects || []).length) {
    html += section('Projects', tpl);
    d.projects.forEach(proj => {
      html += `<div class="cv-entry">
        <div class="cv-job-title">${esc(proj.name)}</div>
        ${proj.technologies ? `<div class="cv-company">${esc(proj.technologies)}</div>` : ''}
        ${proj.description ? `<div class="cv-body">${esc(proj.description)}</div>` : ''}
      </div>`;
    });
  }

  if ((d.languages || []).length) {
    html += section('Languages', tpl);
    const langParts = d.languages.map(l => l.proficiency ? `${l.name} (${l.proficiency})` : l.name).filter(Boolean);
    html += `<div class="cv-skills-text">${langParts.map(esc).join(' · ')}</div>`;
  }

  return html;
}

function section(title, tpl) {
  return `<div class="cv-section-title ${tpl}">${title.toUpperCase()}</div><hr class="cv-section-hr">`;
}

// ── ATS CHECK ─────────────────────────────────────────────────
async function checkATS() {
  collectFormData();
  showLoading('Menganalisis ATS...');
  try {
    const res = await fetch('/api/ats-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cvData),
    });
    const json = await res.json();
    hideLoading();
    showATSResult(json);
  } catch (e) {
    hideLoading();
    showToast('Gagal cek ATS: ' + e.message, 'error');
  }
}

function showATSResult({ score, issues, tips }) {
  const ring = document.getElementById('ats-ring');
  const scoreText = document.getElementById('ats-score-text');
  const label = document.getElementById('ats-label');
  const result = document.getElementById('ats-result');

  const circumference = 326.7;
  const offset = circumference - (score / 100) * circumference;
  ring.style.strokeDashoffset = offset;

  const color = score >= 85 ? '#10B981' : score >= 60 ? '#F59E0B' : '#EF4444';
  ring.style.stroke = color;
  scoreText.textContent = score;
  scoreText.setAttribute('fill', color);

  label.textContent = score >= 85 ? 'Sangat Baik!' : score >= 60 ? 'Cukup Baik' : 'Perlu Perbaikan';
  label.style.color = color;

  let issuesHtml = '';
  if (issues.length) {
    issuesHtml = `<div class="ats-issues-title">Masalah yang Ditemukan</div>`;
    issues.forEach(i => { issuesHtml += `<div class="ats-issue-item">${esc(i)}</div>`; });
  }

  let tipsHtml = '';
  if (tips.length) {
    tipsHtml = `<div class="ats-tips-title" style="margin-top:10px">Saran Perbaikan</div>`;
    tips.forEach(t => { tipsHtml += `<div class="ats-tip-item">${esc(t)}</div>`; });
  }

  document.getElementById('ats-issues').innerHTML = issuesHtml;
  document.getElementById('ats-tips').innerHTML = tipsHtml;
  result.style.display = 'block';
}

// ── DOWNLOAD ──────────────────────────────────────────────────
async function downloadCV(format) {
  collectFormData();
  const endpoint = format === 'pdf' ? '/api/generate-pdf' : '/api/generate-docx';
  showLoading(`Membuat ${format.toUpperCase()}...`);
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cvData),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Download gagal');
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const name = cvData.personal.name.replace(/\s+/g, '_') || 'CV';
    a.download = `${name}_CV.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`CV berhasil didownload sebagai ${format.toUpperCase()}!`, 'success');
  } catch (e) {
    showToast('Gagal download: ' + e.message, 'error');
  } finally {
    hideLoading();
  }
}

// ── LINKEDIN IMPORT ───────────────────────────────────────────
async function parseLinkedIn(file) {
  const formData = new FormData();
  formData.append('file', file);
  showLoading('Memproses data LinkedIn...');
  try {
    const res = await fetch('/api/parse-linkedin', { method: 'POST', body: formData });
    const json = await res.json();
    hideLoading();
    if (json.success) {
      populateForm(json.data);
      goStep(2);
      showToast('Data LinkedIn berhasil diimport!', 'success');
    } else {
      showToast(json.error || 'Gagal memproses file', 'error');
    }
  } catch (e) {
    hideLoading();
    showToast('Error: ' + e.message, 'error');
  }
}

// ── TABS ──────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', function() {
    const tabId = this.dataset.tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    this.classList.add('active');
    document.getElementById(`tab-${tabId}`).classList.add('active');
  });
});

// ── SUMMARY WORD COUNT ────────────────────────────────────────
function updateSummaryCount() {
  const summary = document.getElementById('summary');
  const counter = document.getElementById('summary-count');
  if (summary && counter) {
    const words = summary.value.trim().split(/\s+/).filter(Boolean).length;
    counter.textContent = words;
    counter.style.color = words >= 25 ? '#10B981' : words >= 15 ? '#F59E0B' : '#EF4444';
  }
}
document.getElementById('summary').addEventListener('input', () => { updateSummaryCount(); renderPreview(); });
['name', 'email', 'phone', 'location', 'linkedin', 'website'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', () => renderPreview());
});

// ── SKILL INPUT (Enter / comma) ───────────────────────────────
document.getElementById('skill-input').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault();
    const skill = this.value.replace(/,/g, '').trim();
    if (skill && !cvData.skills.includes(skill)) {
      cvData.skills.push(skill);
      renderSkillTags();
      renderPreview();
    }
    this.value = '';
  }
});

// ── FILE UPLOAD (LinkedIn) ────────────────────────────────────
const uploadArea = document.getElementById('upload-area');
const fileInput  = document.getElementById('linkedin-file');
const parseBtn   = document.getElementById('btn-parse-linkedin');

fileInput.addEventListener('change', function() {
  if (this.files[0]) {
    document.getElementById('upload-label').textContent = this.files[0].name;
    uploadArea.classList.add('file-ready');
    parseBtn.disabled = false;
  }
});

uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.zip')) {
    fileInput.files = e.dataTransfer.files;
    document.getElementById('upload-label').textContent = file.name;
    uploadArea.classList.add('file-ready');
    parseBtn.disabled = false;
  } else {
    showToast('Harap drop file .zip dari LinkedIn', 'error');
  }
});

parseBtn.addEventListener('click', () => {
  if (fileInput.files[0]) parseLinkedIn(fileInput.files[0]);
});

document.getElementById('btn-manual').addEventListener('click', () => {
  if (cvData.experience.length === 0) addExperience();
  if (cvData.education.length === 0) addEducation();
  goStep(2);
});

// ── TOAST & LOADING ───────────────────────────────────────────
function showToast(msg, type = '') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = `toast show ${type}`;
  setTimeout(() => { toast.classList.remove('show'); }, 3500);
}

function showLoading(text = 'Memproses...') {
  document.getElementById('loading-text').textContent = text;
  document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

function esc(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── INIT ──────────────────────────────────────────────────────
(function init() {
  // Initialize with one empty experience & education if manual mode
  updateSummaryCount();
})();
