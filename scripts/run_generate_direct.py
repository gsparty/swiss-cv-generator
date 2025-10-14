from swiss_cv.generator import generate
# generate(count, seed, out_dir, canton, industry, validate_schema, schema_path)
generate(
    count=50,
    seed=42,
    out_dir="swiss_tech_cvs",
    canton="ZH",
    industry="technology",
    validate_schema=True,
    schema_path="data/schemas/swiss_persona.schema.json"
)
print("Done.")
