var state = {lnum:0, cnum:0, op:"+", etype:"num", current:0};

function display(value){
	var display = document.getElementById("display");
	display.innerHTML = value; 
}

function applyOp(v1, v2, op){
	v1 = parseInt(v1);
	v2 = parseInt(v2);
	switch(op){
		case "+":
			return v1 + v2;
		case "-":
			return v1 - v2;
		case "*":
			return v1 * v2;
		case "/":
			return Math.floor(v1 / v2);
		case "=":
			return v2;
		default:
			console.log("recieved unknown operation " + op);
			return 0;
	}
}

function appendNum(num1, num2){
	return parseInt(num1)*10 + parseInt(num2);
}

function enterNum(num) {
	if (state.etype == "op"){
		state.cnum = num;
		display(state.cnum);
	} else {
		state.cnum = appendNum(state.cnum, num);
		display(state.cnum);
	}
	state.etype = "num";
}

function enterOp(op){
	if(state.op == "/" && state.cnum == 0){
		display("Error");
		state.lnum = 0;
		state.cnum = 0;
		state.op = "+"
	} else {
		state.lnum = applyOp(state.lnum, state.cnum, state.op);
		state.cnum = state.lnum
		display(state.lnum);
		state.op = op;
	}
	state.etype = "op"
}