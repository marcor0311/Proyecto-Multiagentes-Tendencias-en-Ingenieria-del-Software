# Proyecto Multiagentes - Generacion de Terraform para AWS

## Descripcion

Este proyecto es un backend en Python construido con FastAPI para implementar un sistema multiagente orientado a Infraestructura como Codigo.

La entrada del sistema es un JSON estructurado que describe una solucion de infraestructura para AWS. A partir de esa entrada, el sistema ejecuta un workflow secuencial con agentes especializados para:

- planificar la solucion
- recuperar contexto util para Terraform
- generar archivos `.tf`
- evaluar la cobertura del proyecto
- construir y empaquetar un `.zip` final

## Objetivo del proyecto

El objetivo base es desarrollar un sistema multiagente con workflow secuencial e iteracion de validacion, compuesto por:

- `PlannerAgent`
- `RetrieverAgent`
- `GeneratorAgent`
- `EvaluatorAgent`
- `BuilderAgent`

La salida esperada es un proyecto Terraform para AWS empaquetado en un archivo `.zip`.

## Arquitectura actual

La aplicacion esta organizada alrededor de estos componentes:

- `main.py`: crea la aplicacion FastAPI, carga variables de entorno y registra CORS.
- `routes/agent_routes.py`: expone el endpoint principal `POST /api/agent`.
- `models/request_model.py`: define el JSON estructurado de entrada.
- `services/agent_service.py`: delega la solicitud al orquestador.
- `orchestrator/orchestrator.py`: coordina la secuencia entre agentes.
- `agents/planner_agent.py`: traduce la solicitud en un plan orientado a Terraform/AWS.
- `agents/retriever_agent.py`: identifica recursos, archivos objetivo, dependencias y pistas de validacion.
- `agents/generator_agent.py`: genera contenido Terraform por archivo.
- `agents/evaluator_agent.py`: valida cobertura de archivos y recursos solicitados.
- `agents/builder_agent.py`: escribe archivos y genera el `.zip` final.
- `kernel/kernel.py`: usa un `MockKernel` para trazas internas.
- `services/openai_service.py`: servicio preparado para integracion con Azure OpenAI.

## Flujo actual

1. El cliente envia un `POST /api/agent` con un JSON IaC.
2. La ruta valida el request con Pydantic.
3. `AgentService` delega la ejecucion a `Orchestrator`.
4. `PlannerAgent` genera el plan del proyecto Terraform.
5. `RetrieverAgent` define archivos requeridos, dependencias y hints de validacion.
6. `GeneratorAgent` produce el contenido de los archivos Terraform.
7. `EvaluatorAgent` revisa si la cobertura es consistente con la solicitud.
8. `BuilderAgent` escribe los archivos en disco y crea el archivo `.zip`.
9. La API devuelve el estado completo del flujo, incluyendo la ubicacion del `.zip`.

## Estado actual de implementacion

Hoy el proyecto ya tiene una base funcional para la demo del workflow multiagente:

- API con FastAPI y CORS.
- Modelo de entrada estructurado para IaC en AWS.
- Orquestacion secuencial entre agentes.
- Generacion de archivos Terraform base.
- Empaquetado de salida en `.zip`.
- Evaluacion heuristica de cobertura.
- Servicio preparado para futura integracion con Azure OpenAI.

Limitaciones actuales:

- El `kernel` sigue siendo mock.
- Los archivos Terraform generados son una primera version base, no una plantilla completa de produccion.
- Aun no se ejecuta `terraform fmt` ni `terraform validate` automaticamente.
- No hay iteracion automatica entre `EvaluatorAgent` y `GeneratorAgent` cuando hay observaciones.

## Modelo de entrada

El backend acepta un unico formato de entrada: el payload que hoy envia el frontend en `PSWE-01`.

Request esperado:

```json
{
  "project_name": "demo-s3-module",
  "cloud_provider": "aws",
  "region": "us-east-1",
  "environment": "dev",
  "resources": [
    {
      "type": "s3",
      "name": "tendencias-bucket"
    }
  ]
}
```

## Como validar con Terraform desde consola

