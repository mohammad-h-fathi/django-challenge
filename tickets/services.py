import datetime
import asyncio
import os
from threading import Thread
from asgiref.sync import sync_to_async
from .models import Ticket

# Time used to reserve a ticket, before payment expires
TICKET_RESERVE_TIME = int(os.getenv('TICKET_RESERVE_TIME') or 30)


@sync_to_async
def delete_holding_tickets():
    last_ticket_time = datetime.datetime.now() - datetime.timedelta(minutes=TICKET_RESERVE_TIME)
    Ticket.objects.filter(submit_date__lt=last_ticket_time, status=1).delete()


async def service_function():
    """
        This function
    :return:
    """
    while True:
        await delete_holding_tickets()
        await asyncio.sleep(TICKET_RESERVE_TIME * 45)


def thread_init():
    loop = asyncio.new_event_loop()
    loop.create_task(service_function())
    loop.run_forever()


def service_start():
    thread = Thread(target=thread_init)
    thread.start()
    # pass


