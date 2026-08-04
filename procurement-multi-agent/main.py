import asyncio

from supervisor import ProcurementSupervisor
from agents import model_client

purchase_request = """
We need to purchase 20 Dell laptops for the new engineering team.
"""


async def main():

    supervisor = ProcurementSupervisor()

    final_result = await supervisor.process_request(
        purchase_request
    )

    print("\n========== Final Result ==========")
    print(final_result)

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())