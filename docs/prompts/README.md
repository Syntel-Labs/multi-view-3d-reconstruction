# Log de prompts de IA

Registro de los prompts enviados a herramientas de IA durante el desarrollo del proyecto. Es un requisito explicito de la rubrica del curso (seccion Herramientas aplicadas) y sirve como bitacora compartida del equipo, sin importar quien los corrio.

## Que se registra

Cada entrada incluye:

- **Fecha**: cuando se envio el prompt (`YYYY-MM-DD`).
- **Herramienta**: Claude / ChatGPT / Copilot / Gemini / etc., con version o modelo si aplica.
- **URL de la herramienta** (si la conversacion es publica o compartible): enlace a la sesion.
- **URL de origen de la pregunta**: si el prompt nace de una pregunta o discusion externa (StackOverflow, GitHub Issue, video de YouTube, paper, doc oficial), el enlace donde se origino la duda.
- **Modulo o area afectada**: `features.py`, `geometry.py`, `frontend/viewer`, `infra/docker`, etc.
- **Prompt**: copia textual del prompt enviado (resumir si excede 30 lineas, conservando la intencion completa).
- **Resultado**: que devolvio el modelo (resumen breve).
- **Uso**: `literal` | `adaptado` | `descartado`.
- **Justificacion**: por que se uso IA en lugar de hacerlo manualmente.

## Formato de cada entrada

```markdown
## YYYY-MM-DD - {tema corto}

- Herramienta: {nombre y version}
- URL herramienta: {link o vacio}
- URL origen: {link o vacio}
- Modulo / area: {ruta o area afectada}
- Prompt: |
    {copia textual; bloque indentado para preservar formato}
- Resultado: {resumen breve de la respuesta}
- Uso: literal | adaptado | descartado
- Justificacion: {por que se uso IA}
```

## Reglas

- Registrar el mismo dia que se uso la herramienta; los logs tardios distorsionan el contexto.
- Incluir prompts cuyo resultado se descarto: el descarte tambien es informacion util.
- Sin secretos, datos sensibles, credenciales ni rutas absolutas a maquinas privadas.
- Si el prompt incluye codigo del repo, basta con referenciar el archivo y la linea, no pegarlo entero.
- Las URLs de origen son particularmente importantes: muestran que la IA se uso para sintetizar o adaptar conocimiento, no para generar desde cero.

## Estructura de archivos

```text
docs/prompts/
├── README.md         (este archivo)
└── {logs por tema, fecha o iteracion segun convenga}
```

La organizacion fina queda abierta: pueden ser archivos por sprint, por modulo, o un unico archivo cronologico. Lo unico obligatorio es que cada entrada cumpla el formato anterior.
