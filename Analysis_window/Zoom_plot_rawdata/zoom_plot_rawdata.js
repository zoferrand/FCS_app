const inputFirstTp = document.getElementById("textbox_first_tp");
const inputLastTp = document.getElementById("textbox_last_tp");
const divTotTp = document.getElementById("text_total_tp");


window.addEventListener('pywebviewready', () => {
    window.save_plot_rawdata = async function() {
        await window.pywebview.api.save_file('Opening_file_window/Int_fluctuations.png','plot_rawdata.png');
    }
});

window.addEventListener('pywebviewready', () => {
    window.updatePlotFirstTp = async function() {
        const valueFirstTp = inputFirstTp.value;
        const valueLastTp = inputLastTp.value;
        const base64Image = await window.pywebview.api.update_crop_values(valueFirstTp, valueLastTp);
        
        // Build the data URL
        const imageUrl = `data:image/png;base64,${base64Image}`;

        // Replace CSS background dynamically
        const zoomPlotDiv = document.querySelector('.zoom_plot');
        zoomPlotDiv.style.backgroundImage = `url('${imageUrl}')`;
    }
});

window.addEventListener('pywebviewready', () => {
    window.updatePlotLastTp = async function() {
        const valueFirstTp = inputFirstTp.value;
        const valueLastTp = inputLastTp.value;
        const base64Image = await window.pywebview.api.update_crop_values(valueFirstTp, valueLastTp);
        
        // Build the data URL
        const imageUrl = `data:image/png;base64,${base64Image}`;

        // Replace CSS background dynamically
        const zoomPlotDiv = document.querySelector('.zoom_plot');
        zoomPlotDiv.style.backgroundImage = `url('${imageUrl}')`;
    }
});

window.addEventListener('pywebviewready', () => {
    window.plotCroppedData = async function() {
        const valueFirstTp = inputFirstTp.value;
        const valueLastTp = inputLastTp.value;
        const base64Image = await window.pywebview.api.plot_cropped_data(valueFirstTp, valueLastTp);
        
        // Build the data URL
        const imageUrl = `data:image/png;base64,${base64Image}`;

        // Replace CSS background dynamically
        const zoomPlotDiv = document.querySelector('.zoom_plot');
        zoomPlotDiv.style.backgroundImage = `url('${imageUrl}')`;
    }
});

window.addEventListener('pywebviewready', () => {
    window.plotUncutData = async function() {
        const valueFirstTp = inputFirstTp.value;
        const valueLastTp = inputLastTp.value;
        const base64Image = await window.pywebview.api.plot_uncut_data();
        
        // Build the data URL
        const imageUrl = `data:image/png;base64,${base64Image}`;

        // Replace CSS background dynamically
        const zoomPlotDiv = document.querySelector('.zoom_plot');
        zoomPlotDiv.style.backgroundImage = `url('${imageUrl}')`;
    }
});


