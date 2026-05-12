"""APScheduler background job runner."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.utils.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def schedule_pipeline_run(cron_expr: str = "0 6 * * *") -> None:
    """Schedule daily pipeline run at 6am UTC by default."""
    from backend.core.graph import run_pipeline
    from backend.core.state import AgentState

    async def _daily_run():
        logger.info("Scheduler: starting daily pipeline run")
        initial: AgentState = {
            "raw_event_input": None, "excel_path": None, "email_content": None,
            "event": None, "hotels": [], "vendor_prices": {}, "competitor_prices": {},
            "approval": None, "scores": None, "report": None, "error": None, "step": "start",
        }
        result = await run_pipeline(initial)
        logger.info(f"Scheduler: pipeline complete — step={result.get('step')}, decision={result.get('approval', {}).get('decision')}")

    hour, minute = 6, 0
    scheduler.add_job(
        _daily_run,
        CronTrigger(hour=hour, minute=minute),
        id="daily_pipeline",
        replace_existing=True,
    )
    logger.info(f"Scheduler: daily pipeline job registered at {hour:02d}:{minute:02d} UTC")
