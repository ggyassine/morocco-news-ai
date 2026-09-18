import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from collector import collect
from config import INTERVAL_MINUTES


def job():
    items = collect()
    print(f"Collected {len(items)} new relevant items")


def start_dashboard():
    try:
        from dashboard import run_dashboard

        threading.Thread(
            target=run_dashboard,
            daemon=True
        ).start()

    except Exception as e:
        print("Dashboard disabled:", e)


if __name__ == "__main__":
    start_dashboard()

    job()

    scheduler = BlockingScheduler(
        timezone="Africa/Casablanca"
    )

    scheduler.add_job(
        job,
        "interval",
        minutes=INTERVAL_MINUTES,
        max_instances=1,
        coalesce=True
    )

    print(
        f"Running every {INTERVAL_MINUTES} minutes. "
        "Dashboard: http://localhost:8080"
    )

    scheduler.start()
