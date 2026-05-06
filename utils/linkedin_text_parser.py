"""
Parser untuk teks LinkedIn — digunakan oleh:
  1. LinkedIn Profile PDF  (Save to PDF dari profil)
  2. Paste teks dari halaman profil LinkedIn
"""
import re


# ── SECTION DETECTION ────────────────────────────────────────────────────────
# Keyword section header dalam bahasa Inggris dan Indonesia
SECTION_MAP = {
    'summary':          ['summary', 'about', 'ringkasan', 'tentang saya', 'tentang', 'profile'],
    'experience':       ['experience', 'work experience', 'pengalaman', 'pengalaman kerja', 'riwayat pekerjaan'],
    'education':        ['education', 'pendidikan', 'riwayat pendidikan'],
    'skills':           ['skills', 'top skills', 'keahlian', 'keterampilan', 'keahlian teratas'],
    'certifications':   ['licenses & certifications', 'certifications', 'sertifikasi', 'lisensi & sertifikasi'],
    'languages':        ['languages', 'bahasa'],
    'projects':         ['projects', 'proyek'],
    'accomplishments':  ['accomplishments', 'pencapaian', 'honors & awards', 'awards'],
    # LinkedIn PDF Indonesia: label area kontak sebelum sections utama
    'contact':          ['hubungi', 'kontak', 'contact info', 'informasi kontak'],
}

EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'(?:\+?\d[\d\s\-().]{7,15}\d)')
URL_RE   = re.compile(r'https?://\S+|linkedin\.com/in/\S+', re.I)

# Indonesian months added: Mei=May, Agu=Aug, Okt=Oct, Des=Dec
# Full Indonesian month names also included
DATE_PATTERN = (
    r'(?:Jan|Feb|Mar|Apr|May|Mei|Jun|Jul|Agu|Aug|Sep|Okt|Oct|Nov|Des|Dec|'
    r'January|February|March|April|June|July|August|September|October|November|December|'
    r'Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|'
    r'Present|Now|Sekarang|present|sekarang)'
    r'[\s\d,–\-]*(?:\d{4})?'
)
DATE_RANGE_RE = re.compile(
    rf'({DATE_PATTERN})\s*[–\-–—]\s*({DATE_PATTERN})',
    re.I
)
YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')

# Indonesian → English month mapping for date normalization
_MONTH_NORM = {
    'mei': 'May', 'agu': 'Aug', 'okt': 'Oct', 'des': 'Dec',
    'januari': 'January', 'februari': 'February', 'maret': 'March',
    'juni': 'June', 'juli': 'July', 'agustus': 'August',
    'oktober': 'October', 'desember': 'December',
    'sekarang': 'Present',
}


def parse_pdf(file_obj):
    """Extract text from LinkedIn PDF then parse it."""
    text = _extract_pdf_text(file_obj)
    return parse_text(text)


def parse_text(raw_text):
    """Parse plain text (from PDF extraction or clipboard paste) into CV dict."""
    lines = [l.rstrip() for l in raw_text.splitlines()]
    lines = [l for l in lines if l.strip()]

    sections = _split_into_sections(lines)
    result = _build_result(sections)
    return result


# ── PDF TEXT EXTRACTION ───────────────────────────────────────────────────────
def _extract_pdf_text(file_obj):
    # Try pdfplumber first (better layout handling), fall back to pypdf
    try:
        import pdfplumber
        with pdfplumber.open(file_obj) as pdf:
            return '\n'.join(page.extract_text() or '' for page in pdf.pages)
    except ImportError:
        pass

    try:
        from pypdf import PdfReader
        reader = PdfReader(file_obj)
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    except ImportError:
        pass

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file_obj)
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    except ImportError:
        raise RuntimeError(
            'Tidak ada library PDF yang terinstall. '
            'Jalankan: pip install pypdf'
        )


# ── SECTION SPLITTING ─────────────────────────────────────────────────────────
def _is_section_header(line):
    """Return section key if line is a section header, else None."""
    stripped = line.strip().lower().rstrip(':').strip()
    for key, keywords in SECTION_MAP.items():
        if stripped in keywords:
            return key
    return None


def _split_into_sections(lines):
    sections = {'header': []}
    current = 'header'

    for line in lines:
        sec = _is_section_header(line)
        if sec:
            current = sec
            if current not in sections:
                sections[current] = []
        else:
            sections.setdefault(current, []).append(line)

    return sections


