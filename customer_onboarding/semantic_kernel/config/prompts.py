WELCOME_EMAIL_PROMPT = """
You are an onboarding assistant.

Write a professional welcome email for the following customer.

Customer Name: {name}
Company: {company}

Keep the email friendly, concise, and professional.
"""


TASK_PROMPT = """
You are an internal onboarding assistant.

Generate a short checklist for onboarding this customer.

Customer Name: {name}
Company: {company}

Return 4-5 concise tasks as bullet points.
"""