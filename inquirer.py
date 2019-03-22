

from Reconciler import Reconciler

import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":

    print("Initiating Reconciler... Please wait...")
    reco = Reconciler()
    print("System is loaded!")
    while True:
        print("Enter a TID to get the summary, enter exit to exit the program.")
        tid = input()
        if tid == "exit":
            break
        else:
            reco.get_summary(tid)
