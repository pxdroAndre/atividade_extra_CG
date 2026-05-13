const imageInput = document.getElementById('imageInput');
const workspace = document.getElementById('workspace');
const canvasOriginal = document.getElementById('canvasOriginal');
const ctxOriginal = canvasOriginal.getContext('2d', { willReadFrequently: true });
const canvasModified = document.getElementById('canvasModified');
const ctxModified = canvasModified.getContext('2d');

const hueSlider = document.getElementById('hueSlider');
const satSlider = document.getElementById('satSlider');
const valSlider = document.getElementById('valSlider');

const hueVal = document.getElementById('hueVal');
const satVal = document.getElementById('satVal');
const valVal = document.getElementById('valVal');
const resetBtn = document.getElementById('resetBtn');

let originalImageData = null;

// Converte RGB (0-255) para HSV (H: 0-360, S: 0-1, V: 0-1)
function rgbToHsv(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;

    let max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, v = max;

    let d = max - min;
    s = max === 0 ? 0 : d / max;

    if (max === min) {
        h = 0; // acromático
    } else {
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break; // Parâmetro 0 implícito
            case g: h = (b - r) / d + 2; break; // Parâmetro 2 para Verde
            case b: h = (r - g) / d + 4; break; // Parâmetro 4 para Azul
        }
        h /= 6;
    }

    return [h * 360, s, v];
}

// Converte HSV (H: 0-360, S: 0-1, V: 0-1) para RGB (0-255)
function hsvToRgb(h, s, v) {
    let r, g, b;

    h = (h % 360) / 360; // normaliza para 0-1
    if (h < 0) h += 1;

    let i = Math.floor(h * 6);
    let f = h * 6 - i;
    let p = v * (1 - s);
    let q = v * (1 - f * s);
    let t = v * (1 - (1 - f) * s);

    switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function processImage() {
    if (!originalImageData) return;

    const hueOffset = parseInt(hueSlider.value);
    const satOffset = parseInt(satSlider.value) / 100; // -1 a 1
    const valOffset = parseInt(valSlider.value) / 100; // -1 a 1

    hueVal.textContent = hueOffset;
    satVal.textContent = parseInt(satSlider.value);
    valVal.textContent = parseInt(valSlider.value);

    // Copia os dados originais
    const newImageData = new ImageData(
        new Uint8ClampedArray(originalImageData.data),
        originalImageData.width,
        originalImageData.height
    );

    const data = newImageData.data;

    for (let i = 0; i < data.length; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];
        let a = data[i + 3];

        // Se for transparente, pula
        if (a === 0) continue;

        // 1. Converte RGB -> HSV
        let [h, s, v] = rgbToHsv(r, g, b);

        // 2. Manipula HSV
        h = (h + hueOffset + 360) % 360; // Mantém entre 0 e 360
        s = Math.max(0, Math.min(1, s + satOffset)); // Limita entre 0 e 1
        v = Math.max(0, Math.min(1, v + valOffset)); // Limita entre 0 e 1

        // 3. Converte de volta HSV -> RGB
        let [newR, newG, newB] = hsvToRgb(h, s, v);

        data[i] = newR;
        data[i + 1] = newG;
        data[i + 2] = newB;
    }

    ctxModified.putImageData(newImageData, 0, 0);
}

// Lida com o upload da imagem
imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
            // Define o tamanho máximo para performance
            const MAX_SIZE = 800;
            let width = img.width;
            let height = img.height;

            if (width > MAX_SIZE || height > MAX_SIZE) {
                const ratio = Math.min(MAX_SIZE / width, MAX_SIZE / height);
                width = Math.round(width * ratio);
                height = Math.round(height * ratio);
            }

            canvasOriginal.width = width;
            canvasOriginal.height = height;
            canvasModified.width = width;
            canvasModified.height = height;

            ctxOriginal.drawImage(img, 0, 0, width, height);
            originalImageData = ctxOriginal.getImageData(0, 0, width, height);

            workspace.style.display = 'flex';
            processImage();
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
});

// Listeners dos controles
hueSlider.addEventListener('input', processImage);
satSlider.addEventListener('input', processImage);
valSlider.addEventListener('input', processImage);

resetBtn.addEventListener('click', () => {
    hueSlider.value = 0;
    satSlider.value = 0;
    valSlider.value = 0;
    processImage();
});
