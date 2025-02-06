import copy
from pydoc import replace

from ply import yacc

variables = [{}]
functions = {}
classDict = []
scope = 0
definingParentClass = False
dontCreateAnotherVar = False
whenRecursiveFunctionBegin = len(variables)
reference = {} # recursive function retun value
curr_ref = ""


def evalPerso(tupleVar):
    global scope, definingParentClass, dontCreateAnotherVar, whenRecursiveFunctionBegin, reference, curr_ref

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
        case '%':
            result = evalPerso(tupleVar[2])
            if result == 0:
                print("Error, Impossible to do a modulo by 0")
                exit(1)
            return evalPerso(tupleVar[1]) % result

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

        case 'if' | 'elif':
            if evalPerso(tupleVar[1]):
                enterScope()
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                exitScope()
                if check is not None:
                    return check
                return result
            else :
                if tupleVar[3] and isinstance(tupleVar[3], tuple):
                    return evalPerso(tupleVar[3])

        case 'else':
            enterScope()
            result = evalPerso(tupleVar[1])
            check = checkBreakReturn(result)
            exitScope()
            if check is not None:
                return check
            return result

        # -------------------- Boucles --------------------

        case 'while':
            while evalPerso(tupleVar[1]):
                scope += 1
                result = evalPerso(tupleVar[2])
                check = checkBreakReturn(result)
                scope -= 1
                if check is not None:
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
                if check is not None:
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
                if check is not None:
                    return check

        case "=":
            returnValue = evalPerso(tupleVar[2])
            var_name = tupleVar[1]

            # Evite aux variables d'être créer dans le scope actuel s'il elle existent déjà dans un scope parent, et qu'on veut les utiliser (ref de variables)
            if dontCreateAnotherVar:
                # Recherche une variable avant d'en créer une dans le scope actuel
                for variable in reversed(variables):
                    if var_name in variable:
                        variable[var_name] = returnValue
                        break
                else:# Si la variable n'existe dans aucun scope, la créer quand même
                    print(f"Warning: Variable '{var_name}' not found in any scope.")
                    variables[-1][var_name] = returnValue
            else:
                variables[-1][var_name] = returnValue

        # -------------------- Switch  --------------------

        case 'switch':
            value = evalPerso(tupleVar[1])
            case = tupleVar[2]
            while case != None:
                if(case[1] == value):
                    return evalPerso(case[2])
                elif case[3] and isinstance(case[3], tuple):
                    case = case[3]
            return None

        # -------------------- Tableau --------------------

        case 'array_access':
            array_name = tupleVar[1]
            index = evalPerso(tupleVar[2])
            for current_scope in reversed(variables):
                if array_name in current_scope:
                    return current_scope[array_name][index]

        case 'array_replace':
            array_name = tupleVar[1]
            index = evalPerso(tupleVar[2])
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
                if check is not None:
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
            if tupleVar[1] not in functions:
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
            params, body = get_function_params_and_body(tupleVar)
            args = tupleVar[2]
            validate_function_args(tupleVar[1], params, args)
            ref_params = setup_function_variables(params, args)

            is_recursive, parent = detect_recursion(body, tupleVar[1], None)
            result = None
            if is_recursive:

                whenRecursiveFunctionBegin = len(variables)
                # On "applati" le tuple pour en faire une liste de block, en supprimant le parent de l'appel récursif
                def flatten_and_extract_incr(body, function_name):
                    flattened = []
                    parent_calls = []
                    ref_counter = 0

                    def process_tuple(tup, parent=None):
                        nonlocal ref_counter
                        if isinstance(tup, tuple):
                            if tup[0] == 'block':
                                for item in tup[1:]:
                                    process_tuple(item, tup)
                            elif tup[0] == 'call':
                                new_args = []
                                for arg in tup[2]:
                                    new_arg = process_tuple(arg, tup)
                                    new_args.append(new_arg if new_arg is not None else arg)

                                if tup[1] == function_name:
                                    ref = f'REFERENCE{ref_counter}'
                                    ref_counter += 1
                                    flattened.append(('block', (tup[0], tup[1], new_args), ref))
                                    return ref
                                else:
                                    new_call = (tup[0], tup[1], new_args)
                                    parent_calls.append(new_call)
                                    return new_call
                            elif tup[0] in ['=', 'print', 'return']:
                                new_value = process_tuple(tup[1], tup) if len(tup) > 1 else None
                                if new_value is not None:
                                    new_tup = (tup[0], new_value)
                                    parent_calls.append(new_tup)
                                    return new_tup
                                else:
                                    flattened.append(('block', tup))
                            else:
                                flattened.append(('block', tup))
                        elif isinstance(tup, list):
                            new_list = [process_tuple(item, tup) or item for item in tup]
                            return new_list
                        return None

                    process_tuple(body)

                    return flattened, parent_calls

                depil_block, parent = flatten_and_extract_incr(body, tupleVar[1])
                i = 0
                i_bkp = []
                return_value = None

                print(depil_block)
                print(parent)
                #exit()
                def handle_control_structure(structure):
                    global dontCreateAnotherVar
                    if structure[0] == 'if':
                        return evalPerso(structure)
                    elif structure[0] == 'for' or structure[0] == 'while':
                        res = evalPerso(structure)
                        check = checkBreakReturn(res)
                        if check is not None:
                            if isinstance(check, tuple) and check[0] == 'return':
                                return check[1]
                        return res

                get_bkp_i = False
                while whenRecursiveFunctionBegin <= len(variables) or i < len(depil_block):
                    found_return = False
                    the_block = depil_block[i][1]
                    if isinstance(the_block, tuple):
                        if the_block[0] == 'call' and the_block[1] == tupleVar[1]:
                            curr_ref = depil_block[i][2]
                            i_bkp.append(i)
                            enterScope()
                            i = -1  # recommence au début de la liste (car récursif)
                        elif the_block[0] in ['if', 'for', 'while']:
                            result = handle_control_structure(the_block)
                            if isinstance(result, tuple) and result[0] == 'return': # un return dans un autre bloc que la racine de la fonction
                                if len(result) > 1:
                                    reference[curr_ref] = result[1]
                                exitScope() # On évalue le parent, donc le scope au dessus (problème de création de var sinon)

                                def is_child_of_next(current, next_tup):
                                    if next_tup[0] == 'call':
                                        for arg in next_tup[2]:
                                            if isinstance(arg, tuple) and arg[0] == 'call':
                                                if arg[1] == current[1] and any(a == current[2][0] for a in arg[2]):
                                                    return True
                                            elif arg == current[2][0]:
                                                return True
                                    elif next_tup[0] in ['return', 'print', '=']:
                                        return next_tup[1] == current[2][0]
                                    return False

                                if parent:
                                    while parent:
                                        tup = parent[0]
                                        is_child = len(parent) > 1 and is_child_of_next(tup, parent[1])

                                        if tup[0] == 'call':
                                            new_args = []
                                            enterScope()
                                            for arg in tup[2]:
                                                if isinstance(arg, tuple) and arg[0] == 'call':
                                                    evalPerso(("=", curr_ref, reference[curr_ref]))
                                                    new_arg = evalPerso(arg)
                                                elif arg == curr_ref:
                                                    new_arg = result[1] if isinstance(result, tuple) else result
                                                else:
                                                    new_arg = arg
                                                new_args.append(new_arg)
                                            exitScope()

                                            new_tup = (tup[0], tup[1], new_args)
                                            result = evalPerso(new_tup)

                                            if result is not None and isinstance(result, tuple) and result[
                                                0] == 'return':
                                                # Traiter le retour de la fonction récursive
                                                return_value = result[1]
                                                found_return = True
                                                break

                                            parent[0] = result

                                        elif tup[0] == 'return':
                                            if isinstance(result, tuple):
                                                return_value = evalPerso((tup[0], result[1]))
                                            else:
                                                return_value = evalPerso((tup[0], result))
                                            found_return = True
                                            break

                                        parent.pop(0)
                                        if len(parent) == 0:
                                            break
                                        if not is_child:
                                            break

                                    if found_return:
                                        while len(i_bkp) > 1:
                                            exitScope()
                                            i_bkp.pop()
                                        i_bkp.pop()

                                if i_bkp:
                                    i_bkp.pop()
                                    get_bkp_i = True # On est sorti de la "dernière itération de la fonction recursive,
                                                  # alors on repart là où on en était de la fonction recu précédente
                                else:
                                    break
                        else:
                            evalPerso(the_block)
                            if i == len(depil_block)-1:
                                exitScope()
                                if len(i_bkp) > 1:
                                    get_bkp_i = True
                                    i_bkp.pop() # On est sorti de la "dernière itération de la fonction recursive,
                                                  # alors on repart là où on en était de la fonction recu précédente
                                else:
                                    break
                    if found_return:
                        break

                    if get_bkp_i == True :
                        i = i_bkp[-1]
                        get_bkp_i = False
                    i += 1
                    # fin while
                return_value = return_value if return_value is not None else result
                return_value = return_value[1] if isinstance(return_value, tuple) else return_value
                result = evalPerso(return_value)
            # fin if
            else:
                result = evalPerso(body)
            handle_class_method_variables(tupleVar)
            update_reference_variables(ref_params)
            exitScope()
            return process_function_result(result)

        # -------------------- Fonctions prédéfinies --------------------

        case 'print':
            print(evalPerso(tupleVar[1]))
            return

        case 'len':
            result = evalPerso(tupleVar[1])
            if isinstance(result, tuple):
                if result[0] == "class":
                    print("Class has no length")
                    exit(1)
                else:
                    print("callable element has no length")
                    exit(1)

            if isinstance(result, int) or isinstance(result, float) or isinstance(result, complex) or isinstance(result,
                                                                                                                 bool):
                print(f"{type(result).__name__} {tupleVar[1]} has no length")
                exit(1)
            return len(evalPerso(tupleVar[1]))

        # -------------------- Statement particuliers --------------------

        case 'string':
            value = tupleVar[1]
            if '"' in value or "'" in value:
                value = tupleVar[1][1:-1]
            return value

        case 'value':
            return tupleVar[1]

        case 'ref':
            return tupleVar[1]

        case 'import':
            s = evalPerso(evalPerso(tupleVar[1]))  # renvoie un tuple, qu'après je reparsed pour renvoyer que la valeur du string

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
            print("variables :")
            print(variables)
            print("fonctions :")
            print(functions)
            print("class dict :")
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
                return ("return", evalPerso(tmp[1]))
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

    if constructor_params != [[]] and args != [[]]:
        for param, arg in zip(constructor_params, args):
            variables[-1][param[1]] = arg
    elif constructor_params == [[]] and args == [[]]: # If empty
        pass
    else:
        if len(constructor_params) != len(args):
            print(f"Constructor of class '{name}' expecting {len(constructor_params)}, received {len(args)}")
            exit(1)
        elif constructor_params != [[]] and args == [[]]:
            print(f"Constructor of class '{name}' expecting {len(constructor_params)} params, received 0")
            exit(1)
        elif constructor_params == [[]] and args != [[]]:
            print(f"Constructor of class '{name}' does not expect params, received {len(args)}")
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


