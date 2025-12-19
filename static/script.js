/**
 * PercentExtractor Script
 * Handles file uploads, column selection, and processing requests.
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("PercentExtractor App Initialized");

    const fileInput = document.getElementById('file-input');
    const uploadStep = document.getElementById('upload-step');
    const columnStep = document.getElementById('column-step');
    const successStep = document.getElementById('success-step');
    const columnSelect = document.getElementById('column-select');
    const loadingOverlay = document.getElementById('loading-overlay');
    const dropZone = document.getElementById('drop-zone');
    const processBtn = document.getElementById('process-btn');
    const restartBtn = document.getElementById('restart-btn');
    const loadingText = document.getElementById('loading-text');

    let selectedFile = null;

    // --- File Interaction Logic ---

    // Trigger file browser on click
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
            dropZone.style.borderColor = 'var(--primary)';
            dropZone.style.background = 'rgba(99, 102, 241, 0.1)';
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
            dropZone.style.borderColor = 'var(--glass-border)';
            dropZone.style.background = 'transparent';
        });
    });

    // Handle File Selection (from browser or drop)
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    /**
     * Handles the initial file upload and column extraction.
     * @param {File} file 
     */
    async function handleFile(file) {
        console.log("Handling file:", file.name);
        if (!file.name.toLowerCase().endsWith('.xlsx')) {
            alert("Please select a .xlsx file");
            return;
        }

        selectedFile = file;
        loadingOverlay.classList.remove('hidden');
        if (loadingText) loadingText.innerText = "Reading file columns...";

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (response.ok) {
                columnSelect.innerHTML = '<option value="" disabled selected>Choose a column...</option>';
                data.columns.forEach(col => {
                    const opt = document.createElement('option');
                    opt.value = opt.textContent = col;
                    columnSelect.appendChild(opt);
                });
                uploadStep.classList.add('hidden');
                columnStep.classList.remove('hidden');

                // Entrance animation
                columnStep.style.opacity = 0;
                setTimeout(() => {
                    columnStep.style.transition = 'opacity 0.5s ease';
                    columnStep.style.opacity = 1;
                }, 50);

            } else {
                alert(data.error || "Failed to load columns");
            }
        } catch (err) {
            alert("Server error: " + err.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    }

    // Process Button
    processBtn.addEventListener('click', async () => {
        const col = columnSelect.value;
        if (!col) {
            alert("Please select a column");
            return;
        }

        loadingOverlay.classList.remove('hidden');
        if (loadingText) loadingText.innerText = "Processing extraction logic...";

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('column', col);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `processed_${selectedFile.name}`;
                document.body.appendChild(a);
                a.click();
                a.remove();

                // Show success feedback
                columnStep.classList.add('hidden');
                successStep.classList.remove('hidden');

                // Appearance animation
                successStep.style.opacity = 0;
                setTimeout(() => {
                    successStep.style.transition = 'opacity 0.5s ease';
                    successStep.style.opacity = 1;
                }, 50);

            } else {
                const err = await response.json();
                alert("Processing failed: " + err.error);
            }
        } catch (err) {
            alert("Error: " + err.message);
        } finally {
            loadingOverlay.classList.add('hidden');
        }
    });

    // Restart Button
    restartBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = "";
        successStep.classList.add('hidden');
        uploadStep.classList.remove('hidden');

        // Reset drop zone appearance
        dropZone.style.borderColor = 'var(--glass-border)';
        dropZone.style.background = 'transparent';
    });
});
