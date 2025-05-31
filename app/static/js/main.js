document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[data-ajax="true"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const url = form.getAttribute('action');
            const method = form.getAttribute('method') || 'POST';
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    showAlert('danger', data.message);
                }
            })
            .catch(error => {
                showAlert('danger', 'An error occurred. Please try again.');
                console.error('Error:', error);
            });
        });
    });

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    document.querySelectorAll('input[type="file"]').forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                const preview = document.querySelector(`#${input.dataset.preview}`);
                
                reader.onload = function(e) {
                    preview.src = e.target.result;
                };
                
                reader.readAsDataURL(file);
            }
        });
    });

    document.querySelectorAll('[data-add-field]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const template = document.querySelector(button.dataset.template);
            const container = document.querySelector(button.dataset.container);
            
            if (template && container) {
                const clone = template.content.cloneNode(true);
                container.appendChild(clone);
            }
        });
    });

    document.querySelectorAll('[data-remove-field]').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const field = button.closest(button.dataset.removeField);
            if (field) {
                field.remove();
            }
        });
    });
}); 