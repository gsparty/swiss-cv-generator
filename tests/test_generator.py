from swiss_cv.generator_mvp import generate_persona
def test_generate_persona_basic():
    p = generate_persona(occupation="technology")
    assert p.first_name and p.last_name
    assert isinstance(p.age, int)
    assert p.summary and len(p.summary) > 5
