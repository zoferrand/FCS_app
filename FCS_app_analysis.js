window.addEventListener('pywebviewready', () => {
    window.go_to_pick_file = async function() {
        await window.pywebview.api.open_main_window();
    }
});