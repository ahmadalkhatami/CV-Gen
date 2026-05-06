from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/parse-linkedin', methods=['POST'])
def parse_linkedin():
    from utils.linkedin_parser import LinkedInParser
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diupload'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Tidak ada file yang dipilih'}), 400

    if not file.filename.lower().endswith('.zip'):
        return jsonify({'error': 'Harap upload file ZIP dari LinkedIn'}), 400

    try:
        parser = LinkedInParser()
        data = parser.parse_zip(file)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': f'Gagal memproses file LinkedIn: {str(e)}'}), 500


@app.route('/api/parse-linkedin-pdf', methods=['POST'])
def parse_linkedin_pdf():
    from utils.linkedin_text_parser import parse_pdf
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diupload'}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Harap upload file PDF dari LinkedIn'}), 400

    try:
        data = parse_pdf(file)
        from utils.translator import translate_cv_data
        data = translate_cv_data(data)
        return jsonify({'success': True, 'data': data})
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Gagal memproses PDF: {str(e)}'}), 500


@app.route('/api/parse-text', methods=['POST'])
def parse_text():
    from utils.linkedin_text_parser import parse_text as do_parse
    body = request.json
    if not body or not body.get('text', '').strip():
        return jsonify({'error': 'Tidak ada teks yang diberikan'}), 400

    try:
        data = do_parse(body['text'])
        from utils.translator import translate_cv_data
        data = translate_cv_data(data)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': f'Gagal memproses teks: {str(e)}'}), 500


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    from utils.pdf_generator import PDFGenerator
    data = request.json
    if not data:
        return jsonify({'error': 'Tidak ada data CV'}), 400

    try:
        generator = PDFGenerator()
        pdf_buffer = generator.generate(data)
        name = data.get('personal', {}).get('name', 'CV').replace(' ', '_')
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{name}_CV.pdf"
        )
    except Exception as e:
        return jsonify({'error': f'Gagal membuat PDF: {str(e)}'}), 500


@app.route('/api/generate-docx', methods=['POST'])
def generate_docx():
    from utils.docx_generator import DocxGenerator
    data = request.json
    if not data:
        return jsonify({'error': 'Tidak ada data CV'}), 400

    try:
        generator = DocxGenerator()
        docx_buffer = generator.generate(data)
        name = data.get('personal', {}).get('name', 'CV').replace(' ', '_')
        return send_file(
            docx_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f"{name}_CV.docx"
        )
    except Exception as e:
        return jsonify({'error': f'Gagal membuat DOCX: {str(e)}'}), 500


@app.route('/api/ats-check', methods=['POST'])
def ats_check():
    data = request.json
    if not data:
        return jsonify({'error': 'Tidak ada data'}), 400
    score, issues, tips = _check_ats_score(data)
    return jsonify({'score': score, 'issues': issues, 'tips': tips})


def _check_ats_score(data):
    score = 100
    issues = []
    tips = []

    personal = data.get('personal', {})

    if not personal.get('name', '').strip():
        score -= 10
        issues.append('Nama tidak ditemukan')
        tips.append('Tambahkan nama lengkap Anda')

    if not personal.get('email', '').strip():
        score -= 15
        issues.append('Email tidak ditemukan')
        tips.append('Tambahkan alamat email profesional')

    if not personal.get('phone', '').strip():
        score -= 10
        issues.append('Nomor telepon tidak ditemukan')
        tips.append('Tambahkan nomor telepon yang aktif')

    summary = data.get('summary', '').strip()
    if not summary:
        score -= 10
        issues.append('Professional Summary tidak ada')
        tips.append('Tambahkan ringkasan profesional 2-4 kalimat')
    elif len(summary.split()) < 25:
        score -= 5
        issues.append('Professional Summary terlalu singkat (kurang dari 25 kata)')
        tips.append('Perluas summary menjadi minimal 25 kata yang mendeskripsikan keahlian utama Anda')

    experience = data.get('experience', [])
    if not experience:
        score -= 20
        issues.append('Pengalaman kerja tidak ada')
        tips.append('Tambahkan minimal 1 pengalaman kerja')
    else:
        exp_without_bullets = [e for e in experience if len(e.get('bullets', [])) < 2]
        if exp_without_bullets:
            score -= 8
            company = exp_without_bullets[0].get('company', 'perusahaan pertama')
            issues.append(f'Deskripsi pekerjaan di {company} kurang detail')
            tips.append('Tambahkan minimal 2-3 bullet point per pengalaman kerja dengan pencapaian terukur')

    skills = data.get('skills', [])
    if not skills:
        score -= 15
        issues.append('Skills tidak ada')
        tips.append('Tambahkan minimal 5-10 keahlian teknis dan soft skills')
    elif len(skills) < 5:
        score -= 7
        issues.append(f'Hanya {len(skills)} skill yang terdaftar')
        tips.append('Tambahkan lebih banyak skills yang relevan dengan posisi yang dilamar')

    education = data.get('education', [])
    if not education:
        score -= 10
        issues.append('Riwayat pendidikan tidak ada')
        tips.append('Tambahkan riwayat pendidikan terakhir')

    return max(0, score), issues, tips


if __name__ == '__main__':
    print("=" * 50)
    print("  CV Generator - ATS Friendly")
    print("  Buka browser: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
