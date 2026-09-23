function readColor(variableName) {
  return getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
}

function formatUsd(value) {
  return `$${value.toFixed(2)}`;
}

function buildTraces(prices) {
  const dates = prices.map((p) => p.date);
  const closes = prices.map((p) => p.close);
  const bandLower = prices.map((p) => p.band_lower);
  const bandUpper = prices.map((p) => p.band_upper);
  const bandRange = prices.map((p) => [p.band_lower, p.band_upper]);

  const lineColor = readColor("--series-line");
  const surface = readColor("--surface-1");

  const lowerBoundary = {
    x: dates,
    y: bandLower,
    mode: "lines",
    line: { width: 0 },
    hoverinfo: "skip",
    showlegend: false,
  };

  const upperBoundary = {
    x: dates,
    y: bandUpper,
    mode: "lines",
    line: { width: 0 },
    fill: "tonexty",
    fillcolor: hexToRgba(lineColor, 0.1),
    hoverinfo: "skip",
    showlegend: false,
  };

  const closeLine = {
    x: dates,
    y: closes,
    customdata: bandRange,
    mode: "lines",
    line: { color: lineColor, width: 2 },
    showlegend: false,
    hovertemplate:
      "%{x|%b %d, %Y}<br>" +
      "<b>%{y:$.2f}</b><br>" +
      "Expected: %{customdata[0]:$.2f}–%{customdata[1]:$.2f}" +
      "<extra></extra>",
  };

  const breakoutTrace = (direction, colorVar, label) => {
    const points = prices.filter((p) => p.is_breakout && p.direction === direction);
    return {
      x: points.map((p) => p.date),
      y: points.map((p) => p.close),
      customdata: points.map((p) => p.date),
      mode: "markers",
      name: label,
      meta: "breakout",
      marker: {
        color: readColor(colorVar),
        size: 10,
        line: { width: 2, color: surface },
      },
      hovertemplate: `%{x|%b %d, %Y}<br><b>%{y:$.2f}</b><br>${label} — click for details<extra></extra>`,
    };
  };

  return [
    lowerBoundary,
    upperBoundary,
    closeLine,
    breakoutTrace("above", "--series-above", "Above expected range"),
    breakoutTrace("below", "--series-below", "Below expected range"),
  ];
}

function hexToRgba(hex, alpha) {
  const value = hex.replace("#", "");
  const r = parseInt(value.substring(0, 2), 16);
  const g = parseInt(value.substring(2, 4), 16);
  const b = parseInt(value.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function renderChart(prices) {
  const layout = {
    margin: { l: 48, r: 16, t: 16, b: 40 },
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: { color: readColor("--text-secondary"), family: "system-ui, sans-serif" },
    xaxis: { gridcolor: readColor("--gridline"), showline: false },
    yaxis: { gridcolor: readColor("--gridline"), tickprefix: "$" },
    legend: { orientation: "h", y: -0.2 },
    hovermode: "x unified",
  };

  Plotly.newPlot("chart", buildTraces(prices), layout, { displayModeBar: false, responsive: true });

  const chart = document.getElementById("chart");
  chart.on("plotly_click", (event) => {
    const point = event.points[0];
    if (point.data.meta !== "breakout") return;
    showExplanation(point.customdata);
  });
}

function renderTable(prices) {
  const tbody = document.querySelector("#data-table tbody");
  tbody.textContent = "";

  for (const p of prices) {
    const row = document.createElement("tr");
    if (p.is_breakout) row.classList.add(`breakout-${p.direction}`);

    const status = p.is_breakout ? (p.direction === "above" ? "Above range" : "Below range") : "Within range";
    const cells = [p.date, formatUsd(p.close), `${formatUsd(p.band_lower)}–${formatUsd(p.band_upper)}`, status];

    for (const value of cells) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    tbody.appendChild(row);
  }
}

async function showExplanation(dateStr) {
  const response = await fetch(`/api/explain/${dateStr}`);
  if (!response.ok) return;
  const explanation = await response.json();

  document.getElementById("explanation-placeholder").hidden = true;
  const panel = document.getElementById("explanation-panel");
  panel.hidden = false;

  document.getElementById("explanation-date").textContent = explanation.date;

  const badge = document.getElementById("explanation-direction");
  badge.textContent = explanation.direction === "above" ? "Above expected range" : "Below expected range";
  badge.className = `badge ${explanation.direction}`;

  document.getElementById("explanation-range").textContent =
    `${formatUsd(explanation.band_lower)}–${formatUsd(explanation.band_upper)}`;
  document.getElementById("explanation-close").textContent = formatUsd(explanation.close);
  document.getElementById("explanation-deviation").textContent = formatUsd(explanation.deviation);
  document.getElementById("explanation-text").textContent = explanation.text;
}

async function main() {
  const response = await fetch("/api/prices");
  const prices = await response.json();
  renderChart(prices);
  renderTable(prices);
}

main();
