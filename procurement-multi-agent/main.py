import asyncio

from supervisor import ProcurementSupervisor
from agents import model_client


async def on_purchase_request_received(purchase_request):

    supervisor = ProcurementSupervisor()

    result = await supervisor.process_request(
        purchase_request
    )

    print("\n========== Final Decision ==========")
    print(result)


async def main():

    # Simulating an event
    purchase_request = """
    We need to purchase 20 Dell laptops
    for the new engineering team.
    """

    await on_purchase_request_received(
        purchase_request
    )

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())