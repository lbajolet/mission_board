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
		var i = 1;
		for (var id in missions) {
			var mission = missions[id];
console.log(mission);
			var className = mission.status;
			g.setNode(id, {
				labelType: "html",
				label: "<img class='mission-icon' src='/static/puzzle_hero/images/icons/"+ (mission.status == "locked"? "lock" : mission.kind) + ".png'></div>",
				rx: 5,
				ry: 5,
				padding: 0,
				id: id,
				class: className
			});

			for(j in mission.dependencies) {
				var did = mission.dependencies[j];
				g.setEdge(did, id, {
					width: 40,
					class: missions[did].status
				});
			}

			i += 1;
		}

		inner.call(render, g);

		$("svg .node").tipsy({
			gravity: $.fn.tipsy.autoNS,
			fade: true,
			html: true,
			title: function() {
				var mission = missions[this.id];
				return "<div class='mission-tip mission-" + mission.status + "'>" +
							"<h3>" + mission.title + "</h3>" +
							"<p>Kind: <b>" + mission.kind + "</b></p>" +
							"<p>Reward: <b class='tip-reward'>" + mission.reward + "</b></p>" +
							"<p>Status: <b class='tip-status'>" + mission.status + "</b></p>" +
						"</div>"
				// console.log(missions)
				// return "hello le dlskdjfd fdss fd sf sdf dfs df sdf sdf"
			}
		});
		$("svg .node").click(function() {
			window.location.href = "/mission/" + this.id;
		});
		// inner.selectAll("g.node")
			// .attr("title", function(v) { return styleTooltip("name", "coucou") })
			// .each(function(v) { $(this).tipsy({ gravity: "w", opacity: 1, html: true }); });


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
	var json = atob($(item).data('json'));
	json = JSON.parse(json);
	drawTree(item, json);
});
