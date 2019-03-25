from ATM import ATM
from Reconciler import Reconciler
from Statement import Statement


if __name__ == "__main__":
    reconciler = Reconciler()
    reconciler.save_records()
    reconciler.statement.save_records()
