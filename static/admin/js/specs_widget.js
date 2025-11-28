/* Specs Widget JavaScript */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        setupSpecsWidget();
    });

    function setupSpecsWidget() {
        // Find all add buttons
        const addButtons = document.querySelectorAll('.spec-add');
        
        addButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const fieldName = this.getAttribute('data-name');
                const specsList = this.previousElementSibling;
                
                // Create new spec row
                const newRow = document.createElement('div');
                newRow.className = 'spec-row';
                newRow.innerHTML = `
                    <input type="text" name="${fieldName}_key" value="" placeholder="Tên thông số" class="spec-key">
                    <input type="text" name="${fieldName}_value" value="" placeholder="Giá trị" class="spec-value">
                    <button type="button" class="spec-remove" title="Xóa">🗑</button>
                `;
                
                specsList.appendChild(newRow);
                
                // Focus on the new key input
                const newKeyInput = newRow.querySelector('.spec-key');
                newKeyInput.focus();
                
                // Setup remove button for the new row
                setupRemoveButton(newRow.querySelector('.spec-remove'));
            });
        });

        // Setup existing remove buttons
        const removeButtons = document.querySelectorAll('.spec-remove');
        removeButtons.forEach(setupRemoveButton);
    }

    function setupRemoveButton(button) {
        button.addEventListener('click', function() {
            const row = this.parentElement;
            
            // Confirm before removing
            if (confirm('Xóa thông số này?')) {
                row.remove();
            }
        });
    }

    // Validation before form submit
    document.addEventListener('submit', function(e) {
        const specsEditors = document.querySelectorAll('.specs-editor');
        
        specsEditors.forEach(function(editor) {
            const rows = editor.querySelectorAll('.spec-row');
            let hasEmptyKey = false;
            
            rows.forEach(function(row) {
                const keyInput = row.querySelector('.spec-key');
                const valueInput = row.querySelector('.spec-value');
                
                if (keyInput.value.trim() === '' && valueInput.value.trim() !== '') {
                    hasEmptyKey = true;
                    keyInput.style.borderColor = '#dc2626';
                    keyInput.style.backgroundColor = '#fee2e2';
                }
            });
            
            if (hasEmptyKey) {
                e.preventDefault();
                alert('Vui lòng điền tên thông số hoặc xóa dòng trống!');
            }
        });
    });

    // Clear error styling on input
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('spec-key') || e.target.classList.contains('spec-value')) {
            e.target.style.borderColor = '';
            e.target.style.backgroundColor = '';
        }
    });

    console.log('✅ Specs Widget JS loaded successfully');
})();
