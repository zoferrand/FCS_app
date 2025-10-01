window.addEventListener('pywebviewready', () => {
    window.go_to_pick_file = async function() {
        await window.pywebview.api.open_main_window();
    }
});

window.addEventListener('pywebviewready', () => {
    window.zoom_plot_detector = async function() {
        await window.pywebview.api.open_zoom_plot_detector();
    }
});

window.addEventListener('pywebviewready', () => {
    window.zoom_plot_rawdata = async function() {
        await window.pywebview.api.open_zoom_plot_rawdata();
    }
});
