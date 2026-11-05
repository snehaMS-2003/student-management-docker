// Global API utilities and helper functions

// Toast / Alert notification banner helper
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;

    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
            <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto dismiss after 4 seconds
    setTimeout(() => {
        const el = document.getElementById(alertId);
        if (el) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert.close();
        }
    }, 4000);
}

// Format Date string helper
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    return dateStr;
}

// ----------------- Dashboard Logic -----------------
async function loadDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            const totalStudentsEl = document.getElementById('stat-total-students');
            const totalDepartmentsEl = document.getElementById('stat-total-departments');
            const recentStudentsTable = document.getElementById('recent-students-body');

            if (totalStudentsEl) totalStudentsEl.textContent = data.total_students;
            if (totalDepartmentsEl) totalDepartmentsEl.textContent = data.total_departments;

            if (recentStudentsTable) {
                if (data.recent_students.length === 0) {
                    recentStudentsTable.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">No students found. Add your first student!</td></tr>`;
                } else {
                    recentStudentsTable.innerHTML = data.recent_students.map(s => `
                        <tr>
                            <td><span class="badge bg-light text-dark border">#${s.id}</span></td>
                            <td class="fw-semibold">${s.name}</td>
                            <td>${s.email}</td>
                            <td><span class="badge bg-primary-subtle text-primary">${s.department}</span></td>
                            <td>${s.gender}</td>
                            <td><small class="text-muted">${s.created_at}</small></td>
                        </tr>
                    `).join('');
                }
            }
        } else {
            showAlert(result.message || 'Error loading dashboard statistics', 'danger');
        }
    } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        showAlert('Could not connect to server to fetch dashboard metrics.', 'danger');
    }
}

// ----------------- Students Table Logic -----------------
let currentDeleteStudentId = null;

async function loadStudents(searchQuery = '') {
    const tableBody = document.getElementById('students-table-body');
    const studentCountEl = document.getElementById('student-count-badge');
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4"><div class="spinner-border text-primary spinner-border-sm me-2" role="status"></div> Loading student records...</td></tr>`;

    try {
        const url = searchQuery ? `/api/students?search=${encodeURIComponent(searchQuery)}` : '/api/students';
        const response = await fetch(url);
        const result = await response.json();

        if (result.success) {
            const students = result.data;
            if (studentCountEl) studentCountEl.textContent = `${students.length} Total`;

            if (students.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-5 text-muted">
                            <i class="bi bi-person-x fs-1 d-block mb-2 text-secondary"></i>
                            ${searchQuery ? 'No student records match your search query.' : 'No students registered yet.'}
                        </td>
                    </tr>
                `;
                return;
            }

            tableBody.innerHTML = students.map(student => `
                <tr>
                    <td><span class="fw-bold text-secondary">#${student.id}</span></td>
                    <td>
                        <div class="fw-semibold">${student.name}</div>
                    </td>
                    <td><a href="mailto:${student.email}" class="text-decoration-none text-muted">${student.email}</a></td>
                    <td>${student.phone}</td>
                    <td><span class="badge bg-info-subtle text-info-emphasis border border-info-subtle">${student.department}</span></td>
                    <td>
                        <span class="badge ${student.gender === 'Female' ? 'bg-danger-subtle text-danger' : student.gender === 'Male' ? 'bg-primary-subtle text-primary' : 'bg-secondary-subtle text-secondary'}">
                            ${student.gender}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <a href="/students/edit/${student.id}" class="btn btn-outline-primary" title="Edit Student">
                                <i class="bi bi-pencil-square"></i> Edit
                            </a>
                            <button type="button" class="btn btn-outline-danger" onclick="confirmDeleteStudent(${student.id}, '${student.name.replace(/'/g, "\\'")}')" title="Delete Student">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        } else {
            showAlert(result.message || 'Failed to fetch students.', 'danger');
        }
    } catch (err) {
        console.error('Error fetching students:', err);
        showAlert('Unable to connect to the backend server.', 'danger');
    }
}

