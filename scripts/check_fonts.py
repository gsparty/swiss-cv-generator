from PyPDF2 import PdfReader
r = PdfReader(r"outputs_fonttest/Luca_Bruno_1.pdf")
fonts = set()
for p in r.pages:
    res = p.get("/Resources")
    if res and "/Font" in res:
        fonts.update(res["/Font"].keys())
print("Fonts referenced:", fonts)
