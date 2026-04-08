# Proyecto Multiagentes - Tendencias en Ingenieria del Software

## Descripcion

Este proyecto es un backend en Python construido con FastAPI para demostrar una arquitectura multiagente simple.

Actualmente la aplicacion recibe un mensaje por medio de un endpoint HTTP, lo envia a un agente planificador, recupera contexto con un agente de consulta, genera una respuesta preliminar y finalmente pasa el resultado a un agente evaluador. El `planner` y el `evaluator` usan un `kernel` compartido que hoy esta implementado como un mock, por lo que el sistema todavia no se conecta a un modelo de lenguaje real ni a herramientas externas.

En su estado actual, el proyecto funciona como una base academica o prototipo para evolucionar hacia un sistema multiagente mas completo.

## Objetivo actual del proyecto

El flujo implementado hoy busca demostrar estos conceptos:

- Exponer una API con FastAPI.
- Recibir una solicitud del usuario.
- Orquestar la ejecucion de multiples agentes especializados.
- Separar responsabilidades entre rutas, modelos, agentes y orquestador.
- Dejar una base lista para integrar mas agentes y un kernel real en el futuro.

## Arquitectura actual

La aplicacion esta organizada alrededor de estos componentes:

- `main.py`: crea la aplicacion FastAPI e incluye las rutas.
- `routes/agent_routes.py`: expone el endpoint `POST /agent`.
- `models/request_model.py`: define el cuerpo esperado de la solicitud con un campo `message`.
- `orchestrator/orchestrator.py`: coordina la secuencia entre agentes.
- `agents/planner_agent.py`: construye un plan estructurado a partir del mensaje recibido.
- `agents/evaluator_agent.py`: evalua la calidad del resultado del flujo completo.
- `kernel/kernel.py`: capa comun de invocacion de agentes. Hoy usa `MockKernel`.

## Flujo actual de ejecucion

1. El cliente envia un `POST /agent` con un JSON como este:

```json
{
  "message": "Analiza tendencias de ingenieria de software"
}
```

2. La ruta recibe el mensaje y llama al orquestador.
3. El orquestador ejecuta `PlannerAgent`.
4. `RetrieverAgent` identifica palabras clave y temas relacionados.
5. `GeneratorAgent` construye una respuesta preliminar con hallazgos y acciones sugeridas.
6. `EvaluatorAgent` valida el resultado consolidado.
7. La API responde con un objeto que contiene:

```json
{
  "input": "Analiza tendencias de ingenieria de software",
  "plan": {
    "objective": "Analiza tendencias de ingenieria de software",
    "task_type": "trend_analysis",
    "focus_areas": [
      "Identificar tendencias y oportunidades relevantes para la solicitud."
    ],
    "steps": [
      "Aclarar el objetivo principal de la solicitud.",
      "Identificar los temas o dominios mas relevantes."
    ],
    "expected_output": "Resumen de tendencias con implicaciones practicas.",
    "kernel_trace": "[planner] proceso: Analiza tendencias de ingenieria de software"
  },
  "retrieval": {
    "query": "Analiza tendencias de ingenieria de software",
    "keywords": [
      "tendencias",
      "ingenieria"
    ],
    "matched_topics": [
      {
        "name": "AI-assisted development",
        "relevance": 1
      }
    ],
    "retrieval_summary": "..."
  },
  "generation": {
    "summary": "...",
    "key_points": [
      "..."
    ],
    "recommended_actions": [
      "..."
    ],
    "draft_response": "..."
  },
  "validation": {
    "status": "approved",
    "score": 100,
    "strengths": [
      "..."
    ],
    "issues": [],
    "suggestions": [
      "..."
    ],
    "kernel_trace": "[evaluator] proceso: validation"
  }
}
```

Nota: el texto exacto puede variar segun el mock, pero el comportamiento actual es simulado.

## Estado real de la implementacion

Hoy el proyecto no es un sistema multiagente completo todavia. Estas son las partes ya implementadas:

- API minima con FastAPI.
- Modelo de entrada con Pydantic.
- Orquestador basico.
- Agente planificador con salida estructurada.
- Agente de recuperacion de contexto.
- Agente generador de respuesta.
- Agente evaluador con validacion heuristica del flujo.
- Kernel simulado para pruebas.

Estas partes existen pero estan vacias o incompletas:

- `services/agent_service.py`
- `utils/logger.py`

## Agentes actuales y posibles extensiones

### 1. PlannerAgent

Responsabilidad actual:

- Recibir el texto de entrada.
- Detectar el tipo de solicitud.
- Proponer areas de enfoque.
- Construir una secuencia de pasos esperados.
- Definir el tipo de salida esperada.

Posibles mejoras:

- Descomponer una tarea compleja en subtareas.
- Definir pasos, prioridades y dependencias.
- Identificar si hacen falta otros agentes.

