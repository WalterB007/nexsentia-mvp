from ..ingestion.outlook_client import OutlookClient
from ..ingestion.transformers import outlook_message_to_signal
from ..nlp.pipeline import process_signal
from ..storage.jsonl_repository import JsonlSignalRepository
from ..storage.ingestion_log import IngestionLogger


def run_ingestion(top: int = 50):
    repo = JsonlSignalRepository()
    logger = IngestionLogger()

    try:
        client = OutlookClient()
        messages = client.fetch_messages(top=top)

        print(f"[INFO] Messages fetched from Outlook: {len(messages)}")

        signals = [outlook_message_to_signal(m) for m in messages]
        enriched = [process_signal(s) for s in signals]

        saved_count = repo.save_signals(enriched)
        logger.log_run(
            source_system="Outlook",
            fetched_count=len(messages),
            saved_count=saved_count,
            status="success",
        )

        print(f"[INFO] Signals saved: {saved_count}")
        print("[INFO] Sample signals:")
        for sig in enriched[:5]:
            print("----")
            print(f"ID: {sig.signal_id}")
            print(f"Date: {sig.event_timestamp}")
            print(f"Title: {sig.title}")
            print(f"Store: {sig.store}")
            print(f"Risk topic: {sig.risk_topic}")
            print(f"Systems: {sig.systems_mentioned}")

    except Exception as e:
        logger.log_run(
            source_system="Outlook",
            fetched_count=0,
            saved_count=0,
            status="error",
            error=str(e),
        )
        raise


if __name__ == "__main__":
    run_ingestion(top=50)
