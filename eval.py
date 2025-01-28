import copy

from ply import yacc

variables = [{}]
functions = {}
classDict = []
scope = 0
definingParentClass = False


def evalPerso(tupleVar):
    global scope, definingParentClass

    if isinstance(tupleVar, (int, float)):
        return tupleVar

    if isinstance(tupleVar, list):
        return tupleVar

    if isinstance(tupleVar, str):

        if definingParentClass:
            # Limite la recherche aux deux derniers éléments
            scopes_to_search = variables[-2:] if len(variables) > 1 else variables
        else:
            scopes_to_search = variables

        for current_scope in reversed(scopes_to_search):
            if tupleVar in current_scope:
                return current_scope[tupleVar]
        if not '"' in tupleVar:
            if definingParentClass:
                print(f"Variable '{tupleVar}' isn't declared in the class or in the parent class")
                exit(1)
            print(f"Variable '{tupleVar}' isn't declared")
            exit(1)
        return ("string", tupleVar)

    # print(tupleVar)
    match (tupleVar[0]):

        # -------------------- Calcul --------------------

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

        # -------------------- Conditions --------------------

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

        # -------------------- Boucles --------------------

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

        # -------------------- Tableau --------------------

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

        # -------------------- Classes --------------------

        case 'class_declaration':
            if tupleVar[1] in classDict:
                print("This class is already declared")
                exit(1)
            classDict.append(save_declaration_class(tupleVar))
            constructor = detect_constructor(tupleVar)
            if constructor:
                evalPerso((constructor[0], constructor, tupleVar[1]))

        case 'class_declaration_extend':
            if tupleVar[1] in classDict:
                print("This extend class is already declared")
                exit(1)

            newTuple = (tupleVar[0], tupleVar[1], tupleVar[3])
            dictPerso = save_declaration_class(newTuple)
            dictPerso["extend"] = tupleVar[2]
            classDict.append(dictPerso)

            # Copie function from parent class to child class
            theClass = find_dict_in_list(classDict, tupleVar[1])
            theClassToAppend = find_dict_in_list(classDict, tupleVar[2])
            key = list(theClass.keys())[0]
            keyOfClassToAppend = list(theClassToAppend.keys())
            for key_b in keyOfClassToAppend:
                theClass[key][1].append(theClassToAppend[key_b])

            # On evalue le constructeur pour remplacer les variables, etc..
            constructor = detect_constructor(newTuple)
            if constructor:
                evalPerso((constructor[0], constructor, tupleVar[1]))

        case 'class_constructor':
            constructor = tupleVar[1]
            name = tupleVar[2]
            classDictFound = find_dict_in_list(classDict, name)
            if not classDictFound:
                print("Can't use a dict outside a class")
                exit(1)
            classDictFound["constructor"] = constructor

        case 'class_new':

            className = tupleVar[1]
            args = tupleVar[2]
            classDictFound = find_dict_in_list(classDict, className)
            if not classDictFound:
                print(f"Class {className} not declared, or declare it before using it")
                exit(1)

            classReturn = None

            parent = classDictFound.get("extend")
            varParent = None
            if parent:
                definingParentClass = True
                classParentDictFound = find_dict_in_list(classDict, parent)
                if classParentDictFound:
                    classReturn = executeConstructor(copy.deepcopy(classParentDictFound), parent, args)
                else:
                    print("NO CONSTRUCTOR")
                varParent = classReturn[1].get(parent)

                enterScope()
                for var in varParent:
                    variables[-1][var] = varParent[var]

            if len(tupleVar[2]) > 0:
                classReturn = executeConstructor(copy.deepcopy(classDictFound), className, args)

            if parent:
                # Enregistre les variables "parent" dans l'endroit des variable de la classe enfant, SAUF si elles existe déjà
                child_vars = classReturn[1].get(className)

                for var, value in varParent.items():
                    if var not in child_vars:
                        child_vars[var] = value
                classReturn[1][className] = child_vars
                exitScope()
                definingParentClass = False

            return classReturn

        case 'class_access':
            var = evalPerso(tupleVar[1])
            class_name = list(var[1].keys())[0]
            if not isinstance(tupleVar[2], tuple) and tupleVar[2] in var[1][class_name].keys():
                return var[1][class_name][tupleVar[2]]
            elif isinstance(tupleVar[2], tuple):
                result = evalPerso(("call", tupleVar[2][1], tupleVar[2][2], tupleVar[1]))
                check = checkBreakReturn(result)
                if check:
                    return check
                return result
            print("This attribute doesn't exist in this class")
            exit(1)

        case 'class':
            print("CLASS")
            print(tupleVar)
            print("ON EST PASSÉ LA, JE SAIS PAS QUOI EN FAIRE")
            exit(1)

        # -------------------- Fonctions --------------------

        case 'function':
            if tupleVar[1] not in functions: #and tupleVar[1] not in list(find_dict_in_list(variables, tupleVar[1]).keys()):
                functions[tupleVar[1]] = (tupleVar[2], tupleVar[3])
                return f"Function {tupleVar[1]} defined."
            elif find_dict_in_list(variables, tupleVar[1]):
                print(f"A variable have the same name as the function '{tupleVar[1]}'")
                exit()
            else:
                print(f"Function {tupleVar[1]} already defined.")
                exit()

        case 'call':
            enterScope()
            params, body = 0, 0
            theClass, key = 0, 0
            if tupleVar[1] not in functions and len(tupleVar) == 3:
                print(f"Function {tupleVar[1]} is not defined.")
                exit(1)
            elif len(tupleVar) > 3:
                # par du dernier élément du tuple, pour retrouver la bonne méthode de classe correspondant
                theClass = evalPerso(tupleVar[3])[1]
                key = list(theClass.keys())[0]
                theFunction = find_dict_in_list(find_dict_in_list(classDict, key)[key][1], tupleVar[1])
                try:
                    params, body = theFunction[tupleVar[1]]
                except:
                    print(f"Function '{tupleVar[1]}' is not a method of the class '{key}'.")
                    exit(1)
                # Mise en scope des variables de la classe
                for var in theClass[key]:
                    variables[-1][var] = theClass[key][var]
            else:
                params, body = functions[tupleVar[1]]

            if len(params) != len(tupleVar[2]):
                print(f"Function {tupleVar[1]} expected {len(params)} arguments, got {len(tupleVar[2])}.")
                exit(1)

            for i in range(len(params)):
                if params[i] != []:
                    variables[-1][params[i]] = evalPerso(tupleVar[2][i])

            result = evalPerso(body)
            check = checkBreakReturn(result)

            # Si la fonction est une méthode de classe
            if len(tupleVar) > 3:
                for var in theClass[key]:
                    theClass[key][var] = variables[-1][var]
            exitScope()
            if check:
                while isinstance(check, tuple) and check and check[0] == "return":
                    if len(check) > 1:
                        check = check[1]
                    else:
                        check = None
                return check

        # -------------------- Fonctions prédéfinies --------------------

        case 'print':
            print(evalPerso(tupleVar[1]))
            return

        case 'len':
            return len(tupleVar[1])

        # -------------------- Statement particuliers --------------------

        case 'string':
            value = tupleVar[1]
            if '"' in value or "'" in value:
                value = tupleVar[1][1:-1]
            return value

        case 'import':
            s = evalPerso(evalPerso(tupleVar[1])) # renvoie un tuple, qu'après je reparsed pour renvoyer que la valeur du string

            if not s.startswith("./") and not s.startswith("../"):
                s = f'./{s}'
            if not s.endswith(".pj"):
                s += ".pj"
            try:
                with open(s, 'r') as f:
                    contenu = f.read()
                    parsed = yacc.parse(contenu)
                    evalPerso(parsed)
            except FileNotFoundError:
                print(f"Erreur : Le fichier '{s}' n'a pas été trouvé.")
                exit(1)
            except Exception as e:
                print(f"Erreur lors de l'importation de '{s}': {str(e)}")
                exit(1)

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


