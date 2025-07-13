// Main JavaScript file for MentorsCue
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive elements
    initializeFormValidation();
    initializeTooltips();
    initializeConfirmDialogs();
    initializeTableSorting();
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

// Form Validation Enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Highlight invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    
                    // Remove invalid class when user starts typing
                    field.addEventListener('input', function() {
                        if (field.checkValidity()) {
                            field.classList.remove('is-invalid');
                            field.classList.add('is-valid');
                        }
                    });
                });
            } else {
                // Add loading state to submit button
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.classList.add('loading');
                    submitBtn.disabled = true;
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Initialize Bootstrap Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Enhanced Confirm Dialogs
function initializeConfirmDialogs() {
    const deleteLinks = document.querySelectorAll('a[onclick*="confirm"]');
    
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            
            const action = this.textContent.trim();
            const itemName = this.closest('tr')?.querySelector('td')?.textContent?.trim() || 'this item';
            
            const confirmDialog = createCustomConfirmDialog(
                'Confirm Action',
                `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
                'Delete',
                'Cancel'
            );
            
            confirmDialog.then(result => {
                if (result) {
                    // Add loading state
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    this.classList.add('disabled');
                    
                    // Navigate to the delete URL
                    window.location.href = this.href;
                }
            });
        });
    });
}

// Custom Confirm Dialog
function createCustomConfirmDialog(title, message, confirmText, cancelText) {
    return new Promise((resolve) => {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="confirmModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                            <button type="button" class="btn btn-danger" id="confirmBtn">${confirmText}</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('confirmModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        const confirmBtn = document.getElementById('confirmBtn');
        
        confirmBtn.addEventListener('click', () => {
            modal.hide();
            resolve(true);
        });
        
        document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
            document.getElementById('confirmModal').remove();
            resolve(false);
        });
        
        modal.show();
    });
}

// Table Sorting Enhancement
function initializeTableSorting() {
    const tables = document.querySelectorAll('table.table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('thead th');
        
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('.btn')) {
                header.style.cursor = 'pointer';
                header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
                
                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            }
        });
    });
}

// Sort Table Function
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelector(`thead th:nth-child(${columnIndex + 1})`);
    const sortIcon = header.querySelector('i');
    
    // Determine sort direction
    const isAscending = sortIcon.classList.contains('fa-sort') || sortIcon.classList.contains('fa-sort-down');
    
    // Reset all sort icons
    table.querySelectorAll('thead th i').forEach(icon => {
        icon.className = 'fas fa-sort text-muted';
    });
    
    // Set current sort icon
    sortIcon.className = isAscending ? 'fas fa-sort-up text-primary' : 'fas fa-sort-down text-primary';
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Compare as strings
        return isAscending 
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });
    
    // Reorder DOM
    rows.forEach(row => tbody.appendChild(row));
}

// Auto-fill today's date in date inputs
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
});

// Subject suggestions for forms
const commonSubjects = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'English',
    'Hindi',
    'History',
    'Geography',
    'Computer Science',
    'Economics',
    'Accountancy',
    'Business Studies'
];

// Add subject suggestions to subject input fields
document.addEventListener('DOMContentLoaded', function() {
    const subjectInputs = document.querySelectorAll('input[name="subject"], input[name="subjects"]');
    
    subjectInputs.forEach(input => {
        // Create datalist for suggestions
        const datalistId = 'subjects-list';
        let datalist = document.getElementById(datalistId);
        
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = datalistId;
            
            commonSubjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject;
                datalist.appendChild(option);
            });
            
            document.body.appendChild(datalist);
        }
        
        input.setAttribute('list', datalistId);
    });
});

// Enhanced form feedback
function showFormFeedback(message, type = 'success') {
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Print functionality for tables
function printTable(tableId) {
    const table = document.getElementById(tableId);
    if (table) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>MentorsCue - Print</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        @media print {
                            .btn { display: none !important; }
                            body { font-size: 12px; }
                        }
                    </style>
                </head>
                <body>
                    <div class="container mt-3">
                        <h2>MentorsCue - Attendance Records</h2>
                        ${table.outerHTML}
                    </div>
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit forms
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const form = event.target.closest('form');
        if (form) {
            event.preventDefault();
            form.submit();
        }
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});
