/* Dashboard JavaScript Handler */

let topMoviesChart = null;
let genreDoughnutChart = null;
let ratingDistChart = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardData();
});

async function fetchDashboardData() {
  try {
    const res = await fetch("/api/dashboard");
    const result = await res.json();

    if (result.status === "success") {
      updateKPICards(result.summary);
      renderTopMoviesChart(result.top_movies);
      renderGenreDoughnutChart(result.genre_popularity);
      renderRatingDistChart(result.rating_distribution);
      renderInsights(result.insights);
    } else {
      console.error("Dashboard API error:", result.message);
    }
  } catch (err) {
    console.error("Failed to load dashboard data:", err);
  }
}

function updateKPICards(summary) {
  document.getElementById("kpiTotalRecords").innerText = summary.total_records.toLocaleString();
  document.getElementById("kpiDistinctMovies").innerText = summary.distinct_movies.toLocaleString();
  document.getElementById("kpiDistinctUsers").innerText = summary.distinct_users.toLocaleString();
  document.getElementById("kpiOverallAvg").innerText = summary.overall_avg_rating ? `${summary.overall_avg_rating} ★` : "0.0 ★";
}

function renderTopMoviesChart(movies) {
  const ctx = document.getElementById("topMoviesChart").getContext("2d");
  
  if (topMoviesChart) {
    topMoviesChart.destroy();
  }

  const labels = movies.map(m => m.movie_title);
  const data = movies.map(m => m.avg_rating);

  topMoviesChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Average Rating (Out of 5)",
        data: data,
        backgroundColor: "rgba(56, 189, 248, 0.7)",
        borderColor: "#38bdf8",
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: 0,
          max: 5,
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#94a3b8" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Rating: ${ctx.raw} ★ (${movies[ctx.dataIndex].count} reviews)`
          }
        }
      }
    }
  });
}

function renderGenreDoughnutChart(genres) {
  const ctx = document.getElementById("genreDoughnutChart").getContext("2d");

  if (genreDoughnutChart) {
    genreDoughnutChart.destroy();
  }

  const labels = genres.map(g => g.genre);
  const data = genres.map(g => g.count);

  const colors = [
    "#ef4444", "#38bdf8", "#a855f7", "#f59e0b",
    "#ec4899", "#dc2626", "#10b981", "#14b8a6"
  ];

  genreDoughnutChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#1e293b"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", boxWidth: 12 }
        }
      }
    }
  });
}

function renderRatingDistChart(distribution) {
  const ctx = document.getElementById("ratingDistChart").getContext("2d");

  if (ratingDistChart) {
    ratingDistChart.destroy();
  }

  const labels = distribution.map(d => `${d.rating} ★`);
  const data = distribution.map(d => d.count);

  ratingDistChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Number of Ratings",
        data: data,
        backgroundColor: "rgba(245, 158, 11, 0.7)",
        borderColor: "#f59e0b",
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { color: "#94a3b8" }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8" }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderInsights(insights) {
  const container = document.getElementById("insightsContainer");
  if (!insights || insights.length === 0) {
    container.innerHTML = '<div class="text-muted small">No insights available.</div>';
    return;
  }

  container.innerHTML = insights.map(text => `
    <div class="insight-item">
      <i class="fa-solid fa-angle-right text-info me-2"></i> ${text}
    </div>
  `).join('');
}
