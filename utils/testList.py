list = [{"'1'": "'111'"}, {"'2'": "'222'"}, {"'3'": "'333'"}]

for i in list:
    i = str(i)
    i = i.replace("{", "")
    i = i.replace("}", "")
    i = i.replace("'", "", 4)
    i = i.replace("\"", "", 4)

    print(i)
    print(type(str(i)))


def testClass():
    print("this is my class")
