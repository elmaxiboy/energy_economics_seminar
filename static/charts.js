const svg_W = 600
const svg_H = 300

function get_results() {

    const sessionCookie = document.cookie;

    fetch("/plot-data", {
        method: 'GET',
        headers: {'Cookie': sessionCookie},
        credentials: 'same-origin' 
      })
      .then(response => response.json())
      .then(data => {

        draw_ghi(data["avg_monthly_ghi"])
        draw_cash_flows(data["cash_flows"])
        draw_depreciation_schedule(data["depreciation_schedule"])
        draw_npv(data["npv"])
        draw_outputs(data["avoided_co2_equivalent"])
        draw_sensitivity_tornado_chart(data["sensitivity_analysis"])
      })
      .catch(err => {
        document.getElementById("plots").textContent = "Error fetching results.";
        console.error(err);
      });
  }
 
 function draw_ghi(data){
    // Load the JSON data
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
        let margin = { top: 20, right: 20, bottom: 50, left: 50 };
        let width = svg_W - margin.left - margin.right;
        let height = svg_H - margin.top - margin.bottom;

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
 
    }

function draw_npv(data) {

            // Validate and transform data into a consistent format
            const formatter = new Intl.NumberFormat('en-US');
            const dataset = Object.entries(data)
                .map(([index, value]) => ({
                    x: +index,
                    y: +value/1000000
                }))
                .filter(d => !isNaN(d.x) && !isNaN(d.y)); // Remove invalid entries

            // Check if dataset is empty
            if (dataset.length === 0) {
                console.error("No valid data available for plotting.");
                return;
            }

            let margin = { top: 20, right: 30, bottom: 45, left: 60 };
            let width = svg_W - margin.left - margin.right;
            let height = svg_H - margin.top - margin.bottom;

            // Create SVG canvas
            const svg = d3.select("#npv")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            // Set up scales
            const xScale = d3.scaleLinear()
                .domain(d3.extent(dataset, d => d.x)) // Input range
                .range([0, width]); // Output range

            const yMin = Math.min(0, d3.min(dataset, d => d.y));
            const yMax = Math.max(0, d3.max(dataset, d => d.y));
            
            const yScale = d3.scaleLinear()
                .domain([yMin, yMax]) // Ensure 0 is always included in the domain
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
                .datum(dataset)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 2)
                .attr("d", line);

            const tooltip = d3.select(".tooltip");

            // Add points
            svg.selectAll(".dot")
                .data(dataset)
                .enter()
                .append("circle")
                .attr("cx", d => xScale(d.x))
                .attr("cy", d => yScale(d.y))
                .attr("r", 4)
                .attr("fill", "steelblue")
                .on("mouseover", function (event, d) {
                    tooltip.style("opacity", 1)
                        .html(`Period: ${d.x}<br>NPV: ${d.y.toFixed(3)} MM USD`)
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

                // Add labels
                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height + margin.bottom - 10)
                    .attr("text-anchor", "middle")
                    .text("Year");

                svg.append("text")
                    .attr("x", -height / 2)
                    .attr("y", -margin.left + 15)
                    .attr("transform", "rotate(-90)")
                    .attr("text-anchor", "middle")
                    .text("MM USD");
        }

