 function draw_ghi(){
    // Load the JSON data
    d3.json('/avg-monthly-ghi-graph').then(data => {
        const formattedData = Object.entries(data).map(([month, radiation]) => ({
            month: +month, // Convert month to integer
            radiation: +radiation // Convert radiation to number
        }));

        // Define the correct month order
        const monthOrder = [1, 2, 3, 4, 5, 6, 7, 8, 9,10, 11, 12];

        // Sort the data based on the desired month order
        const sortedData = formattedData.sort((a, b) => 
            monthOrder.indexOf(a.month) - monthOrder.indexOf(b.month)
        );

        // Set up dimensions and margins
        const margin = { top: 20, right: 20, bottom: 50, left: 50 };
        const width = 800 - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;

        // Create SVG container
        const svg = d3.select("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Define scales
        const x = d3.scaleBand()
            .domain(monthOrder) // Use the custom month order
            .range([0, width])
            .padding(0.1);

        const y = d3.scaleLinear()
            .domain([0, d3.max(sortedData, d => d.radiation)])
            .nice()
            .range([height, 0]);

        // Add X axis
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x).tickFormat(d3.format("02d")))
            .attr("class", "x-axis");

        // Add Y axis
        svg.append("g")
            .call(d3.axisLeft(y).ticks(10))
            .attr("class", "y-axis");

        // Draw bars
        svg.selectAll(".bar")
            .data(sortedData)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.month))
            .attr("y", d => y(d.radiation))
            .attr("width", x.bandwidth())
            .attr("height", d => height - y(d.radiation));

        // Add labels
        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height + margin.bottom - 10)
            .attr("text-anchor", "middle")
            .text("Month");

        svg.append("text")
            .attr("x", -height / 2)
            .attr("y", -margin.left + 15)
            .attr("transform", "rotate(-90)")
            .attr("text-anchor", "middle")
            .text("Radiation (kWh/m²/day)");


        // Tooltip
        const tooltip = d3.select(".tooltip");

        svg.selectAll(".bar")
        .on("mouseover", function (event, d) {
            // Access the correct radiation value using data[d.toString()]
            tooltip.style("opacity", 1)
                .html(`Month: ${d.month}<br>Radiation: ${d.radiation} kWh/m²`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 20) + "px");
        })
        .on("mousemove", function (event) {
            tooltip.style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 20) + "px");
        })
        .on("mouseout", function () {
            tooltip.style("opacity", 0);
        });
 
    });
}

function draw_npv(){
    
}
 
 