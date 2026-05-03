from services.orchestrator import Orchestrator
from asyncio import run
from config import SessionManager



async def main(cnt):
    session = await SessionManager.get_session()
    try:
        orchestrator = Orchestrator(session)
        await orchestrator.process_clients(cnt)
    finally:
        await SessionManager.close_session()

if __name__ == "__main__":
    count = int(input("Сколько персон обработать: "))
    run(main(int(count)))