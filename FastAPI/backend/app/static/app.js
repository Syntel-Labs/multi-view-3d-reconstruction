import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { PLYLoader } from "three/examples/jsm/loaders/PLYLoader.js";

const form = document.querySelector("#upload-form");
const fileInput = document.querySelector("#zip-file");
const statusNode = document.querySelector("#status");
const downloadLink = document.querySelector("#download-link");
const viewer = document.querySelector("#viewer");

const scene = new THREE.Scene();
scene.background = new THREE.Color("#07111f");

const camera = new THREE.PerspectiveCamera(
  60,
  viewer.clientWidth / viewer.clientHeight,
  0.1,
  100,
);
camera.position.set(1.8, 1.4, 2.6);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(viewer.clientWidth, viewer.clientHeight);
viewer.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.AxesHelper(1.5));

const grid = new THREE.GridHelper(8, 16, "#4f8cff", "#213049");
grid.position.y = -1.2;
scene.add(grid);

const ambientLight = new THREE.AmbientLight("#ffffff", 1.2);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight("#ffffff", 1.8);
directionalLight.position.set(3, 4, 2);
scene.add(directionalLight);

let currentObject = null;
let currentDownloadUrl = null;

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.dataset.error = String(isError);
}

function renderPly(arrayBuffer) {
  const loader = new PLYLoader();
  const geometry = loader.parse(arrayBuffer);
  geometry.center();
  geometry.computeBoundingSphere();

  if (currentObject) {
    scene.remove(currentObject);
    currentObject.geometry.dispose();
    currentObject.material.dispose();
  }

  const hasColor = Boolean(geometry.getAttribute("color"));
  const material = new THREE.PointsMaterial({
    size: 0.045,
    vertexColors: hasColor,
    color: hasColor ? "#ffffff" : "#6dd3ff",
  });

  currentObject = new THREE.Points(geometry, material);
  scene.add(currentObject);

  const radius = geometry.boundingSphere?.radius ?? 1;
  camera.position.set(radius * 2.2, radius * 1.8, radius * 2.6);
  controls.target.set(0, 0, 0);
  controls.update();
}

async function handleSubmit(event) {
  event.preventDefault();
  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("Select a ZIP before sending the request.", true);
    return;
  }

  setStatus("Uploading ZIP and waiting for mock reconstruction...");

  const formData = new FormData();
  formData.append("archive", file);

  try {
    const response = await fetch("/reconstruct", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => null);
      throw new Error(errorPayload?.detail || "Reconstruction failed.");
    }

    const blob = await response.blob();
    const filename =
      response.headers
        .get("Content-Disposition")
        ?.match(/filename="(.+)"/)?.[1] || "mock-reconstruction.ply";
    const fileCount = response.headers.get("X-Source-File-Count") || "?";
    const objectUrl = URL.createObjectURL(blob);
    const arrayBuffer = await blob.arrayBuffer();

    if (currentDownloadUrl) {
      URL.revokeObjectURL(currentDownloadUrl);
    }

    renderPly(arrayBuffer);
    currentDownloadUrl = objectUrl;
    downloadLink.href = objectUrl;
    downloadLink.download = filename;
    downloadLink.hidden = false;
    setStatus(`Mock .ply loaded. ZIP contained ${fileCount} file(s).`);
  } catch (error) {
    setStatus(error instanceof Error ? error.message : "Unknown error.", true);
  }
}

function handleResize() {
  const width = viewer.clientWidth;
  const height = viewer.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

form.addEventListener("submit", handleSubmit);
window.addEventListener("resize", handleResize);

animate();
