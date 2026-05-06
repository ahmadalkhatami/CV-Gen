"""
Auto-translation: Indonesian → English for CV content.
Uses deep-translator (Google Translate, no API key needed) when available.
Falls back gracefully with no error if translation library is missing.
"""
import re

# Common Indonesian words used to detect Indonesian text (particles + verbs)
_ID_MARKERS = {
    'dan', 'yang', 'dengan', 'untuk', 'dalam', 'adalah', 'tidak', 'ini',
    'dari', 'pada', 'akan', 'dapat', 'telah', 'saya', 'kami', 'mereka',
    'juga', 'sudah', 'sedang', 'lebih', 'bisa', 'harus', 'oleh', 'ke',
    'atau', 'memiliki', 'melakukan', 'mengembangkan', 'membangun',
    'mengelola', 'meningkatkan', 'berhasil', 'pengalaman', 'sekarang',
    'perusahaan', 'proyek', 'tim', 'sistem', 'aplikasi', 'layanan',
    'serta', 'atas', 'bahwa', 'agar', 'supaya', 'karena', 'ketika',
    'selama', 'sampai', 'antara', 'setelah', 'sebelum', 'melalui',
}

# Indonesian degree name → English
_DEGREE_MAP = [
    (r's\.?1\b',      "Bachelor's Degree"),
    (r's\.?2\b',      "Master's Degree"),
    (r's\.?3\b',      "Doctor of Philosophy"),
    (r'd\.?3\b',      "Diploma (D3)"),
    (r'd\.?4\b',      "Applied Bachelor's Degree"),
    (r'\bsarjana\b',  "Bachelor's Degree"),
    (r'\bmagister\b', "Master's Degree"),
    (r'\bdoktor\b',   "Doctor of Philosophy"),
    (r'\bdiploma\b',  "Diploma"),
    (r's\.kom\b',     "Bachelor of Computer Science"),
    (r'm\.kom\b',     "Master of Computer Science"),
    (r's\.t\.?\b',    "Bachelor of Engineering"),
    (r'm\.t\.?\b',    "Master of Engineering"),
    (r's\.si\b',      "Bachelor of Science"),
    (r'm\.si\b',      "Master of Science"),
]


def _is_indonesian(text):
    """Return True if text likely contains Indonesian (threshold: 2 marker words)."""
    if not text or len(text.strip()) < 8:
        return False
    words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    return len(words & _ID_MARKERS) >= 2


def _translate_one(text):
    """Translate text id→en using deep-translator. Returns original on error."""
    if not text or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source='id', target='en').translate(text)
        return result if result else text
    except Exception:
        return text


def _translate_degree(text):
    """Map Indonesian degree abbreviations to English standard names."""
    lower = text.lower().strip()
    for pattern, replacement in _DEGREE_MAP:
        if re.search(pattern, lower):
            return replacement
    # Fall through to machine translation
    return _translate_one(text)


def translate_cv_data(data):
    """
    Translate Indonesian content in parsed CV data to English.
    Language detection is done once on the full document.
    Company names and school names are intentionally NOT translated.
    Returns data (modified in-place).
    """
    if not data:
        return data

    # Build a representative sample to detect language on the full document
    sample_parts = [
        data.get('summary', ''),
        ' '.join(e.get('title', '') for e in data.get('experience', [])[:3]),
        ' '.join(b for e in data.get('experience', [])[:2]
                 for b in (e.get('bullets') or [])[:2]),
        ' '.join(e.get('field', '') for e in data.get('education', [])[:2]),
    ]
    sample = ' '.join(p for p in sample_parts if p)

    if not _is_indonesian(sample):
        return data  # Already English, skip all translation

    # Document is Indonesian — translate all content fields
    # (company names, school names, certification names are protected)

    if data.get('summary'):
        data['summary'] = _translate_one(data['summary'])

    for exp in data.get('experience', []):
        if exp.get('title'):
            exp['title'] = _translate_one(exp['title'])
        # exp['company'] intentionally skipped
        if exp.get('bullets'):
            exp['bullets'] = [_translate_one(b) for b in exp['bullets'] if b]

    for edu in data.get('education', []):
        if edu.get('degree'):
            degree_text = edu['degree']
            lower = degree_text.lower()
            matched = False
            for pattern, replacement in _DEGREE_MAP:
                m = re.search(pattern, lower)
                if m:
                    remaining = degree_text[m.end():].strip()
                    edu['degree'] = replacement
                    # If field not yet set, use the remaining part (e.g. "Teknik Informatika")
                    if remaining and not edu.get('field'):
                        edu['field'] = _translate_one(remaining)
                    matched = True
                    break
            if not matched:
                edu['degree'] = _translate_one(degree_text)
        if edu.get('field'):
            edu['field'] = _translate_one(edu['field'])
        if edu.get('activities'):
            edu['activities'] = _translate_one(edu['activities'])
        # edu['school'] intentionally skipped

    if data.get('skills'):
        data['skills'] = [_translate_one(s) for s in data['skills'] if s]

    for proj in data.get('projects', []):
        if proj.get('name'):
            proj['name'] = _translate_one(proj['name'])
        if proj.get('description'):
            proj['description'] = _translate_one(proj['description'])

    return data
