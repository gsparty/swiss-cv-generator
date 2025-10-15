from PyPDF2 import PdfReader
p = r'''C:\Projects\swiss-cv-generator\outputs\Stefan_Meier_3.pdf'''
r = PdfReader(p)
text = ''
for pg in r.pages:
    try:
        text += pg.extract_text() or ''
    except Exception:
        pass
print(text)