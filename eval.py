variables = [{}]  # Liste de dictionnaires représentant les différents niveaux de scope
functions = {}
scope = 0


def evalPerso(tupleVar):
    global scope

    if isinstance(tupleVar, (int, float)):
        return tupleVar

    if isinstance(tupleVar, list):
        return tupleVar

    if isinstance(tupleVar, str):
        # Rechercher la variable dans les scopes, du plus récent au plus ancien
        for current_scope in reversed(variables):
            if tupleVar in current_scope:
                return current_scope[tupleVar]
        return tupleVar  # Si la variable n'est pas trouvée, retourner son nom

    match (tupleVar[0]):
        case '*':
            return evalPerso(tupleVar[1]) * evalPerso(tupleVar[2])
        case '^':
            return evalPerso(tupleVar[1]) ** evalPerso(tupleVar[2])
        case '/':
            tmpVar = evalPerso(tupleVar[2])
            if tmpVar == 0:
                print("No division by 0")
                exit(1)
            return evalPerso(tupleVar[1]) / evalPerso(tupleVar[2])
        case '-':
            return evalPerso(tupleVar[1]) - evalPerso(tupleVar[2])
        case '+':
            return evalPerso(tupleVar[1]) + evalPerso(tupleVar[2])

        case '==' | '>=' | '>' | '<=' | '<' | '!=':
            left = evalPerso(tupleVar[1])
            right = evalPerso(tupleVar[2])
            op = tupleVar[0]
            if op == '==':
                return left == right
            elif op == '>=':
                return left >= right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '<':
                return left < right
            elif op == '!=':
                return left != right

        case 'print':
            print(evalPerso(tupleVar[1]))
            return

        case 'if':
            if evalPerso(tupleVar[1]):
                enterScope()
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                exitScope()
                if check:
                    return check

        case 'if-else':
            enterScope()
            if evalPerso(tupleVar[1]):
                result = evalPerso(tupleVar[2])
            else:
                result = evalPerso(tupleVar[3])
            check = checkBreakReturn(result)
            exitScope()
            if check:
                return check

        case 'while':
            while evalPerso(tupleVar[1]):
                scope += 1
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                scope -= 1
                if check:
                    if check[0] == "break":
                        break
                    elif check[0] == "continue":
                        continue
                    elif check[0] == "return":
                        return check

        case 'for':
            print(variables)
            evalPerso(tupleVar[1])  # Initialisation
            while evalPerso(tupleVar[2]):  # Condition
                scope += 1
                result = evalPerso(tupleVar[4])  # Corps de la boucle
                check = checkBreakReturn(result)
                scope -= 1
                if check:
                    if check[0] == "break":
                        break
                    elif check[0] == "continue":
                        continue
                    elif check[0] == "return":
                        return check
                evalPerso(tupleVar[3])  # Incrémentation

        case 'block':
            for statement in tupleVar[1:]:
                result = evalPerso(statement)
                check = checkBreakReturn(result)
                if check:
                    return check

        case "=":
            # Affecter la variable dans le scope actuel
            variables[-1][tupleVar[1]] = evalPerso(tupleVar[2])

        case 'array_access':
            array_name = tupleVar[1]
            index = tupleVar[2]
            for current_scope in reversed(variables):
                if array_name in current_scope:
                    return current_scope[array_name][index]

        case 'array_replace':
            array_name = tupleVar[1]
            index = tupleVar[2]
            value = evalPerso(tupleVar[3])
            for current_scope in reversed(variables):
                if array_name in current_scope:
                    current_scope[array_name][index] = value

        case 'function':
            if tupleVar[1] not in functions:
                functions[tupleVar[1]] = (tupleVar[2], tupleVar[3])
                return f"Function {tupleVar[1]} defined."
            else:
                print(f"Function {tupleVar[1]} already defined.")
                exit()

        case 'call':
            enterScope()
            if tupleVar[1] not in functions:
                print(f"Function {tupleVar[1]} is not defined.")
                exit(1)

            params, body = functions[tupleVar[1]]

            if len(params) != len(tupleVar[2]):
                print(f"Function {tupleVar[1]} expected {len(params)} arguments, got {len(tupleVar[2])}.")
                exit(1)

            for i in range(len(params)):
                variables[-1][params[i]] = evalPerso(tupleVar[2][i])

            result = evalPerso(body)
            check = checkBreakReturn(result)
            exitScope()
            if check:
                while isinstance(check, tuple) and check and check[0] == "return":
                    if len(check) > 1:
                        check = check[1]
                    else:
                        check = None
                return check

        case 'return':
            if len(tupleVar) > 1:
                return ("return", evalPerso(tupleVar[1]))
            else:
                return ("return",)

        case 'break':
            return ("break",)

        case 'continue':
            return ("continue",)

        case 'exit':
            print(variables)
            exit()


def enterScope():
    global variables, scope
    variables.append({})
    scope += 1


def exitScope():
    global variables, scope
    variables.pop()
    scope -= 1


def checkBreakReturn(tmp):
    if isinstance(tmp, tuple):
        if tmp[0] == "return":
            if len(tmp) > 1:
                return ("return", tmp[1])
            else:
                return ("return",)
        elif tmp[0] == "break":
            return ("break",)
        elif tmp[0] == "continue":
            return ("continue",)
    return None