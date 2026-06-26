import time
import traceback
from datetime import datetime

import run_argos

MODE = "PAPER_ONLY"
REAL_ORDER = False
API_ORDER = False

LOOP_SECONDS = 3

run_count = 0
error_count = 0


def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")


def main():
    global run_count, error_count

    log("ARGOS STOCK AUTO LOOP START")
    log("MODE=PAPER_ONLY")
    log("REAL_ORDER=FALSE")
    log("API_ORDER=FALSE")
    log(f"LOOP_SECONDS={LOOP_SECONDS}")

    while True:
        try:
            run_count += 1
            log(f"RUN_START #{run_count}")

            run_argos.main()

            log(f"RUN_DONE #{run_count}")
            log(f"ERROR_COUNT={error_count}")

        except KeyboardInterrupt:
            log("AUTO_LOOP_STOPPED_BY_USER")
            break

        except Exception as e:
            error_count += 1
            log("ERROR_CAUGHT")
            log(f"ERROR_COUNT={error_count}")
            log(str(e))
            traceback.print_exc()

        time.sleep(LOOP_SECONDS)


if __name__ == "__main__":
    main()