Desde la carpeta del proyecto generado:

```bash
cd project/generated/demo-s3-module
terraform init
terraform fmt -check
terraform validate
```

Si quieres probar el plan:

```bash
terraform plan
```

Si `terraform plan` falla con credenciales de AWS, eso no significa necesariamente que el proyecto este mal.
Solo significa que Terraform no encontro acceso configurado a AWS.
```

Internamente el sistema multiagente deriva a partir de `resources`:

- `architecture.resources` a partir de los `type`.
- `architecture.type` segun los recursos seleccionados.
- `storage` cuando existe un recurso `s3`.
- `compute` cuando existen recursos `ec2`.

## Archivos Terraform generados

Segun los recursos solicitados, el sistema puede generar archivos como:

- `provider.tf`
- `variables.tf`
- `terraform.tfvars`
- `main.tf`
- `network.tf`
- `security.tf`
- `compute.tf`
- `storage.tf`
- `outputs.tf`
- `README.md`

## Endpoints disponibles

### `GET /`

Endpoint simple para verificar que el backend esta operativo.

Respuesta esperada:

```json
{
  "message": "Backend Multiagentes operativo",
  "status": "ok",
  "docs": "/docs"
}
```

### `POST /api/agent`

Procesa la solicitud IaC y devuelve el estado completo del workflow.

### Ejemplo de request

```json
{
  "project_name": "demo-s3-module",
  "cloud_provider": "aws",
  "region": "us-east-1",
  "environment": "dev",
  "resources": [
    {
      "type": "s3",
      "name": "tendencias-bucket"
    }
  ]
}
```

### Ejemplo de response

```json
{
  "input": {
    "project_name": "demo-s3-module",
    "cloud_provider": "aws",
    "region": "us-east-1",
    "environment": "dev",
    "architecture": {
      "type": "static_site",
      "resources": [
        "s3"
      ]
    },
    "resources": [
      {
        "type": "s3",
        "name": "tendencias-bucket"
      }
    ],
    "network": null,
    "compute": null,
    "storage": {
      "create_s3_bucket": true,
      "s3_bucket_name": "tendencias-bucket"
    },
    "tags": {}
  },
  "plan": {
    "objective": "Generar IaC Terraform para AWS del proyecto demo-s3-module.",
    "task_type": "terraform_iac_generation",
    "focus_areas": [
      "Definir una estructura Terraform clara y modular.",
      "Alinear los recursos solicitados con buenas practicas basicas de AWS.",
      "Preparar almacenamiento y convenciones de nombres para S3."
    ],
    "steps": [
      "Analizar el JSON estructurado de entrada.",
      "Identificar recursos AWS y dependencias entre ellos.",
      "Determinar los archivos Terraform necesarios."
    ]
  }
}
```

## Estructura del proyecto

```text
project/
  app/
    agents/
      builder_agent.py
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
      openai_service.py
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
- `python-dotenv`
- `openai`

## Como ejecutar el proyecto

Desde la carpeta `project`:

```bash
source venv/bin/activate
pip install -r app/requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La API deberia quedar disponible en:

```text
http://127.0.0.1:8000
```

La documentacion interactiva estara en:

```text
http://127.0.0.1:8000/docs
```

## Resumen

El proyecto ya no es solo una demo de agentes conversacionales. Ahora es una base funcional para un sistema multiagente que recibe un JSON de infraestructura para AWS, genera archivos Terraform, los valida heurísticamente y los empaqueta en un archivo `.zip`.

## Usando modules

### S3 Bucket

El módulo oficial para crear buckets en AWS S3 (`terraform-aws-modules/s3-bucket/aws`) incluye **más de 80 variables** posibles para configurar detalles como versioning, ACLs, políticas, cifrado, logging, CORS, lifecycle rules, replicación, entre muchas otras opciones avanzadas.

```json
{
  "project_name": "demo-s3-module",
  "cloud_provider": "aws",
  "region": "us-east-1",
  "environment": "dev",
  "resources": [
    {
      "type": "s3",
      "name": "tendencias-bucket"
    }
  ]
}