### 2. EvaluatorAgent

Responsabilidad actual:

- Recibir el estado consolidado del flujo.
- Revisar si existe plan, contexto recuperado, borrador generado y acciones sugeridas.
- Calcular un puntaje y devolver observaciones estructuradas.

Posibles mejoras:

- Revisar calidad, consistencia y cobertura.
- Detectar errores o respuestas incompletas.
- Devolver observaciones para iterar sobre el plan o la respuesta.

### 3. GeneratorAgent

Rol recomendado:

- Generar la respuesta final para el usuario.
- Redactar resultados a partir del plan.
- Transformar datos recuperados en texto estructurado.

Estado actual:

- Ya tiene una primera version funcional.
- Construye un resumen, puntos clave, acciones recomendadas y un borrador de respuesta.

Ejemplo de flujo futuro:

- `PlannerAgent` define que hacer.
- `RetrieverAgent` busca contexto.
- `GeneratorAgent` redacta la salida.
- `EvaluatorAgent` revisa la calidad.

### 4. RetrieverAgent

Rol recomendado:

- Buscar informacion de apoyo antes de generar la respuesta.
- Consultar una base de conocimiento, archivos locales, APIs o documentos.
- Entregar contexto al generador o al evaluador.

Estado actual:

- Ya tiene una primera version funcional.
- Extrae palabras clave y relaciona la solicitud con un pequeno catalogo local de tendencias.

## Otros componentes que vale la pena modificar

Ademas de `generator` y `retriever`, estos componentes son claves para evolucionar el proyecto:

### Orchestrator

Archivo:

- `orchestrator/orchestrator.py`

Por que modificarlo:

- Hoy ejecuta `planner`, `retriever`, `generator` y `evaluator`.
- Si agregan mas agentes, aqui se define el orden y la colaboracion entre ellos.

Ejemplo de evolucion:

1. `planner`
2. `retriever`
3. `generator`
4. `evaluator`

### Kernel

Archivo:

- `kernel/kernel.py`

Por que modificarlo:

- Es el mejor punto para reemplazar el mock por una integracion real con un LLM o motor de agentes.
- Permite centralizar llamadas, configuracion, prompts y manejo de errores.

### Agent Service

Archivo:

- `services/agent_service.py`

Por que modificarlo:

- Puede servir como capa de negocio para aislar la logica de invocacion de agentes.
- Ayuda a evitar que el orquestador crezca demasiado.

### Logger

Archivo:

- `utils/logger.py`

Por que modificarlo:

- Permite auditar el flujo entre agentes.
- Facilita depuracion, trazabilidad y observabilidad.

## Estructura del proyecto

```text
project/
  app/
    agents/
      evaluator_agent.py
      generator_agent.py
      planner_agent.py
      retriever_agent.py
    kernel/
      kernel.py
    models/
      request_model.py
    orchestrator/
      orchestrator.py
    routes/
      agent_routes.py
    services/
      agent_service.py
    utils/
      logger.py
    main.py
    requirements.txt
```

## Requisitos

Dependencias actuales:

- `fastapi`
- `uvicorn`
- `pydantic`

## Como ejecutar el proyecto

Desde la carpeta `project`:

```bash
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

La API deberia quedar disponible en:

```text
http://127.0.0.1:8000
```

## Endpoint disponible

### `POST /agent`

Cuerpo esperado:

```json
{
  "message": "Tu solicitud"
}
```

`message` debe contener texto no vacio y se recorta automaticamente si llega con espacios al inicio o al final.

Respuesta esperada:

```json
{
  "input": "...",
  "plan": {},
  "retrieval": {},
  "generation": {},
  "validation": {}
}
```

## Limitaciones actuales

- No hay integracion con un modelo de lenguaje real.
- No hay memoria, contexto persistente ni herramientas externas.
- `GeneratorAgent` y `RetrieverAgent` usan una logica local inicial, pero no consumen fuentes externas reales.
- `agent_service.py` y `logger.py` no se usan todavia.
- El `README` original no documentaba el estado real del proyecto.

## Siguientes pasos sugeridos

Una evolucion natural del proyecto seria:

1. Conectar `RetrieverAgent` a una fuente real de conocimiento.
2. Mejorar `GeneratorAgent` para producir respuestas mas naturales o estructuradas por plantilla.
3. Reemplazar `MockKernel` por una integracion real.
4. Agregar logging y manejo de errores.
5. Mover logica comun a `agent_service.py`.
6. Documentar prompts, entradas y salidas de cada agente.

## Resumen

Este proyecto ya demuestra la base de una arquitectura multiagente, pero todavia esta en una fase inicial. Su valor principal hoy es servir como esqueleto para experimentar con orquestacion de agentes, validacion entre etapas y futura integracion con motores de IA mas reales.
