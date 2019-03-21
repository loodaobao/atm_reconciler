def test_reconciler(timing, statement):
    reco =Reconciler(statement)
    df = reco.get_balance()
    df.to_csv("balance.csv")
