import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export function initViewer(containerId, plyUrl) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x222222);

    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);

    const loader = new PLYLoader();
    loader.load(plyUrl, (geometry) => {
        const material = new THREE.PointsMaterial({ size: 0.05, vertexColors: true });
        const points = new THREE.Points(geometry, material);
        scene.add(points);

        const positions = geometry.attributes.position.array;
        const zValues = [];
        for (let i = 2; i < positions.length; i += 3) {
            zValues.push(positions[i]);
        }
        
        zValues.sort((a, b) => a - b);
        const p5 = zValues[Math.floor(zValues.length * 0.05)];
        const p95 = zValues[Math.floor(zValues.length * 0.95)];
        const zCenter = (p5 + p95) / 2;

        let xSum = 0, ySum = 0, count = 0;
        for (let i = 0; i < positions.length; i += 3) {
            const z = positions[i + 2];
            if (z >= p5 && z <= p95) {
                xSum += positions[i];
                ySum += positions[i + 1];
                count++;
            }
        }
        
        const xCenter = count > 0 ? xSum / count : 0;
        const yCenter = count > 0 ? ySum / count : 0;

        const center = new THREE.Vector3(xCenter, yCenter, zCenter);
        controls.target.copy(center);
        
        camera.position.set(xCenter, yCenter, zCenter - 5);
        controls.update();

    }, undefined, (error) => {
        console.error('No se pudo cargar el archivo PLY:', error);
    });

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}
