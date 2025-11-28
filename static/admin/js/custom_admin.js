/* Simple Admin JavaScript for ComputerStore Admin */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        
        // Confirm before delete
        setupDeleteConfirmation();
        
        // Keyboard shortcuts
        setupKeyboardShortcuts();
        
        console.log('✅ ComputerStore Admin JS loaded successfully');
    });

    // Confirm before delete
    function setupDeleteConfirmation() {
        // Delete links
        const deleteLinks = document.querySelectorAll('.deletelink, .deletelink-box a');
        deleteLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                if (!confirm('⚠️ Bạn có chắc chắn muốn xóa? Hành động này không thể hoàn tác!')) {
                    e.preventDefault();
                }
            });
        });

        // Delete actions in dropdown
        const actionSelect = document.querySelector('select[name="action"]');
        if (actionSelect) {
            actionSelect.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                if (selectedOption.value.includes('delete')) {
                    const goButton = document.querySelector('.button[type="submit"][name="index"]');
                    if (goButton) {
                        goButton.addEventListener('click', function(e) {
                            const checkedItems = document.querySelectorAll('input[name="_selected_action"]:checked');
                            if (checkedItems.length > 0) {
                                if (!confirm(`⚠️ Bạn có chắc chắn muốn xóa ${checkedItems.length} mục đã chọn? Hành động này không thể hoàn tác!`)) {
                                    e.preventDefault();
                                }
                            }
                        });
                    }
                }
            });
        }
    }

    // Keyboard shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + S: Save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const saveButton = document.querySelector('input[name="_save"]');
                if (saveButton) {
                    saveButton.click();
                }
            }
            
            // Ctrl/Cmd + Enter: Save and continue
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const saveContinueButton = document.querySelector('input[name="_continue"]');
                if (saveContinueButton) {
                    saveContinueButton.click();
                }
            }
        });
    }

})();
