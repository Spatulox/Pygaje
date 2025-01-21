variable = {}
functions = {}

def evalPerso(tupleVar):
    #check tuplevar
    #print("tupleVar[0] =", tupleVar[0] if isinstance(tupleVar, tuple) else "Not a tuple")  # Affichage de tupleVar[0]

    if type(tupleVar) == int:
        return tupleVar

    if type(tupleVar) == str:
        if tupleVar in variable:
            return variable[tupleVar]
        return tupleVar

    match(tupleVar[0]):
        case '*':
            return evalPerso(tupleVar[1]) * evalPerso(tupleVar[2])
        case '^':
            return evalPerso(tupleVar[1]) ** evalPerso(tupleVar[2])
        case '/':
            tmpVar = evalPerso(tupleVar[2])
            if tmpVar == 0:
                print("No division by 0")
                exit()
            return evalPerso(tupleVar[1]) / evalPerso(tupleVar[2])
        case '-':
            return evalPerso(tupleVar[1]) - evalPerso(tupleVar[2])
        case '+':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])

        case '==' | '>=' | '>' | '<=' | '<' | '!=':
            #print(f"condition : {tupleVar[1]} {tupleVar[0]} {tupleVar[2]}")
            return eval(f"{evalPerso(tupleVar[1])} {tupleVar[0]} {evalPerso(tupleVar[2])}")

        case 'print':
            print(evalPerso(tupleVar[1]))
            return

        case 'if':
            if evalPerso(tupleVar[1]):
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                if check:
                    return check

        case 'if-else':
            if evalPerso(tupleVar[1]):
                result = evalPerso(tupleVar[2])
            else:
                result = evalPerso(tupleVar[3])
            check = checkBreakReturn(result)
            if check:
                return check

        case 'while':
            while evalPerso(tupleVar[1]):
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                if check:
                    if check[0] == "break":
                        break
                    elif check[0] == "continue":
                        continue
                    elif check[0] == "return":
                        return check

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

            return

        case 'return':
            print("RETURN")
            if len(tupleVar) > 1:
                return ("return", evalPerso(tupleVar[1]))
            else:
                return ("return",)

        case 'break':
            print("BREAK")
            return ("break",)

        case 'continue':
            print("CONTINUE")
            return ("continue",)

        case 'exit':
            print("EXIT")
            exit()


def checkBreakReturn(tmp):
    if isinstance(tmp, tuple):
        if tmp[0] == "return":
            if len(tmp) > 1:
                return ("return", tmp[1])
            else:
                return ("return", None)
        elif tmp[0] == "break":
            return ("break",)
        elif tmp[0] == "continue":
            return ("continue",)
    return None