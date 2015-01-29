from django.shortcuts import render
import json

NUMBER = 'num'
OPERATION = 'op'
STATE = 'state'


def applyOp(v1, v2, op):
    v1 = int(v1)
    v2 = int(v2)
    op = str(op)
    if op == "+":
        return (v1 + v2)
    if op == "-":
        return (v1 - v2)
    if op == "*":
        return (v1 * v2)
    if op == "/":
        return (v1 // v2)
    if op == "=":
        return v2
    return 0


def appendNum(num1, num2):
    return int(num1) * 10 + int(num2)


def enterNum(num, state):
    if state["etype"] == OPERATION:
        state["cnum"] = int(num)
        state["display"] = state["cnum"]
    else:
        state["cnum"] = appendNum(state["cnum"], num)
        state["display"] = state["cnum"]
    state["etype"] = NUMBER


def enterOp(op, state):
    if state["op"] == '/' and state["cnum"] == 0:
        state["lnum"] = 0
        state["cnum"] = 0
        state["op"] = '+'
        state["display"] = "Error"
    else:
        state["lnum"] = applyOp(state["lnum"], state["cnum"], state["op"])
        state["cnum"] = state["lnum"]
        state["display"] = state["lnum"]
    state["etype"] = OPERATION


def init_state():
    return {
        "lnum": 0,
        "cnum": 0,
        "op": "+",
        "etype": NUMBER,
        "display": 0
    }


def state_to_string(state):
    return json.dumps(state)


def string_to_state(state_string):
    try:
        return json.loads(state_string)
    except:
        return init_state()


def calculator(request):
    state = None
    # get the state back
    if STATE in request.POST:
        state = string_to_state(request.POST[STATE])
    else:
        state = init_state()
    # after retrieving state, do whatever
    if NUMBER in request.POST:
        enterNum(request.POST[NUMBER], state)
    elif OPERATION in request.POST:
        enterOp(request.POST[OPERATION], state)

    return render(request, 'calculator/calculator.html',
                  {"value": state["display"], "state": state_to_string(state)})
