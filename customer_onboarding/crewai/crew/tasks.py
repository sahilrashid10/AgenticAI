from crewai import Task

from crew.agents import (
    validation_agent,
    database_agent,
    email_agent
)

validation_task = Task(

    description="""
    Validate the customer information.

    Customer:
    {customer}

    If validation fails, state exactly which field is wrong and why.
    If the customer is valid, say so clearly.
    """,

    expected_output="""
    Either a validation success message or a specific failure reason.
    """,

    agent=validation_agent
)

database_task = Task(

    description="""
    Check whether the customer already exists.

    Only proceed if validation passed.

    If validation failed, do not save anything and explain that the step was skipped.

    If not, save the customer.
    """,

    expected_output="""
    Customer already exists, customer successfully saved, or skipped because validation failed.
    """,

    agent=database_agent,

    # Meaning Before database starts, read the output of Validation. Because if validation fails, we don't want to check the database.
    context=[validation_task]
)

email_task = Task(

    description="""
    Generate

    1. Welcome email

    2. Internal onboarding checklist

    Only proceed if the customer passed validation and database processing completed.

    If validation failed, explain that email generation was skipped because the input was invalid.
    """,

    expected_output="""
    Professional welcome email and onboarding checklist, or a skipped message if validation failed.
    """,

    agent=email_agent,

    context=[database_task]
)
