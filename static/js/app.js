// ============================================================
// API BASE URL
// ============================================================

const API_BASE = '/api';

// ============================================================
// STATE MANAGEMENT
// ============================================================

let movies = [];
let selectedMovie = null;
let seatMap = [];
let selectedSeat = { row: null, col: null };

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Cinema Booking System initialized');
    loadMovies();
});

// ============================================================
// API FUNCTIONS
// ============================================================

async function loadMovies() {
    try {
        const response = await fetch(`${API_BASE}/movies`);
        const data = await response.json();

        if (data.success) {
            movies = data.movies;
            renderMovieCards(movies);
        } else {
            showNotification('Failed to load movies', 'error');
        }
    } catch (error) {
        console.error('Error loading movies:', error);
        showNotification('Failed to load movies', 'error');
    }
}

async function fetchSeatsForMovie(movieId) {
    try {
        const response = await fetch(`${API_BASE}/seats/${movieId}`);
        const data = await response.json();

        if (data.success) {
            return data.seats;
        } else {
            throw new Error(data.error || 'Failed to fetch seats');
        }
    } catch (error) {
        console.error('Error fetching seats:', error);
        showNotification('Failed to load seats', 'error');
        return null;
    }
}

async function bookSeatAPI(movieId, row, col, customerName, customerEmail, customerPhone) {
    try {
        const response = await fetch(`${API_BASE}/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                movie_id: movieId,
                row: row,
                col: col,
                customer_name: customerName,
                customer_email: customerEmail,
                customer_phone: customerPhone
            })
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error booking seat:', error);
        return { success: false, message: 'Network error' };
    }
}

// ============================================================
// UI RENDERING - MOVIES
// ============================================================

function renderMovieCards(movies) {
    const movieCards = document.getElementById('movieCards');
    movieCards.innerHTML = '';

    movies.forEach(movie => {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.onclick = () => selectMovie(movie.id);

        card.innerHTML = `
            <div class="movie-emoji">${movie.poster_emoji}</div>
            <h3 class="movie-title">${movie.title}</h3>
            <div class="movie-details">
                <div class="movie-detail">
                    <span><strong>Genre:</strong></span>
                    <span>${movie.genre}</span>
                </div>
                <div class="movie-detail">
                    <span><strong>Duration:</strong></span>
                    <span>${movie.duration}</span>
                </div>
                <div class="movie-detail">
                    <span><strong>Showtime:</strong></span>
                    <span>${movie.showtime}</span>
                </div>
            </div>
        `;

        movieCards.appendChild(card);
    });
}

async function selectMovie(movieId) {
    selectedMovie = movies.find(m => m.id === movieId);

    if (!selectedMovie) return;

    // Update UI to show selected movie
    document.querySelectorAll('.movie-card').forEach(card => {
        card.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    // Show seat selection section
    document.getElementById('screenContainer').style.display = 'flex';
    document.getElementById('seatGridContainer').style.display = 'block';
    document.getElementById('legend').style.display = 'flex';
    document.getElementById('actions').style.display = 'flex';

    // Update title
    document.getElementById('selectedMovieTitle').textContent = `${selectedMovie.poster_emoji} ${selectedMovie.title}`;

    // Load seats for this movie
    await refreshSeats();

    // Start auto-refresh
    if (window.refreshInterval) {
        clearInterval(window.refreshInterval);
    }
    window.refreshInterval = setInterval(refreshSeats, 5000);
}

function changeMovie() {
    // Clear selection
    selectedMovie = null;
    selectedSeat = { row: null, col: null };

    // Hide seat selection
    document.getElementById('screenContainer').style.display = 'none';
    document.getElementById('seatGridContainer').style.display = 'none';
    document.getElementById('legend').style.display = 'none';
    document.getElementById('actions').style.display = 'none';

    // Clear active movie
    document.querySelectorAll('.movie-card').forEach(card => {
        card.classList.remove('active');
    });

    // Stop auto-refresh
    if (window.refreshInterval) {
        clearInterval(window.refreshInterval);
    }
}

// ============================================================
// UI RENDERING - SEATS
// ============================================================

function renderSeats(seats) {
    const seatGrid = document.getElementById('seatGrid');
    seatGrid.innerHTML = '';

    seats.forEach((row, rowIndex) => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'seat-row';

        // Row label
        const label = document.createElement('div');
        label.className = 'row-label';
        label.textContent = `Row ${rowIndex + 1}`;
        rowDiv.appendChild(label);

        // Seat buttons container
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'seat-buttons';

        row.forEach((status, colIndex) => {
            const button = document.createElement('button');
            button.className = `seat ${status === 0 ? 'available' : 'booked'}`;
            button.textContent = `${rowIndex}-${colIndex}`;
            button.dataset.row = rowIndex;
            button.dataset.col = colIndex;

            if (status === 0) {
                button.onclick = () => handleSeatClick(rowIndex, colIndex);
            } else {
                button.disabled = true;
            }

            buttonsDiv.appendChild(button);
        });

        rowDiv.appendChild(buttonsDiv);
        seatGrid.appendChild(rowDiv);
    });
}

// ============================================================
// EVENT HANDLERS
// ============================================================

async function handleSeatClick(row, col) {
    if (!selectedMovie) {
        showNotification('Please select a movie first', 'error');
        return;
    }

    selectedSeat = { row, col };
    showBookingModal(row, col);
}

async function refreshSeats() {
    if (!selectedMovie) return;

    const seats = await fetchSeatsForMovie(selectedMovie.id);

    if (seats) {
        seatMap = seats;
        renderSeats(seats);
    }
}

// ============================================================
// MODAL FUNCTIONS
// ============================================================

function showBookingModal(row, col) {
    const modal = document.getElementById('bookingModal');
    document.getElementById('modalMovieTitle').textContent = selectedMovie.title;
    document.getElementById('modalRow').textContent = row + 1;
    document.getElementById('modalCol').textContent = col + 1;

    // Reset form
    document.getElementById('bookingForm').reset();

    modal.style.display = 'block';
}

function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    modal.style.display = 'none';
    selectedSeat = { row: null, col: null };
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('bookingModal');
    if (event.target == modal) {
        closeBookingModal();
    }
}

async function submitBooking(event) {
    event.preventDefault();

    const form = event.target;
    const customerName = form.customerName.value.trim();
    const customerEmail = form.customerEmail.value.trim();
    const customerPhone = form.customerPhone.value.trim();

    // Validation
    if (!customerName || !customerEmail || !customerPhone) {
        showNotification('Please fill all fields', 'error');
        return;
    }

    if (!validateEmail(customerEmail)) {
        showNotification('Please enter a valid email', 'error');
        return;
    }

    if (!validatePhone(customerPhone)) {
        showNotification('Please enter a valid phone number', 'error');
        return;
    }

    // Book the seat
    const result = await bookSeatAPI(
        selectedMovie.id,
        selectedSeat.row,
        selectedSeat.col,
        customerName,
        customerEmail,
        customerPhone
    );

    if (result.success) {
        showNotification(`✅ ${result.message}`, 'success');
        closeBookingModal();
        await refreshSeats();
    } else {
        showNotification(`❌ ${result.message}`, 'error');
        await refreshSeats();
    }
}

// ============================================================
// VALIDATION
// ============================================================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    // Indonesian phone number format
    const re = /^(\+62|62|0)[0-9]{9,12}$/;
    return re.test(phone.replace(/[\s-]/g, ''));
}

// ============================================================
// NOTIFICATIONS
// ============================================================

function showNotification(message, type = 'info') {
    // Simple alert for now - can be enhanced with toast notifications
    if (type === 'success') {
        alert(message);
    } else if (type === 'error') {
        alert(message);
    } else {
        alert(message);
    }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function getSeatStatus(row, col) {
    if (seatMap.length > 0 && seatMap[row] && seatMap[row][col] !== undefined) {
        return seatMap[row][col];
    }
    return null;
}

// Export functions for global access
window.refreshSeats = refreshSeats;
window.changeMovie = changeMovie;
window.closeBookingModal = closeBookingModal;
window.submitBooking = submitBooking;