# ── BUILD RESULT ──────────────────────────────────────────────────────────────
def _build_result(sections):
    result = {
        'personal':       {},
        'summary':        '',
        'experience':     [],
        'education':      [],
        'skills':         [],
        'certifications': [],
        'projects':       [],
        'languages':      [],
        'skill_categories': {},
    }

    # Merge 'contact' section into header so email/phone are found correctly
    # (LinkedIn Indonesian PDF puts email/phone under "Hubungi" label)
    header_lines = sections.get('header', []) + sections.get('contact', [])
    _parse_header(header_lines, result)
    _parse_summary(sections.get('summary', []), result)
    _parse_experience(sections.get('experience', []), result)
    _parse_education(sections.get('education', []), result)
    _parse_skills(sections.get('skills', []), result)
    _parse_certifications(sections.get('certifications', []), result)
    _parse_languages(sections.get('languages', []), result)
    _parse_projects(sections.get('projects', []), result)

    return result


# ── HEADER (name, contact) ────────────────────────────────────────────────────
def _parse_header(lines, result):
    personal = {'name': '', 'email': '', 'phone': '', 'location': '', 'linkedin': '', 'website': ''}

    all_text = '\n'.join(lines)

    # Email
    m = EMAIL_RE.search(all_text)
    if m:
        personal['email'] = m.group()

    # Phone
    for m in PHONE_RE.finditer(all_text):
        candidate = m.group().strip()
        if len(re.sub(r'\D', '', candidate)) >= 7:
            personal['phone'] = candidate
            break

    # LinkedIn URL
    li_label = re.search(r'\(LinkedIn\)', all_text, re.I)
    if li_label:
        before = all_text[:li_label.start()]
        base = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/', before, re.I)
        if base:
            slug_raw = before[base.end():]
            slug = re.sub(r'\s+', '', slug_raw).strip('-').strip('/')
            if slug:
                personal['linkedin'] = f'https://www.linkedin.com/in/{slug}'
    if not personal['linkedin']:
        joined = ' '.join(l.strip() for l in lines)
        li_m = re.search(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([\w][\w\s\-]*?)(?=\s{2,}|\s*\(|\s*$)',
            joined, re.I
        )
        if li_m:
            slug = re.sub(r'\s+', '', li_m.group(1)).strip('-')
            if slug:
                personal['linkedin'] = f'https://www.linkedin.com/in/{slug}'
    if not personal['linkedin']:
        for m in URL_RE.finditer(all_text):
            url = m.group()
            if 'linkedin.com/in/' in url.lower():
                personal['linkedin'] = url
                break

    # Name heuristic: first non-empty line that is NOT a section keyword,
    # NOT an email/URL/phone, and looks like a proper name
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if _is_section_header(line):
            continue
        if EMAIL_RE.search(line) or URL_RE.search(line) or PHONE_RE.search(line):
            continue
        if len(line.split()) <= 5 and re.match(r'^[A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Ö][a-zà-öA-ZÀ-Ö\.\-]+){0,4}$', line):
            personal['name'] = line
            break

    # Location: short line with city/country pattern
    for line in lines:
        line = line.strip()
        if personal['name'] and line == personal['name']:
            continue
        if EMAIL_RE.search(line) or PHONE_RE.search(line) or URL_RE.search(line):
            continue
        if 1 <= len(line.split()) <= 5 and re.match(r'^[A-ZÀ-Öa-zà-ö][^\d@]+$', line):
            if _is_section_header(line):
                continue
            # Skip job-title-like lines
            if any(w in line.lower() for w in [
                'engineer', 'manager', 'developer', 'analyst', 'designer',
                'officer', 'director', 'lead', 'head', 'chief', 'specialist',
                'consultant', 'architect', 'scientist', 'intern', 'coordinator',
                'pengembang', 'manajer', 'analis', 'insinyur', 'kepala',
            ]):
                continue
            personal['location'] = line
            break

    result['personal'] = personal


# ── SUMMARY ───────────────────────────────────────────────────────────────────
def _parse_summary(lines, result):
    result['summary'] = ' '.join(l.strip() for l in lines if l.strip())


# Kata kerja yang menandakan bullet point, bukan jabatan
_ACTION_VERBS = {
    # Indonesia
    'memimpin', 'meningkatkan', 'mengembangkan', 'membangun', 'merancang',
    'mengelola', 'memastikan', 'melakukan', 'mengimplementasikan', 'membuat',
    'menyusun', 'merencanakan', 'menganalisis', 'menyelesaikan', 'memperbaiki',
    'berkolaborasi', 'bertanggung', 'mencapai', 'menurunkan', 'mengurangi',
    # English
    'led', 'built', 'improved', 'managed', 'developed', 'designed',
    'implemented', 'created', 'reduced', 'increased', 'launched', 'delivered',
    'collaborated', 'mentored', 'spearheaded', 'streamlined', 'oversaw',
    'maintained', 'deployed', 'architected', 'optimized', 'integrated',
}


def _looks_like_job_title(line):
    """True if line could be a job title (for lookahead confirmation)."""
    if EMAIL_RE.search(line) or URL_RE.search(line):
        return False
    if DATE_RANGE_RE.search(line):
        return False
    if _is_section_header(line):
        return False
    if not line[0].isupper():
        return False
    words = line.split()
    if not (1 <= len(words) <= 8):
        return False
    if line[0].lower() in "'\"":
        return False
    if words[0].lower() in _ACTION_VERBS:
        return False
    if re.search(r'\d+%', line):
        return False
    if re.search(r'\b\d+\b', line) and not re.search(r'\b(19|20)\d{2}\b', line):
        return False
    return True


def _is_confirmed_title(line, lines, i):
    """Job title confirmed jika dalam 4 baris berikutnya ada date range atau tahun."""
    for j in range(i + 1, min(i + 5, len(lines))):
        l = lines[j].strip()
        if DATE_RANGE_RE.search(l) or (YEAR_RE.search(l) and len(l.split()) <= 6):
            return True
        if _is_section_header(l):
            return False
    return False


# ── EXPERIENCE ────────────────────────────────────────────────────────────────
def _parse_experience(lines, result):
    """
    LinkedIn PDF experience block pattern:
      [Job Title]           ← confirmed by date within next 4 lines
      [Company] · [type]
      [StartDate] – [EndDate]
      [Location]
      [description / bullets...]
    """
    entries = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if not (_looks_like_job_title(line) and _is_confirmed_title(line, lines, i)):
            i += 1
            continue

        entry = {
            'title': line,
            'company': '', 'location': '',
            'start_date': '', 'end_date': '',
            'current': False, 'bullets': [],
        }
        i += 1

        # Company
        if i < len(lines) and lines[i].strip():
            company_line = lines[i].strip()
            company_line = re.sub(
                r'\s*·\s*(Full-time|Part-time|Contract|Freelance|Internship|Volunteer|Magang)\s*',
                '', company_line, flags=re.I
            )
            if not DATE_RANGE_RE.search(company_line):
                entry['company'] = company_line.strip()
                i += 1

        # Date range
        if i < len(lines):
            date_m = DATE_RANGE_RE.search(lines[i])
            if date_m:
                entry['start_date'] = _clean_date(date_m.group(1).strip())
                entry['end_date']   = _clean_date(date_m.group(2).strip())
                entry['current']    = bool(re.search(r'present|now|sekarang', date_m.group(2), re.I))
                i += 1

        # Location (pendek, bukan date, bukan title yang punya date lagi)
        if i < len(lines):
            loc_line = lines[i].strip()
            is_short = 1 <= len(loc_line.split()) <= 5
            has_no_date = not DATE_RANGE_RE.search(loc_line)
            has_no_email = not EMAIL_RE.search(loc_line)
            is_not_section = not _is_section_header(loc_line)
            is_not_next_title = not (_looks_like_job_title(loc_line) and _is_confirmed_title(loc_line, lines, i))
            if is_short and has_no_date and has_no_email and is_not_section and is_not_next_title:
                entry['location'] = loc_line
                i += 1

        # Bullets — sampai baris kosong, section header, atau title baru yang confirmed
        while i < len(lines):
            desc_line = lines[i].strip()
            if not desc_line:
                i += 1
                break
            if _is_section_header(desc_line):
                break
            if _looks_like_job_title(desc_line) and _is_confirmed_title(desc_line, lines, i):
                break
            if len(desc_line) > 5:
                bullet = re.sub(r'^[•\-\*•‣◦⁃]+\s*', '', desc_line)
                entry['bullets'].append(bullet)
            i += 1

        entries.append(entry)

    result['experience'] = entries


# ── EDUCATION ─────────────────────────────────────────────────────────────────
def _parse_education(lines, result):
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line[0].isupper() and not DATE_RANGE_RE.search(line) and not _is_section_header(line):
            entry = {'school': line, 'degree': '', 'field': '', 'start_date': '', 'end_date': '', 'gpa': '', 'activities': ''}
            i += 1

            if i < len(lines) and lines[i].strip():
                degree_line = lines[i].strip()
                if not DATE_RANGE_RE.search(degree_line):
                    parts = re.split(r'\s*[·,]\s*', degree_line, maxsplit=1)
                    entry['degree'] = parts[0].strip()
                    if len(parts) > 1:
                        entry['field'] = parts[1].strip()
                    i += 1

            if i < len(lines):
                date_m = DATE_RANGE_RE.search(lines[i]) or re.search(r'(\d{4})\s*[–\-]\s*(\d{4}|Present)', lines[i], re.I)
                if date_m:
                    entry['start_date'] = date_m.group(1).strip()
                    entry['end_date']   = date_m.group(2).strip()
                    i += 1

            if i < len(lines):
                gpa_m = re.search(r'GPA[:\s]+(\d[\d.]+)', lines[i], re.I)
                if gpa_m:
                    entry['gpa'] = gpa_m.group(1)
                    i += 1

            entries.append(entry)
        else:
            i += 1

    result['education'] = entries


# ── SKILLS ────────────────────────────────────────────────────────────────────
def _parse_skills(lines, result):
    skills = []
    for line in lines:
        for skill in re.split(r'[,\n•]', line):
            skill = skill.strip().strip('·').strip()
            if skill and 1 <= len(skill.split()) <= 5 and len(skill) > 1:
                skills.append(skill)
    result['skills'] = list(dict.fromkeys(skills))


# ── CERTIFICATIONS ────────────────────────────────────────────────────────────
_DATE_ONLY_RE = re.compile(r'^(?:[A-Z][a-z]+ \d{4}|\d{4})$', re.I)

def _parse_certifications(lines, result):
    certs = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or _is_section_header(line):
            i += 1
            continue

        cert = {'name': line, 'authority': '', 'date': ''}
        i += 1

        if i < len(lines) and lines[i].strip():
            nxt = lines[i].strip()
            if _DATE_ONLY_RE.match(nxt):
                cert['date'] = nxt
                i += 1
            elif not DATE_RANGE_RE.search(nxt) and len(nxt.split()) <= 6 and not _is_section_header(nxt):
                cert['authority'] = nxt
                i += 1
                if i < len(lines) and lines[i].strip():
                    date_line = lines[i].strip()
                    if _DATE_ONLY_RE.match(date_line) or re.search(r'(?:Issued|Dikeluarkan)', date_line, re.I):
                        cert['date'] = re.sub(r'(?:Issued|Dikeluarkan)[:\s]*', '', date_line, flags=re.I).strip()
                        i += 1

        certs.append(cert)
    result['certifications'] = certs


# ── LANGUAGES ─────────────────────────────────────────────────────────────────
def _parse_languages(lines, result):
    langs = []
    PROFICIENCY_LEVELS = ['native', 'fluent', 'professional', 'intermediate', 'basic',
                          'elementary', 'limited working', 'full professional', 'penutur asli']
    for line in lines:
        line = line.strip()
        if not line:
            continue
        proficiency = ''
        for level in PROFICIENCY_LEVELS:
            if level in line.lower():
                proficiency = level.title()
                line = re.sub(level, '', line, flags=re.I).strip().strip('()·-').strip()
                break
        if line:
            langs.append({'name': line, 'proficiency': proficiency})
    result['languages'] = langs


# ── PROJECTS ──────────────────────────────────────────────────────────────────
def _parse_projects(lines, result):
    projects = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line and line[0].isupper() and not _is_section_header(line):
            proj = {'name': line, 'technologies': '', 'description': ''}
            i += 1
            desc_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip()[0].isupper():
                desc_lines.append(lines[i].strip())
                i += 1
            proj['description'] = ' '.join(desc_lines)
            projects.append(proj)
        else:
            i += 1
    result['projects'] = projects


# ── HELPERS ───────────────────────────────────────────────────────────────────
def _clean_date(date_str):
    date_str = date_str.strip()
    # Remove duration suffixes: "· 2 thn 5 bln" or "2 yrs 3 mos"
    date_str = re.sub(r'\s*·?\s*\d+\s+(?:yrs?|thn|tahun).*$', '', date_str, flags=re.I).strip()
    date_str = re.sub(r'\s*·?\s*\d+\s+(?:mos?|bln|bulan).*$', '', date_str, flags=re.I).strip()
    # Normalize Indonesian month names to English
    for id_m, en_m in _MONTH_NORM.items():
        date_str = re.sub(r'\b' + re.escape(id_m) + r'\b', en_m, date_str, flags=re.I)
    return date_str.strip()
