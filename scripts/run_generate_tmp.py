from swiss_cv.generator import generate
generate(count=10, seed=123, out_dir="sample_out", validate_schema=True, schema_path="data/schemas/swiss_persona.schema.json")
print("Done.")
