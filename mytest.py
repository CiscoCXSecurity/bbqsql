from bbqsql.requester import LooseEquality

eq = LooseEquality()

eq.add_true(10)
eq.add_true(10)
eq.add_true(10)
eq.add_true(10)
eq.add_true(10)
eq.add_true(10)
eq.add_true(10)
eq.add_true(10)

print eq.trues
print eq.falses

eq.equals(10)
