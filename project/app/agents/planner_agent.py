from typing import Any, Dict, List

from app.kernel.kernel import kernel


class PlannerAgent:
    FILE_MAP = {
        "vpc": "network.tf",
        "subnets": "network.tf",
        "security_groups": "security.tf",
        "ec2": "compute.tf",
        "s3": "storage.tf",
    }

    async def run(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        project_name = request_data.get("project_name", "infra-project")
        architecture = request_data.get("architecture", {})
        resources = architecture.get("resources", [])
        summary = self._build_summary(request_data)

        kernel_trace = await kernel.invoke("planner", summary)

        return {
            "objective": f"Generar IaC Terraform para AWS del proyecto {project_name}.",
            "task_type": "terraform_iac_generation",
            "focus_areas": self._build_focus_areas(request_data),
            "steps": self._build_steps(resources),
            "expected_output": "Proyecto Terraform para AWS empaquetado en un archivo zip.",
            "target_files": self._determine_files(resources),
            "kernel_trace": kernel_trace,
        }

    def process(self, message: str) -> str:
        from app.services.openai_service import ask_azure_openai

        prompt = (
            "Eres un agente planner para infraestructura como codigo en Terraform para AWS. "
            "A partir de la solicitud del usuario, resume brevemente la infraestructura requerida, "
            "identifica los recursos principales y responde en espanol de forma corta y estructurada.\n"
            f"Solicitud: {message}"
        )
        return ask_azure_openai(prompt)

    def _build_summary(self, request_data: Dict[str, Any]) -> str:
        resources = request_data.get("architecture", {}).get("resources", [])
        resources_text = ", ".join(resources) if resources else "sin recursos definidos"
        return (
            f"Proyecto {request_data.get('project_name', 'infra-project')} "
            f"en {request_data.get('region', 'aws-region')} "
            f"para ambiente {request_data.get('environment', 'dev')} "
            f"con recursos: {resources_text}."
        )

    def _build_focus_areas(self, request_data: Dict[str, Any]) -> List[str]:
        focus_areas = [
            "Definir una estructura Terraform clara y modular.",
            "Alinear los recursos solicitados con buenas practicas basicas de AWS.",
        ]

        if request_data.get("network"):
            focus_areas.append("Resolver correctamente la configuracion de red.")
        if request_data.get("compute"):
            focus_areas.append("Configurar recursos de computo y sus parametros clave.")
        if request_data.get("storage", {}).get("create_s3_bucket"):
            focus_areas.append("Preparar almacenamiento y convenciones de nombres para S3.")

        return focus_areas

    def _build_steps(self, resources: List[str]) -> List[str]:
        steps = [
            "Analizar el JSON estructurado de entrada.",
            "Identificar recursos AWS y dependencias entre ellos.",
            "Determinar los archivos Terraform necesarios.",
            "Recuperar contexto reutilizable para la generacion.",
            "Generar contenido Terraform por archivo.",
            "Validar cobertura y consistencia del proyecto.",
            "Construir y empaquetar el proyecto final en un zip.",
        ]

        if resources:
            steps.append("Recursos objetivo: " + ", ".join(resources))

        return steps

    def _determine_files(self, resources: List[str]) -> List[str]:
        files = ["provider.tf", "variables.tf", "terraform.tfvars", "outputs.tf", "README.md"]

        for resource in resources:
            candidate = self.FILE_MAP.get(resource)
            if candidate and candidate not in files:
                files.append(candidate)

        if "main.tf" not in files:
            files.append("main.tf")

        return files
