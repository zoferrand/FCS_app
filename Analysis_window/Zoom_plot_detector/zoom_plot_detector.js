window.addEventListener('pywebviewready', () => {
    window.save_plot_detector = async function() {
        await window.pywebview.api.save_file('Opening_file_window/Detector_array.png','plot_detector.png');
    }
});

