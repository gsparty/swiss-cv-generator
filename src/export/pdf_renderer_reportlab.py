from swiss_cv.text_utils import normalize_for_output
name = normalize_for_output(name)
summary = normalize_for_output(summary)
c.setFont(DEFAULT_FONT if DEFAULT_FONT else "Helvetica", 12)
c.drawString(40, 800, name)