def find_dict_in_list(data, keyword):
    if isinstance(data, list):
        for item in data:
            result = find_dict_in_list(item, keyword)
            if result:
                return result
    elif isinstance(data, dict):
        if keyword in data:
            return data
    return None


def save_declaration_class(input_data):
    class_name = input_data[1]
    class_body = input_data[2][1:]  # Ignorer le premier élément 'block'

    internVariables = []
    functions = []

    def process_block(block):
        for item in block:
            if isinstance(item, tuple):
                if item[0] == 'function':
                    function_name = item[1]
                    function_params = item[2]
                    function_body = item[3]
                    functions.append({function_name: (function_params, function_body)})
                elif item[0] == 'block':
                    process_block(item[1:])
            elif isinstance(item, str):
                internVariables.append({item: None})

    process_block(class_body)

    return {class_name: [internVariables, functions]}


def executeConstructor(dict, name, args):
    constructor = dict.get("constructor")
    if not constructor or len(constructor) < 3:
        return ("class", {name: {}})

    constructor_params = constructor[1]
    constructor_body = constructor[2]

    enterScope()
    # Dictionnaire pour { param : valeur, param2 : valeur2}
    # Doit être fait car le "evalPerso()" va devoir faire des calculs avec le paramètre "param"

    if constructor_params != [[]] and args != [[]] :
        for param, arg in zip(constructor_params, args):
            variables[-1][param] = arg
    elif constructor_params == [[]] and args == [[]]:
        pass
    else:
        if len(constructor_params) != len(args):
            print("Le nomre d'argument attendu ne correspond pas au nombre d'argument donné")
            exit(1)
        print("Erreur de class inconnu")
        exit(1)

    if isinstance(constructor_body, tuple) and constructor_body[0] == 'block':
        for statement in constructor_body[1:]:
            evalPerso(statement)

    tmp = copy.deepcopy(variables[-1])

    # Les params du constructeur sont supprimé pour éviter d'avoir des fausses valeur et des trucs useless dans le dico
    for var, value in list(tmp.items()):
        if var in constructor_params:
            del tmp[var]

    exitScope()
    return ("class", {name: tmp})


def detect_constructor(input_data):
    def search_constructor(item):
        if isinstance(item, tuple):
            if item[0] == 'class_constructor':
                return item
            for sub_item in item:
                result = search_constructor(sub_item)
                if result:
                    return result
        return None

    return search_constructor(input_data)
