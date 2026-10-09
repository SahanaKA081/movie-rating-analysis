/* Analysis Page JavaScript Handler */

let topMoviesAnalysisChart = null;
let mostRatedChart = null;
let genreComparisonChart = null;
let yearTrendsChart = null;

document.addEventListener("DOMContentLoaded", () => {
  loadAllAnalysisData();
});

function loadAllAnalysisData() {
  loadAnalysisInsights();
  loadTopMovies();
  loadMostRated();
  loadGenrePerformance();
  loadYearTrends();
}

async function loadAnalysisInsights() {
  try {
    const res = await fetch("/api/analysis/insights");
    const result = await res.json();
    if (result.status === "success") {
      const container = document.getElementById("analysisInsightsList");
      container.innerHTML = result.insights.map(item => `
        <li class="mb-1"><i class="fa-solid fa-check text-info me-2"></i>${item}</li>
      `).join('');
    }
  } catch (err) {
    console.error("Failed to load analysis insights:", err);
  }
}

async function loadTopMovies() {
  const minVotes = document.getElementById("minVotesFilter").value;
  try {
    const res = await fetch(`/api/analysis/top-movies?min_votes=${minVotes}&limit=10`);
    const result = await res.json();

    if (result.status === "success") {
      renderTopMoviesChartAnalysis(result.data);
      renderTopMoviesTable(result.data);
    }
  } catch (err) {
    console.error("Failed to load top movies:", err);
  }
}

function renderTopMoviesChartAnalysis(data) {
  const ctx = document.getElementById("topMoviesChartAnalysis").getContext("2d");
  if (topMoviesAnalysisChart) topMoviesAnalysisChart.destroy();

  const labels = data.map(d => d.movie_title);
  const values = data.map(d => d.avg_rating);

  topMoviesAnalysisChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Average Rating",
        data: values,
        backgroundColor: "rgba(245, 158, 11, 0.75)",
        borderColor: "#f59e0b",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 5, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderTopMoviesTable(data) {
  const tbody = document.getElementById("topMoviesTableBody");
  if (!data || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No movies meet this minimum review count threshold.</td></tr>';
    return;
  }

  tbody.innerHTML = data.map((d, index) => `
    <tr>
      <td class="fw-bold text-warning">#${index + 1}</td>
      <td class="fw-bold">${escapeHtml(d.movie_title)}</td>
      <td><span class="badge badge-genre badge-${escapeHtml(d.genre)}">${escapeHtml(d.genre)}</span></td>
      <td><span class="badge badge-release-year">${d.release_year}</span></td>
      <td class="fw-bold text-info">${d.avg_rating} ★</td>
      <td><span class="badge bg-dark border border-secondary">${d.total_ratings} reviews</span></td>
    </tr>
  `).join('');
}

async function loadMostRated() {
  try {
    const res = await fetch("/api/analysis/most-rated?limit=8");
    const result = await res.json();

    if (result.status === "success") {
      renderMostRatedChart(result.data);
      renderMostRatedTable(result.data);
    }
  } catch (err) {
    console.error("Failed to load most rated movies:", err);
  }
}

function renderMostRatedChart(data) {
  const ctx = document.getElementById("mostRatedChart").getContext("2d");
  if (mostRatedChart) mostRatedChart.destroy();

  const labels = data.map(d => d.movie_title);
  const values = data.map(d => d.total_ratings);

  mostRatedChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Total Rating Submissions",
        data: values,
        backgroundColor: "rgba(236, 72, 153, 0.75)",
        borderColor: "#ec4899",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        y: { grid: { display: false }, ticks: { color: "#94a3b8" } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderMostRatedTable(data) {
  const tbody = document.getElementById("mostRatedTableBody");
  tbody.innerHTML = data.map(d => `
    <tr>
      <td class="fw-bold">${escapeHtml(d.movie_title)}</td>
      <td><span class="badge badge-genre badge-${escapeHtml(d.genre)}">${escapeHtml(d.genre)}</span></td>
      <td class="fw-bold text-pink" style="color: #ec4899;">${d.total_ratings} reviews</td>
      <td class="text-info">${d.avg_rating} ★</td>
    </tr>
  `).join('');
}

async function loadGenrePerformance() {
  try {
    const res = await fetch("/api/analysis/genres");
    const result = await res.json();

    if (result.status === "success") {
      renderGenreComparisonChart(result.data);
    }
  } catch (err) {
    console.error("Failed to load genre performance:", err);
  }
}

function renderGenreComparisonChart(data) {
  const ctx = document.getElementById("genreComparisonChart").getContext("2d");
  if (genreComparisonChart) genreComparisonChart.destroy();

  const labels = data.map(d => d.genre);
  const avgRatings = data.map(d => d.avg_rating);
  const totalCounts = data.map(d => d.total_ratings);

  genreComparisonChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Average Rating (Out of 5)",
          data: avgRatings,
          backgroundColor: "rgba(56, 189, 248, 0.7)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          yAxisID: "y"
        },
        {
          label: "Total Rating Submissions",
          data: totalCounts,
          backgroundColor: "rgba(168, 85, 247, 0.4)",
          borderColor: "#a855f7",
          borderWidth: 1,
          type: "line",
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: "linear",
          display: true,
          position: "left",
          min: 0,
          max: 5,
          title: { display: true, text: "Avg Rating", color: "#38bdf8" },
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#94a3b8" }
        },
        y1: {
          type: "linear",
          display: true,
          position: "right",
          beginAtZero: true,
          title: { display: true, text: "Total Reviews", color: "#a855f7" },
          grid: { drawOnChartArea: false },
          ticks: { color: "#94a3b8" }
        },
        x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
      },
      plugins: {
        legend: { labels: { color: "#94a3b8" } }
      }
    }
  });
}

async function loadYearTrends() {
  try {
    const res = await fetch("/api/analysis/year-stats");
    const result = await res.json();

    if (result.status === "success") {
      renderYearTrendsChart(result.data);
    }
  } catch (err) {
    console.error("Failed to load year trends:", err);
  }
}

function renderYearTrendsChart(data) {
  const ctx = document.getElementById("yearTrendsChart").getContext("2d");
  if (yearTrendsChart) yearTrendsChart.destroy();

  const labels = data.map(d => d.release_year);
  const avgRatings = data.map(d => d.avg_rating);

  yearTrendsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Avg Rating by Release Year",
        data: avgRatings,
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.15)",
        fill: true,
        tension: 0.3,
        pointBackgroundColor: "#10b981"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 0, max: 5, grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94a3b8" } },
        x: { grid: { display: false }, ticks: { color: "#94a3b8" } }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
