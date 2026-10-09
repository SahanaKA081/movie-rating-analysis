/* Ratings Page CRUD & Data Table JavaScript */

let currentPage = 1;
const pageLimit = 10;
function showCustomModal(modalId) {
  const modalEl = document.getElementById(modalId);
  if (modalEl) {
    modalEl.classList.add('show');
    modalEl.style.display = 'block';
    modalEl.removeAttribute('aria-hidden');
    let backdrop = document.getElementById('custom-modal-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.id = 'custom-modal-backdrop';
      backdrop.className = 'modal-backdrop fade show';
      document.body.appendChild(backdrop);
    }
  }
}

function hideCustomModal(modalId) {
  const modalEl = document.getElementById(modalId);
  if (modalEl) {
    modalEl.classList.remove('show');
    modalEl.style.display = 'none';
    modalEl.setAttribute('aria-hidden', 'true');
  }
  const backdrop = document.getElementById('custom-modal-backdrop');
  if (backdrop) {
    backdrop.remove();
  }
}

function openAddModal() {
  showCustomModal('addRatingModal');
}

document.addEventListener("DOMContentLoaded", () => {
  loadRatings(1);
});

function handleSearchKeyup(e) {
  if (e.key === "Enter" || e.target.value === "") {
    loadRatings(1);
  }
}

function resetFilters() {
  document.getElementById("searchInput").value = "";
  document.getElementById("genreFilter").value = "All";
  document.getElementById("sortSelect").value = "rating_date:desc";
  loadRatings(1);
}

async function loadRatings(page = 1) {
  currentPage = page;
  const search = document.getElementById("searchInput").value.trim();
  const genre = document.getElementById("genreFilter").value;
  const [sortBy, order] = document.getElementById("sortSelect").value.split(":");

  const url = `/api/ratings?search=${encodeURIComponent(search)}&genre=${encodeURIComponent(genre)}&sort_by=${sortBy}&order=${order}&page=${page}&limit=${pageLimit}`;

  const tbody = document.getElementById("ratingsTableBody");
  tbody.innerHTML = `
    <tr>
      <td colspan="8" class="text-center py-4 text-muted">
        <i class="fa-solid fa-spinner fa-spin me-2"></i> Fetching ratings from MongoDB...
      </td>
    </tr>
  `;

  try {
    const res = await fetch(url);
    const result = await res.json();

    if (result.status === "success") {
      populateGenreDropdown(result.available_genres);
      renderTableRows(result.data, page);
      renderPagination(result.pagination);
    } else {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">${result.message}</td></tr>`;
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center text-danger py-4">Failed to load data. Ensure Flask server and MongoDB are running.</td></tr>`;
  }
}

function populateGenreDropdown(genres) {
  const select = document.getElementById("genreFilter");
  const currentVal = select.value;

  select.innerHTML = '<option value="All">All Genres</option>';
  genres.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g;
    opt.textContent = g;
    if (g === currentVal) opt.selected = true;
    select.appendChild(opt);
  });
}