// Confirm Delete Modal setup
function confirmDeleteStudent(id, name) {
    currentDeleteStudentId = id;
    const nameEl = document.getElementById('delete-student-name');
    if (nameEl) nameEl.textContent = name;

    const modalEl = document.getElementById('deleteModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
}

// Perform Delete Request
async function executeDeleteStudent() {
    if (!currentDeleteStudentId) return;

    const deleteBtn = document.getElementById('confirm-delete-btn');
    if (deleteBtn) {
        deleteBtn.disabled = true;
        deleteBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Deleting...`;
    }

    try {
        const response = await fetch(`/api/students/${currentDeleteStudentId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        const modalEl = document.getElementById('deleteModal');
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }

        if (result.success) {
            showAlert(result.message, 'success');
            loadStudents(); // Refresh table
        } else {
            showAlert(result.message || 'Could not delete student.', 'danger');
        }
    } catch (err) {
        console.error('Delete error:', err);
        showAlert('Failed to connect to server to delete student.', 'danger');
    } finally {
        currentDeleteStudentId = null;
        if (deleteBtn) {
            deleteBtn.disabled = false;
            deleteBtn.innerHTML = `Delete Student`;
        }
    }
}

// ----------------- Student Form Logic (Create & Edit) -----------------
async function initStudentForm(studentId) {
    const form = document.getElementById('student-form');
    if (!form) return;

    if (studentId) {
        // Edit mode: fetch existing details
        try {
            const response = await fetch(`/api/students/${studentId}`);
            const result = await response.json();

            if (result.success) {
                const s = result.data;
                document.getElementById('name').value = s.name || '';
                document.getElementById('email').value = s.email || '';
                document.getElementById('phone').value = s.phone || '';
                document.getElementById('department').value = s.department || '';
                document.getElementById('gender').value = s.gender || '';
                document.getElementById('date_of_birth').value = s.date_of_birth || '';
            } else {
                showAlert(result.message || 'Student not found', 'danger');
            }
        } catch (err) {
            console.error('Error fetching student details:', err);
            showAlert('Could not load student information for editing.', 'danger');
        }
    }

    // Form submit listener
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Clear previous validation states
        clearFormErrors();

        const payload = {
            name: document.getElementById('name').value.trim(),
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            department: document.getElementById('department').value.trim(),
            gender: document.getElementById('gender').value,
            date_of_birth: document.getElementById('date_of_birth').value
        };

        const submitBtn = document.getElementById('submit-btn');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Saving...`;

        const isEdit = Boolean(studentId);
        const url = isEdit ? `/api/students/${studentId}` : '/api/students';
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                showAlert(result.message || 'Student saved successfully!', 'success');
                // Redirect back to student list after short delay
                setTimeout(() => {
                    window.location.href = '/students';
                }, 900);
            } else if (response.status === 422 && result.errors) {
                // Highlight validation errors
                for (const [field, errorMsg] of Object.entries(result.errors)) {
                    showFieldError(field, errorMsg);
                }
                showAlert(result.message || 'Please fix the errors in the form.', 'danger');
            } else {
                showAlert(result.message || 'Failed to save student.', 'danger');
            }
        } catch (err) {
            console.error('Error saving student:', err);
            showAlert('Error communicating with server.', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

function showFieldError(field, message) {
    const input = document.getElementById(field);
    if (!input) return;

    input.classList.add('is-invalid');
    const feedbackEl = document.getElementById(`${field}-feedback`);
    if (feedbackEl) {
        feedbackEl.textContent = message;
    }
}

function clearFormErrors() {
    const inputs = document.querySelectorAll('.is-invalid');
    inputs.forEach(input => input.classList.remove('is-invalid'));
    const feedbacks = document.querySelectorAll('.invalid-feedback');
    feedbacks.forEach(el => el.textContent = '');
}

