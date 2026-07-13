from crew.crew import customer_onboarding_crew


while True:
    name = input("Customer Name: ").strip()
    email = input("Customer Email: ").strip()
    company = input("Company Name: ").strip()

    if not name:
        print("Customer name cannot be empty.")
        continue

    if not email:
        print("Customer email cannot be empty.")
        continue

    if not company:
        print("Company name cannot be empty.")
        continue

    result = customer_onboarding_crew.kickoff(
        inputs={
            "customer": f"""
            Name: {name}
            Email: {email}
            Company: {company}
            """
        }
    )
    break

print(result)