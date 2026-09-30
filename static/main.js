function openFileInput(inputId = 'file-upload') {
    const fileInput = document.getElementById(inputId);
    if (fileInput) {
        fileInput.click();
    }
}

function openPhotoInput(inputId = 'photo-upload') {
    const fileInput = document.getElementById(inputId);
    if (fileInput) {
        fileInput.click();
    }
}

function addPhotoInput(inputId = 'photo-add') {
    const fileInput = document.getElementById(inputId);
    if (fileInput) {
        fileInput.click();
    }
}

function saveTask(checkbox) {
    const taskId = checkbox.getAttribute('data-task-id');
    const status = checkbox.checked ? 'checked' : 'unchecked';
    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('status', status);
    fetch('/done', {
        method: 'POST',
        body: formData
    })
    .then(response => { if (!response.ok) checkbox.checked = !checkbox.checked; })
    .catch(error => { checkbox.checked = !checkbox.checked; });
}

document.querySelectorAll('.task_shown_link').forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const task_id = this.dataset.taskId;
        const targetPage = this.getAttribute('href');
        window.location.href = `${targetPage}?task_id=${task_id}`;
    });
});

document.querySelectorAll('.send_the_formula').forEach(function(link) {
    link.addEventListener('click', function(event) {
        event.preventDefault();
        const inputField = document.querySelector('#enter_formula');
        const formula = inputField ? inputField.value : ''; 
        const targetPage = this.dataset.page;

        if (targetPage) {
            window.location.href = `${targetPage}?formula=${formula}`;
        }
    });
});

document.querySelectorAll('.send_the_formula_input').forEach(function(inputField) {
    inputField.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const formula = this.value || ''; 
            const targetPage = this.dataset.page;

            if (targetPage) {
                window.location.href = `${targetPage}?formula=${formula}`;
            }
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form.submit');
    if (form) {
        form.addEventListener('submit', function(event) {
            const isAddButton = event.submitter && event.submitter.id === 'add_formula';
            if (!isAddButton) {
                event.preventDefault();
                const inputField = document.querySelector('#enter_formula');
                const formula = inputField ? inputField.value.trim() : '';
                const targetPage = '/search';
                const finalUrl = `${targetPage}?formula=${formula}`;
                window.location.href = finalUrl;
            }
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const messages = document.querySelectorAll('.flash-toast');
    messages.forEach(msg => {
        const duration = parseInt(msg.getAttribute('data-timeout')) || 3000;
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-20px)';
            setTimeout(() => msg.remove(), 500); 
        }, duration);
    });
});

document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'show_the_answer') {
        e.preventDefault();
        fetch('/show_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                const answerContainer = document.getElementById('answer_container');
                const btn = e.target;
                if (data.show_answer) {
                    if (answerContainer) answerContainer.style.display = 'block';
                    btn.textContent = 'Сховати відповідь';
                } else {
                    if (answerContainer) answerContainer.style.display = 'none';
                    btn.textContent = 'Показати відповідь';
                }
            }
        })
        .catch(err => console.error(err));
    }
});

document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'show_the_note') {
        e.preventDefault();
        fetch('/show_note', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                const noteContainer = document.getElementById('note_container');
                const btn = e.target;
                if (data.show_note) {
                    if (noteContainer) noteContainer.style.display = 'block';
                    btn.textContent = 'Сховати пояснення';
                } else {
                    if (noteContainer) noteContainer.style.display = 'none';
                    btn.textContent = 'Показати пояснення';
                }
            }
        })
        .catch(err => console.error(err));
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const filters = document.getElementById("filters");
    const toggle = document.getElementById("toggle_filters");
    if (!filters || !toggle) return;
    toggle.addEventListener("click", () => {
        filters.classList.toggle("collapsed");
    });
});


document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'next_photo') {
        e.preventDefault();
        navigatePhoto('/next_photo');
    }
    if (e.target && e.target.id === 'previous_photo') {
        e.preventDefault();
        navigatePhoto('/previous_photo');
    }
});
function navigatePhoto(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                const photoImg = document.getElementById('image');
                if (photoImg && data.photo_url) {
                    photoImg.src = data.photo_url;
                }
                const nextBtn = document.getElementById('next_photo');
                const prevBtn = document.getElementById('previous_photo');
                if (nextBtn) {
                    updateButtonState(nextBtn, data.blocked_next_button);
                }
                if (prevBtn) {
                    updateButtonState(prevBtn, data.blocked_previous_button);
                }
            }
        })
        .catch(err => console.error('Помилка оновлення фото:', err));
}
function updateButtonState(btn, isBlocked) {
    btn.disabled = isBlocked;
    btn.style.opacity = isBlocked ? '0.5' : '1';
    btn.style.cursor = isBlocked ? 'not-allowed' : 'pointer';
    btn.style.pointerEvents = isBlocked ? 'none' : 'auto';
}