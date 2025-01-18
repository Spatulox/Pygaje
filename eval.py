variable = {}
functions = {}

def evalPerso(tupleVar):
    #check tuplevar
    print("tupleVar[0] =", tupleVar[0] if isinstance(tupleVar, tuple) else "Not a tuple")  # Affichage de tupleVar[0]

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

        case 'function':

            if tupleVar[1] not in functions:
                functions[tupleVar[1]] = (tupleVar[2], tupleVar[3])
                print(functions)
                return f"Function {tupleVar[1]} defined."
            else:
                print( f"Function {tupleVar[1]} already defined.")
                exit()


        case 'call':

            if tupleVar[1] not in functions:
                raise Exception(f"Function {tupleVar[1]} is not defined.")

            params, body = functions[tupleVar[1]]
            if len(params) != len(tupleVar[2]):
                raise Exception(f"Function {tupleVar[1]} expected {len(params)} arguments, got {len(tupleVar[2])}.")

            old_vars = variable.copy()

            for param, arg in zip(params, tupleVar[2]):
                variable[param] = evalPerso(arg)

            result = evalPerso(body)

            variable.clear()
            variable.update(old_vars)

            return result

        case 'return':
            if len(tupleVar) > 1:
                return evalPerso(tupleVar[1])
            else:
                return


