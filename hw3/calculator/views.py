from django.shortcuts import render

NUMBER='num'
OPERATION='op'

def applyOp(v1, v2, op):
    v1 = int(v1);
    v2 = int(v2);
    operations = {
        "+": (v1 + v2),
        "-": (v1 - v2),
        "*": (v1 * v2),
        "/": (v1 // v2),
        "=": v2
    }
    print v1, op, v2, " ", operations[str(op)]
    return operations[str(op)]


def appendNum(num1, num2):
    return int(num1)*10+int(num2)

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

def assert_state(state, reset=False):
    items_required = ["lnum","cnum","op","etype","display"]
    passed = True
    for req in items_required:
        if req not in state:
            passed = False
    if not passed or reset:
        state["lnum"] = 0
        state["cnum"] = 0
        state["op"] = "+"
        state["etype"] = NUMBER
        state["display"] = 0

def calculator(request):
    assert_state(request.session)
    if NUMBER in request.GET:
        enterNum(request.GET[NUMBER], request.session)
    elif OPERATION in request.GET:
       enterOp(request.GET[OPERATION], request.session)
    else:
        assert_state(request.session, reset=True)
    print(request.session["display"])
    return render(request, 'calculator/calculator.html', 
                  {"value": int(request.session["display"])})