function draw_cash_flows(data){

        const table = d3.select("#data-table-cash-flows");

        // Extract column names from the JSON
        const columns = Object.keys(data[0]);

        // Add table header
        const thead = table.append("thead").append("tr");
        thead.selectAll("th")
            .data(columns)
            .enter()
            .append("th")
            .text(d => d);

        // Add table body
        const tbody = table.append("tbody");
        const rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr")
            .attr("class", (row, i) => {
                if (row.cum_npv > 0 && tbody.selectAll("tr.highlighted").empty()) {
                    return "highlighted"; // Highlight the first positive cum_npv row
                }
                return null;
            });

        rows.selectAll("td")
            .data(row => columns.map(col => ({ key: col, value: row[col] })))
            .enter()
            .append("td")
            .text(d => formatNumber(d.value))
            .attr("class", d => (typeof d.value === "number" && d.key == "cum_npv")
                ? (d.value >= 0 ? "positive" : "negative")
                : "");

        // Add table footer for totals
        const tfoot = table.append("tfoot").append("tr");
        tfoot.selectAll("td")
            .data(columns)
            .enter()
            .append("td")
            .text((col, i) => {
                if (i === 0) return "Total"; // First column (year) shows "Total"
                if (col === "cum_npv") return "";
                const total = data.reduce((sum, row) => sum + (row[col] || 0), 0);
                return col !== "year" ? formatNumber(total) : ""; // Skip totals for "year"
            })
            .style("font-weight", "bold"); // Make the total row bold
    }




function draw_outputs(data){


        const table = d3.select("#data-table-outputs");

        // Extract column names from the JSON
        const columns = Object.keys(data[0]);

        // Add table header
        const thead = table.append("thead").append("tr");
        thead.selectAll("th")
            .data(columns)
            .enter()
            .append("th")
            .text(d => d);

        // Add table body
        const tbody = table.append("tbody");
        const rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

        rows.selectAll("td")
            .data(row => columns.map(col => ({ key: col, value: row[col] })))
            .enter()
            .append("td")
            .text(d => formatNumber(d.value))


        // Add table footer for totals
        const tfoot = table.append("tfoot").append("tr");
        tfoot.selectAll("td")
            .data(columns)
            .enter()
            .append("td")
            .text((col, i) => {
                if (i === 0) return "Total"; // First column (year) shows "Total"
                const total = data.reduce((sum, row) => sum + (row[col] || 0), 0);
                return col !== "year" ? formatNumber(total) : ""; // Skip totals for "year"
            })
            .style("font-weight", "bold"); // Make the total row bold
    }


function draw_depreciation_schedule(data){


        const table = d3.select("#data-table-depreciation-schedule");

        // Extract column names from the JSON
        const columns = Object.keys(data[0]);

        // Add table header
        const thead = table.append("thead").append("tr");
        thead.selectAll("th")
            .data(columns)
            .enter()
            .append("th")
            .text(d => d);

        // Add table body
        const tbody = table.append("tbody");
        const rows = tbody.selectAll("tr")
            .data(data)
            .enter()
            .append("tr");

        rows.selectAll("td")
            .data(row => columns.map(col => ({ key: col, value: row[col] })))
            .enter()
            .append("td")
            .text(d => formatNumber(d.value))


        // Add table footer for totals
        const tfoot = table.append("tfoot").append("tr");
        tfoot.selectAll("td")
            .data(columns)
            .enter()
            .append("td")
            .text((col, i) => {
                if (i === 0) return "Total"; // First column (year) shows "Total"
                const total = data.reduce((sum, row) => sum + (row[col] || 0), 0);
                return col !== "year" ? formatNumber(total) : ""; // Skip totals for "year"
            })
            .style("font-weight", "bold"); // Make the total row bold
    }



