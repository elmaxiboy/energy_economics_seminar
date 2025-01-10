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
        const svg = d3.select("#ghi")
            .append('svg')
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


    // Fetch data from the endpoint
    fetch("/npv-graphh")
        .then(response => response.json())
        .then(data => {
            // Convert JSON into an array of points
            const dataset = Object.entries(data).map(([index, value]) => ({
                x: +index,
                y: +value
            }));

            createChart(dataset);
        })
        .catch(error => console.error('Error fetching data:', error));

    function createChart(data) {
        const margin = { top: 20, right: 30, bottom: 40, left: 50 };
        const width = 800 - margin.left - margin.right;
        const height = 400 - margin.top - margin.bottom;

        // Create SVG canvas
        const svg = d3.select("#npv")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Set up scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.x)) // Input range
            .range([0, width]); // Output range

        const yScale = d3.scaleLinear()
            .domain([
                d3.min(data, d => d.y),
                d3.max(data, d => d.y)
            ])
            .range([height, 0]);

        // Add x-axis
        svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .attr("class", "axis")
            .call(d3.axisBottom(xScale));

        // Add y-axis
        svg.append("g")
            .attr("class", "axis")
            .call(d3.axisLeft(yScale));

        // Add dashed line at y = 0
        svg.append("line")
            .attr("class", "dashed-line")
            .attr("x1", 0)
            .attr("y1", yScale(0))
            .attr("x2", width)
            .attr("y2", yScale(0));

        // Define line generator
        const line = d3.line()
            .x(d => xScale(d.x))
            .y(d => yScale(d.y));

        // Add line path
        svg.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 2)
            .attr("d", line);

        // Add points
        svg.selectAll(".dot")
            .data(data)
            .enter()
            .append("circle")
            .attr("cx", d => xScale(d.x))
            .attr("cy", d => yScale(d.y))
            .attr("r", 4)
            .attr("fill", "steelblue");
    }
    
}
 
 