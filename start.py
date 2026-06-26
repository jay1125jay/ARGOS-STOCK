from engines.stock.run_mode import RunMode

def main():

    print("=" * 60)
    print("ARGOS STOCK")
    print("MODE : PAPER_ONLY")
    print("STATUS : START")
    print("=" * 60)

    RunMode().start()

if __name__ == "__main__":
    main()