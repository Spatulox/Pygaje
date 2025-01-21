variable = {}
functions = {}
scope = 0


def evalPerso(tupleVar):
    # check tuplevar
    # print("tupleVar[0] =", tupleVar[0] if isinstance(tupleVar, tuple) else "Not a tuple")  # Affichage de tupleVar[0]

    if type(tupleVar) == int:
        return tupleVar

    if type(tupleVar) == str:
        if tupleVar in variable:
            return variable[tupleVar]
        return tupleVar

    match (tupleVar[0]):
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
            for statement in tupleVar[1:]:
                result = evalPerso(statement)
                check = checkBreakReturn(result)
                if check:
                    return check

        case "=":
            variable[tupleVar[1]] = evalPerso(tupleVar[2])

        case 'function':

            if tupleVar[1] not in functions:
                functions[tupleVar[1]] = (tupleVar[2], tupleVar[3])

                return f"Function {tupleVar[1]} defined."
            else:
                print(f"Function {tupleVar[1]} already defined.")
                exit()

        case 'call':

            if tupleVar[1] not in functions:
                raise Exception(f"Function {tupleVar[1]} is not defined.")

            params, body = functions[tupleVar[1]]

            if len(params) != len(tupleVar[2]):
                raise Exception(f"Function {tupleVar[1]} expected {len(params)} arguments, got {len(tupleVar[2])}.")

            old_vars = variable.copy()

            for i in range(len(params)):
                variable[params[i]] = tupleVar[2][i]

            print(body)

            result = evalPerso(body)
            check = checkBreakReturn(result)
            if isinstance(check, tuple) and check:
                if check[0] == "return":
                    return check[1]
                elif check[0] == "break":
                    print("Warning: 'break' used outside of a loop in a function")
                    return None
                else:

                    print(f"Unexpected control flow: {check[0]}")
                    return None
            return result

        case 'return':
            if len(tupleVar) > 1:
                return evalPerso(tupleVar[1])
            else:
                return

def checkBreakReturn(tmp):
    if isinstance(tmp, tuple):
        if tmp[0] == "return":
            if len(tmp) > 1:
                return ("return", tmp[1])
            else:
                return ("return", None)
        elif tmp[0] == "break":
            return ("break",)
    return tmp