/**
 * Globe Hero — Vanilla JS COBE globe for lesson hero sections
 * Uses the COBE library (loaded via CDN ESM) to render interactive 3D globes.
 */
import createGlobe from 'https://cdn.jsdelivr.net/npm/cobe@0.6.3/dist/index.esm.js';

var GLOBE_CONFIG = {
    devicePixelRatio: 2,
    phi: 0,
    theta: 0.3,
    dark: 0,
    diffuse: 0.4,
    mapSamples: 16000,
    mapBrightness: 1.2,
    baseColor: [1, 1, 1],
    markerColor: [110 / 255, 193 / 255, 228 / 255],   // matches #6ec1e4 accent
    glowColor: [0.08, 0.12, 0.18],                      // subtle dark glow
    markers: [
        { location: [-17.8292, 31.0522], size: 0.12 },   // Harare, Zimbabwe (prominent)
        { location: [-20.1500, 28.5833], size: 0.08 },   // Bulawayo, Zimbabwe
        { location: [-26.2041, 28.0473], size: 0.06 },   // Johannesburg, SA
        { location: [-33.9249, 18.4241], size: 0.05 },   // Cape Town, SA
        { location: [-15.3875, 28.3228], size: 0.05 },   // Lusaka, Zambia
        { location: [-25.9692, 32.5732], size: 0.04 },   // Maputo, Mozambique
        { location: [-24.6282, 25.9231], size: 0.04 },   // Gaborone, Botswana
        { location: [30.0444, 31.2357], size: 0.05 },    // Cairo
        { location: [6.5244, 3.3792], size: 0.06 },      // Lagos
        { location: [-1.2921, 36.8219], size: 0.05 },    // Nairobi
        { location: [51.5074, -0.1278], size: 0.06 },    // London
        { location: [40.7128, -74.006], size: 0.06 },    // New York
        { location: [39.9042, 116.4074], size: 0.05 },   // Beijing
    ],
};

function initGlobe(canvasEl) {
    var phi = 0;
    var width = canvasEl.offsetWidth;
    var pointerInteracting = null;
    var pointerMovement = 0;
    var r = 0;

    function onRender(state) {
        if (pointerInteracting === null) {
            phi += 0.005;
        }
        state.phi = phi + r;
        state.width = width * 2;
        state.height = width * 2;
    }

    function onResize() {
        width = canvasEl.offsetWidth;
    }

    window.addEventListener("resize", onResize);
    onResize();

    var globe = createGlobe(canvasEl, {
        width: width * 2,
        height: width * 2,
        onRender: onRender,
        devicePixelRatio: GLOBE_CONFIG.devicePixelRatio,
        phi: GLOBE_CONFIG.phi,
        theta: GLOBE_CONFIG.theta,
        dark: GLOBE_CONFIG.dark,
        diffuse: GLOBE_CONFIG.diffuse,
        mapSamples: GLOBE_CONFIG.mapSamples,
        mapBrightness: GLOBE_CONFIG.mapBrightness,
        baseColor: GLOBE_CONFIG.baseColor,
        markerColor: GLOBE_CONFIG.markerColor,
        glowColor: GLOBE_CONFIG.glowColor,
        markers: GLOBE_CONFIG.markers,
    });

    setTimeout(function () {
        canvasEl.style.opacity = "1";
    }, 100);

    // Pointer interaction for dragging
    canvasEl.addEventListener("pointerdown", function (e) {
        pointerInteracting = e.clientX - pointerMovement;
        canvasEl.style.cursor = "grabbing";
    });
    canvasEl.addEventListener("pointerup", function () {
        pointerInteracting = null;
        canvasEl.style.cursor = "grab";
    });
    canvasEl.addEventListener("pointerout", function () {
        pointerInteracting = null;
        canvasEl.style.cursor = "grab";
    });
    canvasEl.addEventListener("mousemove", function (e) {
        if (pointerInteracting !== null) {
            var delta = e.clientX - pointerInteracting;
            pointerMovement = delta;
            r = delta / 200;
        }
    });
    canvasEl.addEventListener("touchmove", function (e) {
        if (e.touches[0] && pointerInteracting !== null) {
            var delta = e.touches[0].clientX - pointerInteracting;
            pointerMovement = delta;
            r = delta / 200;
        }
    });

    return globe;
}

// Initialize all globe canvases
var wraps = document.querySelectorAll(".globe-hero-canvas-wrap");
wraps.forEach(function (wrap) {
    var canvas = wrap.querySelector("canvas");
    if (canvas) {
        initGlobe(canvas);
    }
});
