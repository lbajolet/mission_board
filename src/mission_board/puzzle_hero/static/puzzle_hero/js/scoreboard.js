var format = d3.time.format("%m/%d %H:%M")

function drawGraph(selector, data) {
	var svg = d3.select(selector),
		width = $(selector).parent().width(),
		height = $(selector).parent().height(),
		margins = {
			top: 20,
			right: 70,
			bottom: 20,
			left: 50
		},
		x = d3.scale.linear().range(
					[margins.left, width - margins.right]).domain([data.minDate, data.maxDate]),
		y = d3.scale.linear().range(
					[height - margins.top, margins.bottom]).domain([data.minScore, data.maxScore]),

		yAxis = d3.svg.axis().scale(y)
			.orient("left")
			.ticks(5)
			.innerTickSize(-width)
		    .outerTickSize(0)
		    .tickPadding(10);

	// Y axis
	svg.append("svg:g")
		.attr("class", "y axis")
		.attr("transform", "translate(" + (margins.left) + ",0)")
		.call(yAxis);

	var lineGen = d3.svg.line()
		.x(function(d) { return x(d.timestamp); })
		.y(function(d) { return y(d.score); });

	//Mouseover tip
	var tip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([120, 40])
	.html(function(d) {
		return "<strong>" + d.team + "</strong><br>" +
				"<i>" + format(new Date(d.timestamp * 1000)) + "</i><br>" +
				d.score + " pts";
	});
	svg.call(tip);

	data.teams.forEach(function(team) {
		svg.append('svg:path')
			.attr("class", "team-line")
			.attr('d', lineGen(team.scores))
			.attr('stroke', team.color);

		var last = team.scores[team.scores.length - 1]
		svg.append("a")
			.attr("class", "team-lbl")
			.attr("transform", "translate(" + x(last.timestamp) + "," + y(last.score) + ")")
			.attr("xlink:href", "/team/" + team.id)
			.append("text")
				.attr("dx", "15px")
				.attr("text-anchor", "start")
				.text(team.name);

		svg.selectAll("dot")
			.data(team.scores)
			.enter().append("circle")
			.attr("class", "score-dot")
			.attr("r", 3.5)
			.attr("cx", function(d) { return x(d.timestamp); })
			.attr("cy", function(d) { return y(d.score); })
			.on('mouseover', tip.show)
			.on('mouseout', tip.hide);
	});
}

$("#scoregraph").each(function(index, item) {
	var json = atob($(item).data('json'));
	json = JSON.parse(json);
	drawGraph("#scoregraph", json);
});
