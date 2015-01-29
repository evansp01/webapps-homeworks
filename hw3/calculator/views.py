from django.shortcuts import render

NUMBER='num'
OPERATION='op'

class State:
    lnum = 0
    cnum = 0
    op = '+'
    etype = NUMBER
    display = 0

    def __str__(self):
        return "Last: %d Current: %d Operation: %s" % (self.lnum, self.cnum, self.op)

state = State()


def applyOp(v1, v2, op):
    v1 = int(v1);
    v2 = int(v2);
    return {
        "+": (v1 + v2),
        "-": (v1 - v2),
        "*": (v1 * v2),
        "/": (v1 // v2),
        "=": v2
    }.get(str(op),0)


def appendNum(num1, num2):
    return int(num1)*10+num2

def enterNum(num):
    if state.etype is OPERATION:
        state.cnum = int(num)
        state.display = state.cnum
    else:
        state.cnum = appendNum(state.cnum, num)
        state.display = state.cnum
    state.etype = NUMBER

def enterOp(op):
    if state.op is '/' and state.cnum is 0:
        state.lnum = 0
        state.cnum = 0
        state.op = '+'
        state.display = "Error"
    else:
        state.lnum = applyOp(state.lnum, state.cnum, state.op)
        state.cnum = state.lnum
        state.display = state.lnum
    state.etype - OPERATION

def calculator(request):
    print(state)
    if NUMBER in request.GET:
        print "Number request", request.GET[NUMBER]
    elif OPERATION in request.GET:
        print "Operation request", request.GET[OPERATION]
    else:
        print "Page request"    
    return render(request, 'calculator/calculator.html', {"value": state.display})