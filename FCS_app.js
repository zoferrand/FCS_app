let selectedFilePath = null;
const dropArea = document.getElementById("dropbox");
const dropboxText = document.getElementById("dropbox_text");
const fileNameText = document.getElementById("name_of_file")
const confirmButton = document.getElementById("confirm_button");

const fileName = localStorage.getItem("selectedFile");

window.addEventListener('pywebviewready', () => {
    window.selectFile = async function(){

        const path = await window.pywebview.api.open_file_dialog();
        localStorage.setItem("fileSelected", "False");
        if (path) {
            
            selectedFilePath = path
            const fileName = path.split(/[\\/]/).pop();  // get last part of path
            const extension = fileName.split('.').pop();
            localStorage.setItem("selectedFile", fileName);
            if (extension === `czi`){
                fileNameText.hidden = false
                fileNameText.innerHTML = `${fileName}`;
                confirmButton.hidden = false;
                dropArea.style.border = "25px double #F1BCCD";
            }
            else {
                selectedFilePath = null
                fileNameText.hidden = false
                dropboxText.hidden = true
                fileNameText.innerHTML = `Please provide a .CZI file`;
                confirmButton.hidden = true;
                dropArea.style.border = "9px solid rgba(255, 217, 185, 0.7)";
            }
        }
    }
});

window.addEventListener('pywebviewready', () => {
    window.confirmFile = async function() {
        if (!selectedFilePath) return; // Stops the execution if there's no file to analyse
        localStorage.setItem("fileSelected", "True");
        const result = await window.pywebview.api.open_file(selectedFilePath);
        console.log(result);

    }
});

window.addEventListener('pywebviewready', () => {
    window.go_to_analysis_file = async function() {
        await window.pywebview.api.open_analysis_window();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const fileName = localStorage.getItem("selectedFile");
    const fileSelected = localStorage.getItem("fileSelected");

    if (fileSelected === "True" && fileName) {
        fileNameText.hidden = false;
        fileNameText.innerHTML = `${fileName}`;
        confirmButton.hidden = false;
        dropArea.style.border = "25px double #F1BCCD";
    }
});
