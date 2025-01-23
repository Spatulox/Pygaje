import copy

variables = [{}]
functions = {}
classDict = []
scope = 0


def evalPerso(tupleVar):
    global scope

    if isinstance(tupleVar, (int, float)):
        return tupleVar

    if isinstance(tupleVar, list):
        return tupleVar

    if isinstance(tupleVar, str):

        for current_scope in reversed(variables):
            if tupleVar in current_scope:
                return current_scope[tupleVar]

            if not '"' in tupleVar:
                print("erreur")
                exit(1)
        return ("string", tupleVar)

    # print(tupleVar)
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

        case 'string':
            value = tupleVar[1][1:-1]
            return value

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
            evalPerso(tupleVar[1])
            while evalPerso(tupleVar[2]):
                scope += 1
                result = evalPerso(tupleVar[4])
                check = checkBreakReturn(result)
                scope -= 1
                if check:
                    if check[0] == "break":
                        break
                    elif check[0] == "continue":
                        continue
                    elif check[0] == "return":
                        return check
                evalPerso(tupleVar[3])

        case 'block':
            for statement in tupleVar[1:]:
                result = evalPerso(statement)
                check = checkBreakReturn(result)
                if check:
                    return check

        case "=":
            returnValue = evalPerso(tupleVar[2])
            variables[-1][tupleVar[1]] = returnValue

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

        case 'class_declaration':
            if tupleVar[1] in classDict:
                print("This class is already declared")
                exit(1)
            classDict.append(save_declaration_class(tupleVar))
            constructor = detect_constructor(tupleVar)
            if constructor:
                evalPerso((constructor[0], constructor, tupleVar[1]))

        # case 'class_declaration_extend':
        #     if tupleVar[1] in classDict:
        #         print("This extend class is already declared")
        #         exit(1)
        #     classDict[tupleVar[1]] = (tupleVar[1])

        case 'class_constructor':
            constructor = tupleVar[1]
            name = tupleVar[2]
            classDictFound = find_dict_in_list(classDict, name)
            if not classDictFound:
                print("Can't use a dict outside a class")
                exit(1)
            classDictFound["constructor"] = constructor

        case 'class_new':
            classDictFound = find_dict_in_list(classDict, tupleVar[1])
            if not classDictFound:
                print(f"Class ${tupleVar[1]} not declared, or declare it before using it")
                exit(1)

            classReturn = None
            if len(tupleVar[2]) > 0:
                classReturn = executeConstructor(copy.deepcopy(classDictFound), tupleVar[1], tupleVar[2])
            return classReturn

        case 'class_access':
            var = evalPerso(tupleVar[1])
            class_name = list(var[1].keys())[0]

            if tupleVar[2] in var[1][class_name].keys():
                return var[1][class_name][tupleVar[2]]
            print("This attribute doesn't exist in this class")
            exit(1)

        case 'class':
            print("CLASS")
            print(tupleVar)
            print("ON EST PASSÉ LA, JE SAIS PAS QUOI EN FAIRE")
            exit(1)

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
            exit()

        case 'debug':
            print(variables)
            print(functions)
            print(classDict)


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