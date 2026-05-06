import zipfile
import csv
import io
import re
from datetime import datetime


class LinkedInParser:
    """Parse LinkedIn data export ZIP file into CV data structure."""

    def parse_zip(self, file_obj):
        result = {
            'personal': {'name': '', 'email': '', 'phone': '', 'location': '', 'linkedin': '', 'website': ''},
            'summary': '',
            'experience': [],
            'education': [],
            'skills': [],
            'certifications': [],
            'projects': [],
            'languages': [],
        }

        with zipfile.ZipFile(file_obj, 'r') as zf:
            name_map = {n.lower(): n for n in zf.namelist()}

            self._parse_profile(zf, name_map, result)
            self._parse_email(zf, name_map, result)
            self._parse_positions(zf, name_map, result)
            self._parse_education(zf, name_map, result)
            self._parse_skills(zf, name_map, result)
            self._parse_certifications(zf, name_map, result)
            self._parse_languages(zf, name_map, result)
            self._parse_projects(zf, name_map, result)

        return result

    def _read_csv(self, zf, name_map, filename):
        if filename not in name_map:
            return []
        with zf.open(name_map[filename]) as f:
            content = f.read().decode('utf-8-sig')
        return list(csv.DictReader(io.StringIO(content)))

    def _parse_profile(self, zf, name_map, result):
        for fname in ['profile.csv']:
            rows = self._read_csv(zf, name_map, fname)
            for row in rows:
                result['personal'].update({
                    'name': f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip(),
                    'location': row.get('Geo Location', ''),
                    'linkedin': row.get('Public Profile Url', ''),
                })
                result['summary'] = row.get('Summary', '')
            break

    def _parse_email(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'email_addresses.csv')
        for row in rows:
            email = row.get('Email Address', '')
            if email and (row.get('Primary', '').lower() == 'yes' or not result['personal']['email']):
                result['personal']['email'] = email

    def _parse_positions(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'positions.csv')
        for row in rows:
            finished = row.get('Finished On', '').strip()
            exp = {
                'title': row.get('Title', ''),
                'company': row.get('Company Name', ''),
                'location': row.get('Location', ''),
                'start_date': self._format_date(row.get('Started On', '')),
                'end_date': self._format_date(finished) if finished else 'Present',
                'current': not bool(finished),
                'bullets': self._extract_bullets(row.get('Description', '')),
            }
            result['experience'].append(exp)

    def _parse_education(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'education.csv')
        for row in rows:
            edu = {
                'school': row.get('School Name', ''),
                'degree': row.get('Degree Name', ''),
                'field': row.get('Notes', ''),
                'start_date': row.get('Start Date', ''),
                'end_date': row.get('End Date', ''),
                'gpa': '',
                'activities': row.get('Activities and Societies', ''),
            }
            result['education'].append(edu)

    def _parse_skills(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'skills.csv')
        for row in rows:
            skill = row.get('Name', '').strip()
            if skill:
                result['skills'].append(skill)

    def _parse_certifications(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'certifications.csv')
        for row in rows:
            cert = {
                'name': row.get('Name', ''),
                'authority': row.get('Authority', ''),
                'date': self._format_date(row.get('Started On', '')),
            }
            if cert['name']:
                result['certifications'].append(cert)

    def _parse_languages(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'languages.csv')
        for row in rows:
            lang = {
                'name': row.get('Name', ''),
                'proficiency': row.get('Proficiency', ''),
            }
            if lang['name']:
                result['languages'].append(lang)

    def _parse_projects(self, zf, name_map, result):
        rows = self._read_csv(zf, name_map, 'projects.csv')
        for row in rows:
            proj = {
                'name': row.get('Title', ''),
                'technologies': '',
                'description': row.get('Description', ''),
                'url': row.get('Url', ''),
            }
            if proj['name']:
                result['projects'].append(proj)

    def _format_date(self, date_str):
        if not date_str:
            return ''
        date_str = date_str.strip()
        for fmt in ['%b %Y', '%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%b %Y')
            except ValueError:
                continue
        return date_str

    def _extract_bullets(self, description):
        if not description:
            return []
        lines = re.split(r'\n|(?<=[.!?])\s+(?=[A-Z•\-\*])', description)
        bullets = []
        for line in lines:
            line = re.sub(r'^[\s•\-\*\d\.]+', '', line).strip()
            if line and len(line) > 5:
                bullets.append(line)
        return bullets
