from openai_client import client
p = {'first_name':'Anna','last_name':'Müller','title':'Software Engineer','years_experience':6,'industry':'technology','canton':'ZH'}
print('=== generate_summary (DE) ===')
print(client.generate_summary(p, language='de'))
print('=== generate_summary (FR) ===')
print(client.generate_summary(p, language='fr'))
