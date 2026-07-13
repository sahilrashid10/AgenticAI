from crewai import Crew, Process

from crew.tasks import (
    validation_task,
    database_task,
    email_task
)

from crew.agents import (
    validation_agent,
    database_agent,
    email_agent
)


customer_onboarding_crew = Crew(

    agents=[
        validation_agent,
        database_agent,
        email_agent
    ],

    tasks=[
        validation_task,
        database_task,
        email_task
    ],

    process=Process.sequential,

    verbose=True
)