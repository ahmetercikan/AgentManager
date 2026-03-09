
from generate_combined_reports import run_batch_reports
import sys

# Mock logger that prints to stdout with flush
def logger(msg):
    try:
        print(f"[FORCE_LOG] {msg}", flush=True)
    except:
        pass

if __name__ == "__main__":
    print("STARTING FORCE RUN SCRIPT...", flush=True)
    try:
        # Run ONLY for the target domain
        run_batch_reports(
            selected_domains=["Engagement Management & İş Geliştirme ve Satış"],
            # Ensure defaulting works or pass explicit
            start_date="2026-02-01",
            end_date="2026-02-28",
            report_month="Şubat 2026",
            month_en="Subat_2026",
            log_callback=logger
        )
        print("FORCE RUN COMPLETED.", flush=True)
    except Exception as e:
        print(f"FORCE RUN FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
