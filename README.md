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

El request actual espera un JSON estructurado como este:

```json
{
  "project_name": "infra-web-demo",
  "cloud_provider": "aws",
  "region": "us-east-1",
  "environment": "dev",
  "architecture": {
    "type": "web_app",
    "resources": [
      "vpc",
      "subnets",
      "security_groups",
      "ec2",
      "s3"
    ]
  },
  "network": {
    "vpc_cidr": "10.0.0.0/16",
    "public_subnets": [
      "10.0.1.0/24",
      "10.0.2.0/24"
    ],
    "private_subnets": [
      "10.0.11.0/24",
      "10.0.12.0/24"
    ]
  },
  "compute": {
    "ec2_instance_type": "t3.micro",
    "ec2_count": 1,
    "ami_id": "ami-xxxxxxxx"
  },
  "storage": {
    "create_s3_bucket": true,
    "s3_bucket_name": "infra-web-demo-dev-bucket"
  },
  "tags": {
    "owner": "equipo-arquitectura",
    "course": "PSWE-01",
    "environment": "dev"
  }
}
```

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
  "project_name": "infra-web-demo",
  "cloud_provider": "aws",
  "region": "us-east-1",
  "environment": "dev",
  "architecture": {
    "type": "web_app",
    "resources": [
      "vpc",
      "subnets",
      "security_groups",
      "ec2",
      "s3"
    ]
  },
  "network": {
    "vpc_cidr": "10.0.0.0/16",
    "public_subnets": [
      "10.0.1.0/24",
      "10.0.2.0/24"
    ],
    "private_subnets": [
      "10.0.11.0/24",
      "10.0.12.0/24"
    ]
  },
  "compute": {
    "ec2_instance_type": "t3.micro",
    "ec2_count": 1,
    "ami_id": "ami-xxxxxxxx"
  },
  "storage": {
    "create_s3_bucket": true,
    "s3_bucket_name": "infra-web-demo-dev-bucket"
  },
  "tags": {
    "owner": "equipo-arquitectura",
    "course": "PSWE-01",
    "environment": "dev"
  }
}
```

### Ejemplo de response

```json
{
  "input": {
    "project_name": "infra-web-demo",
    "cloud_provider": "aws",
    "region": "us-east-1",
    "environment": "dev",
    "architecture": {
      "type": "web_app",
      "resources": [
        "vpc",
        "subnets",
        "security_groups",
        "ec2",
        "s3"
      ]
    },
    "network": {
      "vpc_cidr": "10.0.0.0/16",
      "public_subnets": [
        "10.0.1.0/24",
        "10.0.2.0/24"
      ],
      "private_subnets": [
        "10.0.11.0/24",
        "10.0.12.0/24"
      ]
    },
    "compute": {
      "ec2_instance_type": "t3.micro",
      "ec2_count": 1,
      "ami_id": "ami-xxxxxxxx"
    },
    "storage": {
      "create_s3_bucket": true,
      "s3_bucket_name": "infra-web-demo-dev-bucket"
    },
    "tags": {
      "owner": "equipo-arquitectura",
      "course": "PSWE-01",
      "environment": "dev"
    }
  },
  "plan": {
    "objective": "Generar IaC Terraform para AWS del proyecto infra-web-demo.",
    "task_type": "terraform_iac_generation",
    "focus_areas": [
      "Definir una estructura Terraform clara y modular.",
      "Alinear los recursos solicitados con buenas practicas basicas de AWS.",
      "Resolver correctamente la configuracion de red.",
      "Configurar recursos de computo y sus parametros clave.",
      "Preparar almacenamiento y convenciones de nombres para S3."
    ],
    "steps": [
      "Analizar el JSON estructurado de entrada.",
      "Identificar recursos AWS y dependencias entre ellos.",
      "Determinar los archivos Terraform necesarios.",
      "Recuperar contexto reutilizable para la generacion.",
      "Generar contenido Terraform por archivo.",
      "Validar cobertura y consistencia del proyecto.",
      "Construir y empaquetar el proyecto final en un zip.",
      "Recursos objetivo: vpc, subnets, security_groups, ec2, s3"
    ],
    "expected_output": "Proyecto Terraform para AWS empaquetado en un archivo zip.",
    "target_files": [
      "provider.tf",
      "variables.tf",
      "terraform.tfvars",
      "outputs.tf",
      "README.md",
      "network.tf",
      "security.tf",
      "compute.tf",
      "storage.tf",
      "main.tf"
    ],
    "kernel_trace": "[planner] proceso: Proyecto infra-web-demo en us-east-1 para ambiente dev con recursos: vpc, subnets, security_groups, ec2, s3."
  },
  "retrieval": {
    "cloud_provider": "aws",
    "architecture_type": "web_app",
    "requested_resources": [
      "vpc",
      "subnets",
      "security_groups",
      "ec2",
      "s3"
    ],
    "resource_context": [
      {
        "resource": "vpc",
        "target_file": "network.tf",
        "summary": "Define la red principal donde se desplegaran los recursos.",
        "dependencies": [],
        "validation_hints": [
          "Verificar que el CIDR de la VPC exista.",
          "Revisar que la VPC tenga tags coherentes."
        ]
      }
    ],
    "required_files": [
      "README.md",
      "compute.tf",
      "main.tf",
      "network.tf",
      "outputs.tf",
      "provider.tf",
      "security.tf",
      "storage.tf",
      "terraform.tfvars",
      "variables.tf"
    ],
    "validation_hints": [
      "Verificar que el CIDR de la VPC exista.",
      "Revisar que la VPC tenga tags coherentes."
    ],
    "retrieval_summary": "Para el proyecto infra-web-demo se identificaron recursos Terraform AWS: vpc, subnets, security_groups, ec2, s3. Los archivos sugeridos son: README.md, compute.tf, main.tf, network.tf, outputs.tf, provider.tf, security.tf, storage.tf, terraform.tfvars, variables.tf."
  },
  "generation": {
    "summary": "Se generaron archivos Terraform para el proyecto infra-web-demo con foco en vpc, subnets, security_groups, ec2, s3.",
    "key_points": [
      "El proyecto se genera para AWS con archivos Terraform separados por responsabilidad.",
      "La estructura considera provider, variables, tfvars, outputs y archivos por dominio.",
      "El contenido puede servir como base para refinar con modelos o plantillas mas avanzadas."
    ],
    "recommended_actions": [
      "Ejecutar terraform fmt sobre los archivos generados.",
      "Ejecutar terraform validate antes de aplicar.",
      "Revisar manualmente reglas de seguridad y nombres finales."
    ],
    "terraform_files": {
      "provider.tf": "terraform { ... }",
      "variables.tf": "variable \"project_name\" { ... }",
      "terraform.tfvars": "project_name = \"infra-web-demo\"",
      "main.tf": "# Terraform base para el proyecto ...",
      "network.tf": "resource \"aws_vpc\" \"main\" { ... }",
      "security.tf": "resource \"aws_security_group\" \"app\" { ... }",
      "compute.tf": "resource \"aws_instance\" \"app\" { ... }",
      "storage.tf": "resource \"aws_s3_bucket\" \"artifacts\" { ... }",
      "outputs.tf": "output \"project_name\" { ... }",
      "README.md": "# infra-web-demo"
    },
    "file_notes": [
      {
        "file": "provider.tf",
        "line_count": 12
      },
      {
        "file": "network.tf",
        "line_count": 25
      }
    ],
    "draft_response": "Proyecto infra-web-demo listo para construccion. Se prepararon 10 archivos Terraform para AWS. Recursos cubiertos: vpc, subnets, security_groups, ec2, s3."
  },
  "validation": {
    "status": "approved",
    "score": 100,
    "strengths": [
      "El plan define etapas para generar y empaquetar IaC.",
      "La recuperacion identifica recursos AWS, archivos objetivo y dependencias.",
      "GeneratorAgent produjo archivos Terraform listos para construccion.",
      "La cobertura de archivos y recursos es consistente con la solicitud."
    ],
    "issues": [],
    "suggestions": [
      "Ejecutar terraform fmt y terraform validate sobre el zip generado."
    ],
    "missing_files": [],
    "missing_resource_coverage": [],
    "kernel_trace": "[evaluator] proceso: terraform-validation"
  },
  "build": {
    "project_name": "infra-web-demo",
    "output_dir": "project/generated/infra-web-demo",
    "zip_path": "project/generated/infra-web-demo.zip",
    "files_created": [
      "provider.tf",
      "variables.tf",
      "terraform.tfvars",
      "outputs.tf",
      "README.md",
      "main.tf",
      "network.tf",
      "security.tf",
      "compute.tf",
      "storage.tf"
    ],
    "status": "success"
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
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

La API deberia quedar disponible en:

```text
http://127.0.0.1:8000
```

La documentacion interactiva estara en:

```text
http://127.0.0.1:8000/docs
```

## Proximos pasos sugeridos

1. Reemplazar el `MockKernel` por una integracion real entre agentes y LLM.
2. Integrar validacion automatica con `terraform fmt` y `terraform validate`.
3. Hacer iterativo el flujo entre `EvaluatorAgent` y `GeneratorAgent`.
4. Mejorar plantillas Terraform para mas tipos de arquitectura y recursos.
5. Formalizar modelos de respuesta con Pydantic.
6. Agregar pruebas automatizadas del endpoint y del workflow multiagente.

## Resumen

El proyecto ya no es solo una demo de agentes conversacionales. Ahora es una base funcional para un sistema multiagente que recibe un JSON de infraestructura para AWS, genera archivos Terraform, los valida heurísticamente y los empaqueta en un archivo `.zip`.
