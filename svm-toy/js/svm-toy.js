var index = 0;
var colors = ["#A06", "#FF0", "#66F"];
var answer_colors = [[127, 0, 60], [127, 127, 0],  [0, 0, 127]];
var svr_line_color = "white";
var eps_tube_color = "blue";
var context = null;
var width = null;
var height = null;
var train_points = [];
function setColorButton()
{
	var color = document.getElementById("color");
	color.style.backgroundColor = colors[index];
	color.style.color = "black";
}

function drawPoint(x, y, color)
{
	context.fillStyle = color;
	context.fillRect(x, y, 4, 4);
}

function drawAllPoints()
{
	for(i = 0; i < train_points.length; ++i)
	{
		var point = train_points[i];
		var index = point[0];
		var x = point[1];
		var y = point[2];
		drawPoint(x, y, colors[index]);
	}
}

function addPoint(x, y)
{
	drawPoint(x, y, colors[index]);
	train_points.push([index, x, y]);
}

function init()
{
	setColorButton();
	var canvas = document.getElementById('features');
	width = canvas.width;
	height = canvas.height;
	context = canvas.getContext("2d");
	canvas.onclick = function(e)
	{
		var mouseX = e.pageX - this.offsetLeft;
		var mouseY = e.pageY - this.offsetTop;

		addPoint(mouseX, mouseY);
	};
}

function nextColor()
{
	index = (index + 1) % colors.length;
	setColorButton();
}

function clearScreen()
{
	context.clearRect(0, 0, width, height);
}

function clearScreenAndData()
{
	clearScreen();
	train_points = [];
}

function generateTrainData()
{
	var prob = create_svm_nodes(train_points.length);
	for(i = 0; i < train_points.length; ++i)
	{
		var point = train_points[i];
		var index = point[0];
		var x = point[1];
		var y = point[2];
		add_instance(prob, i, index, x/width, y/height);
	}

	return prob;
}

function testAllPoints(model)
{
	var svmtype = svm_get_svm_type(model);
	if(svmtype == 3 || svmtype == 4)
	{
		clearScreen();

		var p = get_svr_epsilon(model) * width;

		for(var i = 0; i < width; i += 1)
		{
			var answer = libsvm_predict_for_toy(1.0*i/width, 0, model) * width;
			context.fillStyle = svr_line_color;
			context.fillRect(i, answer, 1, 1);

			if(svmtype == 3)
			{
				context.fillStyle = eps_tube_color;
				context.fillRect(i, answer + p, 1, 1);
				context.fillRect(i, answer - p, 1, 1);
			}
		}

		return;
	}

	var imgData=context.createImageData(width, height);
	var k = 0;
	for(var j = 0; j < height; j += 1)
	{
		for(var i = 0; i < width; i += 1, k += 1)
		{
			var answer = libsvm_predict_for_toy(i/width, j/height, model);
			imgData.data[k*4+0] = answer_colors[answer][0];
			imgData.data[k*4+1] = answer_colors[answer][1];
			imgData.data[k*4+2] = answer_colors[answer][2];
			imgData.data[k*4+3] = 255;
		}
	}
	context.putImageData(imgData,0,0);
}

function drawModel()
{
	var param = document.getElementById("param").value;
	var prob = generateTrainData();
	var model = libsvm_train_for_toy(prob, param); // free problem
	testAllPoints(model);

	drawAllPoints();

	svm_free_model_content(model);
	Module._free(model);
}

function checkApplet()
{
	if (window.location.search.toString().search('js=1') == -1)
		document.getElementById('svm-toy-js').style.display = "none";
	else{
		document.getElementById('applet').style.display = "none";
		init();
	}
}