## --------------- FUNCTION FOR THE CALL TUPLE ------------------ ##

def get_function_params_and_body(tupleVar):
    if tupleVar[1] not in functions and len(tupleVar) == 3:
        print(f"Function {tupleVar[1]} is not defined.")
        exit(1)
    elif len(tupleVar) > 3:
        return get_class_method_params_and_body(tupleVar)
    else:
        return functions[tupleVar[1]]

def get_class_method_params_and_body(tupleVar):
    theClass = evalPerso(tupleVar[3])[1]
    key = list(theClass.keys())[0]
    theFunction = find_dict_in_list(find_dict_in_list(classDict, key)[key][1], tupleVar[1])
    try:
        params, body = theFunction[tupleVar[1]]
    except:
        print(f"Function '{tupleVar[1]}' is not a method of the class '{key}'.")
        exit(1)
    setup_class_variables(theClass, key)
    return params, body

def setup_class_variables(theClass, key):
    for var in theClass[key]:
        variables[-1][var] = theClass[key][var]

def validate_function_args(func_name, params, args):
    if len(params) != len(args):
        print(f"Function {func_name} expected {len(params)} arguments, got {len(args)}.")
        exit(1)
    elif params != [[]] and args == [[]]:
        print(f"Function '{func_name}' expecting {len(params)} params, received 0")
        exit(1)
    elif params == [[]] and args != [[]]:
        print(f"Function '{func_name}' does not expect params, received {len(args)}")
        exit(1)

