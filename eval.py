import array

variable = {}
functions = {}

def evalPerso(tupleVar):

    if isinstance(tupleVar, (int, float)):
        return tupleVar

    if isinstance(tupleVar, list):
        return tupleVar

    if isinstance(tupleVar, str):
        if tupleVar in variable:
            return variable[tupleVar]
        return tupleVar

    #print("tupleVar[0] =", tupleVar[0] if isinstance(tupleVar, tuple) else "Not a tuple")

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
        case 'for':
            evalPerso(tupleVar[1])
            while evalPerso(tupleVar[2]):
                result = evalPerso(tupleVar[4])

                evalPerso(tupleVar[3])

                check = checkBreakReturn(result)
                if check:
                    if check[0] == "break":
                        break
                    elif check[0] == "continue":
                        continue
                    elif check[0] == "return":
                        return check

            #print(tupleVar)

        case 'block':
            for statement in tupleVar[1:]:
                result = evalPerso(statement)
                check = checkBreakReturn(result)
                if check:
                    return check

        case "=":
            variable[tupleVar[1]] = evalPerso(tupleVar[2])

        case 'array_access':
            return variable[tupleVar[1]][tupleVar[2]]

        case 'array_replace':
            variable[tupleVar[1]][tupleVar[2]] = evalPerso(tupleVar[3])

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
            # print(functions[tupleVar[1]])


            if len(params) != len(tupleVar[2]):
                raise Exception(f"Function {tupleVar[1]} expected {len(params)} arguments, got {len(tupleVar[2])}.")

            old_vars = variable.copy()

            # for param, arg in zip(params, tupleVar[2]):
            #     variable[param] = evalPerso(arg)

            if body[0] == "block":
                for stmt in body[1:]:  # Exécute chaque instruction du bloc
                    evalPerso(stmt)
            else:
                evalPerso(body)  # Si c'est une seule instruction, on l'exécute directement

            # print(body)
            result = evalPerso(body)
            print(result)

            variable.clear()
            variable.update(old_vars)

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