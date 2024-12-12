variable = {}

def evalPerso(tupleVar):
    if type(tupleVar) == int:
        return tupleVar

    if type(tupleVar) == str:
        if tupleVar in variable:
            return variable[tupleVar]
        return tupleVar

    print(tupleVar)
    match(tupleVar[0]):
        case '*':
            return evalPerso(tupleVar[1]) * evalPerso(tupleVar[2])
        case '/':
            return evalPerso(tupleVar[1]) / evalPerso(tupleVar[2])
        case '-':
            return evalPerso(tupleVar[1]) - evalPerso(tupleVar[2])
        case '+':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])

        case '==':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])
        case '>=':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])
        case '<=':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])
        case '!=':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])

        case 'print':
            print(evalPerso(tupleVar[1]))
            return

        case 'block':
            return evalPerso(tupleVar[1])

        case "=":
            variable[tupleVar[1]] = evalPerso(tupleVar[2])