def setup_function_variables(params, args):
    ref_params = {}
    for i, param in enumerate(params):
        if param != [] and param[0] == "value":
            variables[-1][param[1]] = evalPerso(args[i])
        elif param != [] and param[0] == "ref":
            setup_reference_variable(param[1], args[i], ref_params)
    return ref_params

def setup_reference_variable(ref_name, arg_name, ref_params):
    global dontCreateAnotherVar
    if not is_variable_in_scope(ref_name):
        dontCreateAnotherVar = True
        variables[-1][ref_name] = evalPerso(arg_name)
        ref_params[ref_name] = arg_name

def is_variable_in_scope(var_name):
    for scope in reversed(variables):
        if var_name in scope:
            return True
    return False

def handle_class_method_variables(tupleVar):
    if len(tupleVar) > 3:
        theClass = evalPerso(tupleVar[3])[1]
        key = list(theClass.keys())[0]
        for var in theClass[key]:
            theClass[key][var] = variables[-1][var]

def update_reference_variables(ref_params):
    global dontCreateAnotherVar
    for ref_name, arg_name in ref_params.items():
        for s in reversed(range(len(variables) - 1)):
            if arg_name in variables[s]:
                variables[s][arg_name] = variables[-1][ref_name]
                break
    dontCreateAnotherVar = False

def process_function_result(result):
    check = checkBreakReturn(result)
    if check is not None:
        if isinstance(check, tuple) and check and check[0] == "break":
            print("break statement cannot be in a function")
            exit(1)
        while isinstance(check, tuple) and check and check[0] == "return":
            if len(check) > 1:
                check = check[1]
        return evalPerso(check)
    return result

def detect_recursion(body, function_name, parent_stack=None):
    if parent_stack is None:
        parent_stack = []

    if isinstance(body, tuple):
        if body[0] == 'call' and body[1] == function_name:
            if len(parent_stack) > 0:
                return True, parent_stack[0]
            return True, parent_stack

        new_parent_stack = parent_stack + [body] if body[0] in ['=', 'print', 'call'] else parent_stack

        for element in body[1:]:  # Start from index 1 to skip the first element
            result, context = detect_recursion(element, function_name, new_parent_stack)
            if result:
                return True, context

    elif isinstance(body, list):
        for element in body:
            result, context = detect_recursion(element, function_name, parent_stack)
            if result:
                return True, context

    elif isinstance(body, dict):
        for value in body.values():
            result, context = detect_recursion(value, function_name, parent_stack)
            if result:
                return True, context

    return False, None

def debug():
    evalPerso(("debug",))

def pritn(value):
    print(value)