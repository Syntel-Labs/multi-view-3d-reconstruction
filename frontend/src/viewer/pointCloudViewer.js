import * as THREE from 'three';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/**
 * Inicializa el visor dentro del elemento con el id dado y carga el PLY.
 * @param {string} containerId  - id del elemento contenedor
 * @param {string} plyUrl       - URL del archivo .ply (via backend)
 * @returns {Promise<void>}     - resuelve cuando el PLY está en escena, rechaza si falla
 */
export function initViewer(containerId, plyUrl) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0b0d);

    const camera = new THREE.PerspectiveCamera(
        60,
        container.clientWidth / container.clientHeight,
        0.001,
        2000
    );

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.rotateSpeed = 0.6;
    controls.zoomSpeed = 1.2;
    controls.minDistance = 0.05;
    controls.maxDistance = 500;

    let animFrameId;
    function animate() {
        animFrameId = requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    const onResize = () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    };
    window.addEventListener('resize', onResize);

    return new Promise((resolve, reject) => {
        const loader = new PLYLoader();

        loader.load(
            plyUrl,
            (geometry) => {
                geometry.computeBoundingBox();

                const material = new THREE.PointsMaterial({
                    size: 0.025,
                    vertexColors: geometry.hasAttribute('color'),
                    color: geometry.hasAttribute('color') ? 0xffffff : 0x4fffb0,
                    sizeAttenuation: true,
                });

                const points = new THREE.Points(geometry, material);
                scene.add(points);

                const pos = geometry.attributes.position.array;
                const n   = pos.length / 3;

                const xs = [], ys = [], zs = [];
                for (let i = 0; i < n; i++) {
                    xs.push(pos[i * 3]);
                    ys.push(pos[i * 3 + 1]);
                    zs.push(pos[i * 3 + 2]);
                }

                const pct = (arr, p) => {
                    const s = [...arr].sort((a, b) => a - b);
                    return s[Math.floor(s.length * p)];
                };

                const [x5, x95] = [pct(xs, 0.05), pct(xs, 0.95)];
                const [y5, y95] = [pct(ys, 0.05), pct(ys, 0.95)];
                const [z5, z95] = [pct(zs, 0.05), pct(zs, 0.95)];

                const center = new THREE.Vector3(
                    (x5 + x95) / 2,
                    (y5 + y95) / 2,
                    (z5 + z95) / 2,
                );

                const span = Math.max(x95 - x5, y95 - y5, z95 - z5) || 1;

                controls.target.copy(center);
                camera.position.set(
                    center.x,
                    center.y,
                    center.z + span * 2.2
                );
                controls.update();

                resolve();
            },
            undefined,
            (error) => {
                console.error('[pointCloudViewer] Error al cargar PLY:', error);
                cancelAnimationFrame(animFrameId);
                window.removeEventListener('resize', onResize);
                renderer.dispose();
                reject(error);
            }
        );
    });
}
