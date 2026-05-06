from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT
from io import BytesIO


THEMES = {
    'classic': {'primary': '#1E3A5F', 'accent': '#2563EB', 'muted': '#64748B'},
    'modern':  {'primary': '#111827', 'accent': '#7C3AED', 'muted': '#6B7280'},
    'minimal': {'primary': '#000000', 'accent': '#374151', 'muted': '#6B7280'},
    'executive': {'primary': '#1A1A1A', 'accent': '#B45309', 'muted': '#6B7280'},
}


class PDFGenerator:
    def generate(self, data):
        buffer = BytesIO()
        theme = THEMES.get(data.get('template', 'classic'), THEMES['classic'])
        primary = HexColor(theme['primary'])
        accent  = HexColor(theme['accent'])
        muted   = HexColor(theme['muted'])
        body_color = HexColor('#1F2937')
        divider_color = HexColor('#E5E7EB')

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1.8 * cm,
            rightMargin=1.8 * cm,
            topMargin=1.6 * cm,
            bottomMargin=1.6 * cm,
            title=data.get('personal', {}).get('name', 'CV'),
            author=data.get('personal', {}).get('name', ''),
            subject='Curriculum Vitae',
        )

        def style(name, **kwargs):
            defaults = dict(fontName='Helvetica', fontSize=9, textColor=body_color,
                            leading=13, spaceAfter=0, spaceBefore=0, alignment=TA_LEFT)
            defaults.update(kwargs)
            return ParagraphStyle(name, **defaults)

        s_name      = style('Name', fontName='Helvetica-Bold', fontSize=20, textColor=primary, leading=24, spaceAfter=3)
        s_contact   = style('Contact', fontSize=8.5, textColor=muted, leading=12, spaceAfter=1)
        s_section   = style('Section', fontName='Helvetica-Bold', fontSize=10, textColor=accent, spaceBefore=10, spaceAfter=3, leading=14)
        s_job_title = style('JobTitle', fontName='Helvetica-Bold', fontSize=9.5, textColor=primary, spaceAfter=1, leading=13)
        s_sub       = style('Sub', fontSize=8.5, textColor=muted, spaceAfter=2, leading=12)
        s_body      = style('Body', fontSize=9, leading=13, spaceAfter=2)
        s_bullet    = style('Bullet', fontSize=9, leading=13, leftIndent=10, spaceAfter=1)
        s_skills    = style('Skills', fontSize=9, leading=14, spaceAfter=2)

        def hr(thick=0.5, color=None):
            return HRFlowable(width='100%', thickness=thick, color=color or divider_color,
                              spaceAfter=4, spaceBefore=0, lineCap='round')

        def section_header(title):
            return [Paragraph(title.upper(), s_section), hr()]

        def bullet_para(text):
            return Paragraph(f'&#8226; {text.strip()}', s_bullet)

        story = []
        personal = data.get('personal', {})

        # ── HEADER ──────────────────────────────────────────────────
        story.append(Paragraph(personal.get('name', 'Nama Anda'), s_name))

        parts = []
        for key, label in [('email', None), ('phone', None), ('location', None)]:
            v = personal.get(key, '').strip()
            if v:
                parts.append(v)

        linkedin = personal.get('linkedin', '').strip()
        if linkedin:
            li = linkedin.replace('https://www.linkedin.com/in/', '').replace('https://linkedin.com/in/', '').strip('/')
            parts.append(f'linkedin.com/in/{li}')

        website = personal.get('website', '').strip()
        if website:
            parts.append(website)

        if parts:
            story.append(Paragraph(' &nbsp;|&nbsp; '.join(parts), s_contact))

        story.append(hr(thick=2, color=accent))

        # ── SUMMARY ─────────────────────────────────────────────────
        summary = data.get('summary', '').strip()
        if summary:
            story += section_header('Professional Summary')
            story.append(Paragraph(summary, s_body))

        # ── EXPERIENCE ──────────────────────────────────────────────
        experience = data.get('experience', [])
        if experience:
            story += section_header('Work Experience')
            for exp in experience:
                end = 'Present' if exp.get('current') else (exp.get('end_date') or 'Present')
                date_range = f"{exp.get('start_date', '')} – {end}".strip(' –')

                title_line = exp.get('title', '')
                if date_range:
                    title_line += f'<font color="#{theme["muted"][1:]}" size="8">  {date_range}</font>'
                story.append(Paragraph(title_line, s_job_title))

                company_line = exp.get('company', '')
                if exp.get('location'):
                    company_line += f" · {exp['location']}"
                if company_line:
                    story.append(Paragraph(company_line, s_sub))

                bullets = exp.get('bullets', [])
                if not bullets and exp.get('description'):
                    bullets = [exp['description']]

                for b in bullets:
                    if b.strip():
                        story.append(bullet_para(b))

                story.append(Spacer(1, 5))

        # ── EDUCATION ───────────────────────────────────────────────
        education = data.get('education', [])
        if education:
            story += section_header('Education')
            for edu in education:
                degree = edu.get('degree', '')
                if edu.get('field'):
                    degree += f" in {edu['field']}"

                start = edu.get('start_date', '')
                end   = edu.get('end_date', '')
                date_range = f'{start} – {end}'.strip(' –') if (start or end) else ''

                title_line = degree
                if date_range:
                    title_line += f'<font color="#{theme["muted"][1:]}" size="8">  {date_range}</font>'
                story.append(Paragraph(title_line, s_job_title))
                story.append(Paragraph(edu.get('school', ''), s_sub))

                if edu.get('gpa'):
                    story.append(Paragraph(f"GPA: {edu['gpa']}", s_body))
                if edu.get('activities'):
                    story.append(Paragraph(edu['activities'], s_body))

                story.append(Spacer(1, 5))

        # ── SKILLS ──────────────────────────────────────────────────
        skills = data.get('skills', [])
        skill_cats = data.get('skill_categories', {})
        if skills or skill_cats:
            story += section_header('Skills')
            if skill_cats:
                for cat, cat_skills in skill_cats.items():
                    if cat_skills:
                        line = f'<b>{cat}:</b> {" · ".join(cat_skills)}'
                        story.append(Paragraph(line, s_skills))
            else:
                chunks = [skills[i:i+8] for i in range(0, len(skills), 8)]
                for chunk in chunks:
                    story.append(Paragraph(' &nbsp;·&nbsp; '.join(chunk), s_skills))

        # ── CERTIFICATIONS ──────────────────────────────────────────
        certifications = data.get('certifications', [])
        if certifications:
            story += section_header('Certifications')
            for cert in certifications:
                line = cert.get('name', '')
                if cert.get('authority'):
                    line += f" – {cert['authority']}"
                if cert.get('date'):
                    line += f" ({cert['date']})"
                story.append(bullet_para(line))

        # ── PROJECTS ────────────────────────────────────────────────
        projects = data.get('projects', [])
        if projects:
            story += section_header('Projects')
            for proj in projects:
                story.append(Paragraph(f"<b>{proj.get('name', '')}</b>", s_job_title))
                if proj.get('technologies'):
                    story.append(Paragraph(proj['technologies'], s_sub))
                if proj.get('description'):
                    story.append(Paragraph(proj['description'], s_body))
                story.append(Spacer(1, 4))

        # ── LANGUAGES ───────────────────────────────────────────────
        languages = data.get('languages', [])
        if languages:
            story += section_header('Languages')
            lang_parts = []
            for lang in languages:
                part = lang.get('name', '')
                if lang.get('proficiency'):
                    part += f" ({lang['proficiency']})"
                if part:
                    lang_parts.append(part)
            story.append(Paragraph(' &nbsp;·&nbsp; '.join(lang_parts), s_skills))

        doc.build(story)
        buffer.seek(0)
        return buffer
