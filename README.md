# ATM Reconciler
This repository shows the implementation of ATM reconciliation.

An ATM, also known as "Automatic Telling Machine", if not operated and owned by the bank itself, is usually managed by an ATM solutions company. In this business model, the ATM solutions company buys and owns the machines, and then signs a tri-party agreement with a cash-in-transit (CIT) company and a bank, or a funding entity that provides the cash. A payment switch company will also be involved to facilitates the sending the money back to the funding entity.



## The Life Cycle of an ATM
The life cycle of a machine is based on 3 types of cash flows:

#### Cash Orders
The ATM solutions company orders a certain amount of cash to be deposited into a certain ATM. Money is sent from the funding entity to the CIT company, and the CIT company would in turn puts the money into the designated machine.

#### Withdrawals (switch payments)
When a customer visits the ATM and withdraws $100 dollars using an XYZ bank card. XYZ bank would reduce the balance of the customer and sends money to the payment switch company in order to pay it back to the funding entity, because the $100 bill withdrawn actually belongs to the funding entity. The payment switch company sits in the middle of the customer bank and funding entity to facilitate the returns of money.

#### Rebanks
Before the cash in a machine is completely depleted, the ATM solutions company would again send a cash order to the funding entity for more cash to be deposited. The funding entity sends the cash to the CIT and CIT visits the ATM again. However, there in the machines sits the remaining balance (previous cash order - total withdrawals). The CIT will take all the remaining balance out of the machine and puts the "new" cash order into the machine. The CIT company will then send the remaining balance back to the funding entity and tag the transfer with a transaction description "REBANK"


## Reconciliation Concept
For a funding entity, in order to track how much money is left in the machine, it needs to have complete information of the three cash components that make up the life cycle of an ATM. The easiest way to achieve this is to have all three types of cash flows centralized within one designated bank account and use the transaction references to identify the TID associated with each transaction and the "cash flow type" of the transaction.

The remaining balance of an ATM can be calculated at any time with the function below:

`Remaining Balance =  Cash Orders - Total Withdrawals - Rebanks`

This function gives the funding entity a cash-flow based balance of each ATM. However it might not be consistent with the actual balance that actually sits in the machine due to several situations:

* The delay of switch payments: there is a delay of 1-3 day(s) between the day on which a customer withdraws money from the machine and the day on which the funding entity received the payment from the payment switch company.

* Fat fingers: The rebanks sent to the funding entity from the CIT are done manually, and therefore the errors might occur when the staff of the CIT puts incorrect ATM reference codes in the reference.

* Unexpected behaviors of the ATM solutions company: Oftentimes the ATM solutions company might behave erratically and move the money from one ATM to the other without notifying the funding entity. It might also puts its own money into the machine when it sees fit and claim that the money returned to the funding entity actually belongs to the ATM solutions company.

Given the manual nature of this operation, errors abound and there is no way that a funding entity can know whether an error has indeed occurred. The reconciliation process only gives the funding entity a rough idea of how much is in the machine and with daily monitoring, it can identify potential faults when the balance based on cash flows shown on the bank statement is abnormally large or small.

## Reconciliation Algorithm

1. Clean up & fix the bank statement

```
read fixes_instructions from fixes_instructions.csv in AppData/, make all texts upper case
read new_statement from Data.csv in AppData/, make all texts upper case
read all_cash_orders from AppData/

breakdown the bulk transactions in new_statement into individual cash orders
with all_cash_orders

apply the fixes_instructions to new_statement




```

2. Calculate the balance of each ATM

```
for each ATM_SOLUTIONS_COMPANY:

    get the cleaned BANK_STATEMENT of the relevant account

    for each ATM_REFERENCE in the BANK_STATEMENT:
        TOTAL_CASH_ORDERS = sum of the debit balances for the ATM_REFERENCE
        TOTAL_CASH_RETURNS = sum of the credit balances for the ATM_REFERENCE
        BALANCE_IN_MACHINE = TOTAL_CASH_ORDERS - TOTAL_CASH_RETURNS

```

## /AppData/fixes.csv Specs

| Column Name     | Data Type       |
| ------------- |:-------------:|
|ITEM_NUM|Int|
|ATM_SOLUTIONS_COMPANY(0=ATMCO, 1=VENUE_SMART, 2=CASHPOINT|Int|
|ERROR_DATE|Date(mm/dd/yyyy)|
|ERROR_TYPE(1=CHANGE_DESCRIPTION, 2=TID_CHANGE, 3=INSERT_NEW_TRANSACTION, 4=DELETE_ROW)|Int|
|EXISTING_REFERENCE|Text|
|AMOUNT|Float|
|INSERTED_CREDIT_DEBIT (1=DEBIT, 2=CREDIT)|Int|
|INSERTED_REFERENCE|Text|
|OLD_TID|Text|
|NEW_TID|Text|
|COMMENT|Text|


<!-- ## Algorithm Toolbox
#### Big-O Notation
In computer science, big O notation is used to classify algorithms according to how their running time or space requirements grow as the input size grows. Click [here](https://tinyurl.com/y9tzg6sh) for the article I wrote to illustrate the basics of this concept.
#### Greedy Algorithm
The basic pattern of a greedy algorithm starts with picking a safe choice to tackle the problem, check that the safe choice works, repeat and solve smaller problems (sub-problem) with safe choices of the same concept and finish when there’s no smaller problem anymore. Click [here](https://tinyurl.com/y9twoym6) for the article I wrote to illustrate the greedy algorithm with simple toy problems.
#### Divide & Conquer
#### Dynamic Programming
## Data Structures
#### Stack
An abstract data type that allows adding and removing data on a Last-In-First-Out(LIFO) basis. It can be implemented with an array or linked-list.
#### Queue
#### Tree
#### Heap
#### Priority Queue
#### Hash Table -->
