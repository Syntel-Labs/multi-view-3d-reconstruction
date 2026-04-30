# Documento final

Documento PDF, diagramas y resultados que se entregan en Canvas el 21 de mayo de 2026.

## Estructura

```text
docs/final/
├── README.md
├── document.md         # fuente Markdown del documento final
├── diagrams/           # .mmd / .puml grandes referenciados por document.md
└── results/            # tablas de metricas, capturas de pantalla, nubes ejemplo
```

## Reglas

- `document.md` es la fuente; el PDF se exporta como `document.pdf` (no se versiona el PDF mientras este en borrador, solo el final).
- Diagramas pequenos van inline con Mermaid en `document.md`; los grandes en `diagrams/<nombre>.mmd` o `.puml`.
- `results/` aloja tablas, capturas y nubes ejemplo referenciadas desde `document.md`.

## Secciones sugeridas

Ver `docs/plan.md` y la rubrica del curso.

1. Problema
2. Analisis
3. Propuesta
4. Descripcion de la solucion (subdividida por modulo)
5. Demo web
6. Resultados con metricas reales
7. Conclusion
8. Bibliografia