function renderTableRows(items, page) {
  const tbody = document.getElementById("ratingsTableBody");

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center py-4 text-muted">
          <i class="fa-solid fa-film-slash me-2 fs-4 d-block mb-2"></i>
          No rating records found matching your query.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map((item, index) => {
    const rowNum = (page - 1) * pageLimit + index + 1;
    const formattedDate = item.rating_date ? new Date(item.rating_date).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) : 'N/A';
    
    // Star display
    const stars = '★'.repeat(Math.floor(item.rating)) + (item.rating % 1 !== 0 ? '½' : '');

    return `
      <tr>
        <td class="text-muted fw-bold">${rowNum}</td>
        <td><code class="text-info">${item.user_id}</code></td>
        <td class="fw-bold">${escapeHtml(item.movie_title)}</td>
        <td><span class="badge badge-genre badge-${escapeHtml(item.genre)}">${escapeHtml(item.genre)}</span></td>
        <td><span class="badge badge-release-year">${item.release_year}</span></td>
        <td>
          <span class="star-rating">${stars}</span>
          <span class="fw-bold ms-1">(${item.rating})</span>
        </td>
        <td class="text-muted small">${formattedDate}</td>
        <td class="text-center">
          <button class="btn btn-sm btn-outline-warning me-1" onclick="openEditModal('${item._id}', '${escapeHtml(item.user_id)}', '${escapeHtml(item.movie_title)}', '${escapeHtml(item.genre)}', ${item.release_year}, ${item.rating})" title="Edit Document">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger" onclick="openDeleteModal('${item._id}', '${escapeHtml(item.movie_title)}', '${escapeHtml(item.user_id)}')" title="Delete Document">
            <i class="fa-solid fa-trash"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderPagination(p) {
  const info = document.getElementById("paginationInfo");
  const start = p.total_records === 0 ? 0 : (p.current_page - 1) * p.limit + 1;
  const end = Math.min(p.current_page * p.limit, p.total_records);
  info.innerText = `Showing ${start} - ${end} of ${p.total_records.toLocaleString()} rating records`;

  const container = document.getElementById("paginationControls");
  container.innerHTML = "";

  if (p.total_pages <= 1) return;

  // Prev Button
  const prevLi = document.createElement("li");
  prevLi.className = `page-item ${p.current_page === 1 ? 'disabled' : ''}`;
  prevLi.innerHTML = `<a class="page-link bg-dark border-secondary text-light" href="#" onclick="loadRatings(${p.current_page - 1}); return false;">Prev</a>`;
  container.appendChild(prevLi);

  // Page numbers
  const maxButtons = 5;
  let startPage = Math.max(1, p.current_page - 2);
  let endPage = Math.min(p.total_pages, startPage + maxButtons - 1);

  if (endPage - startPage < maxButtons - 1) {
    startPage = Math.max(1, endPage - maxButtons + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    const li = document.createElement("li");
    li.className = `page-item ${i === p.current_page ? 'active' : ''}`;
    li.innerHTML = `<a class="page-link ${i === p.current_page ? 'bg-primary border-primary' : 'bg-dark border-secondary'} text-light" href="#" onclick="loadRatings(${i}); return false;">${i}</a>`;
    container.appendChild(li);
  }

  // Next Button
  const nextLi = document.createElement("li");
  nextLi.className = `page-item ${p.current_page === p.total_pages ? 'disabled' : ''}`;
  nextLi.innerHTML = `<a class="page-link bg-dark border-secondary text-light" href="#" onclick="loadRatings(${p.current_page + 1}); return false;">Next</a>`;
  container.appendChild(nextLi);
}

// -----------------------------------------------------------------------------
// CRUD Form Handlers
// -----------------------------------------------------------------------------

async function submitAddRating(e) {
  e.preventDefault();

  const payload = {
    user_id: document.getElementById("addUserId").value.trim(),
    movie_title: document.getElementById("addMovieTitle").value.trim(),
    genre: document.getElementById("addGenre").value,
    release_year: parseInt(document.getElementById("addReleaseYear").value),
    rating: parseFloat(document.getElementById("addRating").value)
  };

  try {
    const res = await fetch("/api/ratings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.status === "success") {
      hideCustomModal('addRatingModal');
      document.getElementById("addRatingForm").reset();
      showToast(result.message, "success");
      loadRatings(1);
    } else {
      showToast(result.message, "danger");
    }
  } catch (err) {
    showToast("Failed to create rating document.", "danger");
  }
}

function openEditModal(id, user_id, title, genre, year, rating) {
  document.getElementById("editRatingId").value = id;
  document.getElementById("editUserId").value = user_id;
  document.getElementById("editMovieTitle").value = title;
  document.getElementById("editGenre").value = genre;
  document.getElementById("editReleaseYear").value = year;
  document.getElementById("editRating").value = rating.toFixed(1);

  showCustomModal('editRatingModal');
}

async function submitEditRating(e) {
  e.preventDefault();
  const id = document.getElementById("editRatingId").value;

  const payload = {
    user_id: document.getElementById("editUserId").value.trim(),
    movie_title: document.getElementById("editMovieTitle").value.trim(),
    genre: document.getElementById("editGenre").value,
    release_year: parseInt(document.getElementById("editReleaseYear").value),
    rating: parseFloat(document.getElementById("editRating").value)
  };

  try {
    const res = await fetch(`/api/ratings/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.status === "success") {
      hideCustomModal('editRatingModal');
      showToast(result.message, "success");
      loadRatings(currentPage);
    } else {
      showToast(result.message, "danger");
    }
  } catch (err) {
    showToast("Failed to update rating document.", "danger");
  }
}

let deleteTargetId = null;

function openDeleteModal(id, title, userId) {
  deleteTargetId = id;
  document.getElementById("deleteDocDetails").innerText = `"${title}" by User ${userId}`;
  showCustomModal('deleteRatingModal');
}

async function executeDelete() {
  if (!deleteTargetId) return;

  try {
    const res = await fetch(`/api/ratings/${deleteTargetId}`, {
      method: "DELETE"
    });
    const result = await res.json();

    hideCustomModal('deleteRatingModal');
    deleteTargetId = null;

    if (result.status === "success") {
      showToast(result.message, "success");
      loadRatings(currentPage);
    } else {
      showToast(result.message, "danger");
    }
  } catch (err) {
    showToast("Failed to delete rating document.", "danger");
  }
}

// Toast helper
function showToast(msg, type = "info") {
  const toastEl = document.getElementById("liveToast");
  const msgEl = document.getElementById("toastMessage");

  toastEl.className = `toast align-items-center text-white bg-${type === 'danger' ? 'danger' : 'primary'} border-0`;
  msgEl.innerText = msg;

  const toast = new bootstrap.Toast(toastEl);
  toast.show();
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