function draw_sensitivity_tornado_chart(data) {

        const keys = Object.keys(data);
        const formattedData = keys.map(key => ({
          key,
          up: data[key].percentage_up,
          down: data[key].percentage_down,
          range: Math.abs(data[key].percentage_up - data[key].percentage_down),
        }))
        .sort((a, b) => b.range - a.range); // Sort by range in descending order
  
        // Chart dimensions
        const margin = { top: 20, right: 30, bottom: 50, left: 150 }; // Increased left margin to avoid bars touching the axis
        const width = svg_W - margin.left - margin.right;
        const height = keys.length * 55;
  
        // Create SVG container
        const svg = d3.select("#tornado_chart")
          .append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);
  
  
        // Find max absolute value for symmetric domain
        const maxValue = d3.max(formattedData, d => Math.max(Math.abs(d.up), Math.abs(d.down)));
  
        // Scales
        const x = d3.scaleLinear()
          .domain([-maxValue - 0.1*maxValue, maxValue + 0.1]) // Symmetric domain
          .range([0, width]);
  
        const y = d3.scaleBand()
          .domain(formattedData.map(d => d.key))
          .range([0, height])
          .padding(0.4);
  
        // Axes
        svg.append("g")
          .call(d3.axisLeft(y).tickSize(0))
          .selectAll("text")
          .style("font-size", "12px");
  
        svg.append("g")
          .attr("transform", `translate(0, ${height})`)
          .call(d3.axisBottom(x).ticks(6))
          .selectAll("text")
          .style("font-size", "12px");
  
        // Draw bars
        svg.selectAll(".bar-group")
          .data(formattedData)
          .join("g")
          .attr("class", "bar-group")
          .each(function (d) {
            const group = d3.select(this);
            
        const tooltip = d3.select(".tooltip");

            // Draw "down" bar
            group.append("rect")
              .attr("class", "bar-down")
              .attr("x", d.down < 0 ? x(d.down) : x(0)) // Start from `d.down` if negative
              .attr("y", y(d.key))
              .attr("width", Math.abs(x(d.down) - x(0))) // Width based on distance from 0
              .attr("height", y.bandwidth() / 2)
              .on("mouseover", (event) => {
                tooltip.transition().duration(200).style("opacity", 1);
                tooltip.html(`Parameter: ${d.key}<br>-10%: ${d.down.toFixed(2)}%`)
                  .style("left", `${event.pageX + 10}px`)
                  .style("top", `${event.pageY - 20}px`);
              })
              .on("mousemove", (event) => {
                tooltip.style("left", `${event.pageX + 10}px`)
                  .style("top", `${event.pageY - 20}px`);
              })
              .on("mouseout", () => {
                tooltip.transition().duration(200).style("opacity", 0);
              });
  
            // Draw "up" bar
            group.append("rect")
              .attr("class", "bar-up")
              .attr("x", d.up < 0 ? x(d.up) : x(0)) // Start from `d.up` if negative
              .attr("y", y(d.key) + y.bandwidth() / 2)
              .attr("width", Math.abs(x(d.up) - x(0))) // Width based on distance from 0
              .attr("height", y.bandwidth() / 2)
              .on("mouseover", (event) => {
                tooltip.transition().duration(200).style("opacity", 1);
                tooltip.html(`Parameter: ${d.key}<br>+10%: ${d.up.toFixed(2)}%`)
                  .style("left", `${event.pageX + 10}px`)
                  .style("top", `${event.pageY - 20}px`);
              })
              .on("mousemove", (event) => {
                tooltip.style("left", `${event.pageX + 10}px`)
                  .style("top", `${event.pageY - 20}px`);
              })
              .on("mouseout", () => {
                tooltip.transition().duration(200).style("opacity", 0);
              });
          });

          // Add labels
          svg.append("text")
          .attr("x", width / 2)
          .attr("y", height + margin.bottom-3)
          .attr("text-anchor", "middle")
          .text("% change in NPV ");

      svg.append("text")
          .attr("x", -height / 2)
          .attr("y", -margin.left + 15)
          .attr("transform", "rotate(-90)")
          .attr("text-anchor", "middle")
          .text("Parameters");
  
      }

  
  function updateSliderValues() {
    const slider = document.getElementById('slider_input');
    const valueX = document.getElementById('tangible_capex');
    const value1MinusX = document.getElementById('intangible_capex');
    const x = parseFloat(slider.value).toFixed(2);
    valueX.textContent = `${x}%`; // Add the % sign
    value1MinusX.textContent = `${(1 - x).toFixed(2)}%`; // Add the % sign
}


function formatNumber(value) {
    if (typeof value !== "number") return value; // Skip formatting for non-numeric values
    return value.toFixed(1).replace(/\d(?=(\d{3})+\.)/g, '$&,'); // Round to 1 decimal and add thousand separators
}
 
 