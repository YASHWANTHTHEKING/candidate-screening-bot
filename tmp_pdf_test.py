import io
from backend.pdf_processor import extract_text_from_pdf, extract_resume_data

sample_pdf = b"%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R>>endobj\n2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1>>endobj\n3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n4 0 obj<< /Length 44>>stream\nBT /F1 24 Tf 50 150 Td (Name: John Doe\nEmail: john@doe.com\nSkills: Python, SQL\n5 years of experience) Tj ET\nendstream endobj\n5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000119 00000 n \n0000000200 00000 n \n0000000265 00000 n \ntrailer<< /Size 6 /Root 1 0 R >>\nstartxref\n337\n%%EOF"

print('Running PDF extraction test...')
text = extract_text_from_pdf(sample_pdf)
print('Extracted text:', repr(text))
print('Resume data:', extract_resume_data(text))
