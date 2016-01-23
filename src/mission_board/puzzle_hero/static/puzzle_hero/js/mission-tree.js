  var missions = {
    "mission_01": {
      "status": "closed",
      "reward": 20,
      "dependencies": []
    },
    "mission_02": {
      "status": "open",
      "reward": 50,
      "dependencies": [ "mission_01" ]
    },
    "mission_03": {
      "status": "locked",
      "reward": 50,
      "dependencies": [ "mission_02" ]
    },
    "mission_04": {
      "status": "locked",
      "reward": 50,
      "dependencies": [ "mission_03" ]
    },
    "mission_05": {
      "status": "open",
      "reward": 50,
      "dependencies": [ "mission_01" ]
    },
    "mission_06": {
      "status": "locked",
      "reward": 50,
      "dependencies": [ "mission_05" ]
    },
    "mission_07": {
      "status": "locked",
      "reward": 50,
      "dependencies": [ "mission_04", "mission_06" ]
    }
  };

function drawTree(selector, missions) {
	var svg = d3.select(selector)
    var inner = svg.select("g")
	var render = new dagreD3.render();

	// Left-to-right layout
	var g = new dagreD3.graphlib.Graph();
	g.setGraph({
		nodesep: 20,
		ranksep: 40,
		rankdir: "LR",
		marginx: 10,
		marginy: 10
	});

	function draw(isUpdate) {
		for (var id in missions) {
			var mission = missions[id];
			var className = mission.status;
			var html = "<div>";
			html += "<span class=reward>"+mission.reward+"</span>";
			// html += '<button type="button" class="btn btn-danger" data-toggle="popover" title="Popover title" data-content="And heres some amazing content. Its very engaging. Right?">r</button>' #}
			html += "</div>";
			g.setNode(id, {
				labelType: "html",
				label: html,
				rx: 5,
				ry: 5,
				padding: 0,
				class: className
			});

			for(i in mission.dependencies) {
				var did = mission.dependencies[i];
				g.setEdge(did, id, {
					width: 40,
					class: missions[did].status
				});
			}
		}

		inner.call(render, g);

		// Zoom and scale to fit
		var graphWidth = g.graph().width;
		var graphHeight = g.graph().height;
		var width = parseInt(svg.style("width").replace(/px/, ""));
		var height = parseInt(svg.style("height").replace(/px/, ""));
		var zoomScale = Math.min(width / graphWidth, height / graphHeight);
		var translate = [(width/2) - ((graphWidth*zoomScale)/2), (height/2) - ((graphHeight*zoomScale)/2)];

		var zoom = d3.behavior.zoom().on("zoom", function() {
			inner.attr("transform", "translate(" + d3.event.translate + ")" +
				"scale(" + d3.event.scale + ")");
		});
		zoom.translate(translate);
		zoom.scale(zoomScale);
		zoom.event(isUpdate ? svg.transition().duration(500) : d3.select("svg"));
	}

	draw();
}

$(".track-tree").each(function(index, item) {
	var json = atob($(item).data('json'))
	drawTree(item, missions);
});
