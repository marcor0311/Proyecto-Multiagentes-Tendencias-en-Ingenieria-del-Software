from typing import Any, Dict, List

from app.services.openai_service import safe_ask_azure_openai

class RetrieverAgent:
    RESOURCE_CATALOG = {
        "vpc": {
            "file": "network.tf",
            "summary": "Define la red principal donde se desplegaran los recursos.",
            "dependencies": [],
            "validation_hints": [
                "Verificar que el CIDR de la VPC exista.",
                "Revisar que la VPC tenga tags coherentes.",
            ],
        },
        "subnets": {
            "file": "network.tf",
            "summary": "Organiza subredes publicas y privadas dentro de la VPC.",
            "dependencies": ["vpc"],
            "validation_hints": [
                "Confirmar que existan rangos CIDR para subredes.",
                "Validar separacion entre subredes publicas y privadas.",
            ],
        },
        "security_groups": {
            "file": "security.tf",
            "summary": "Controla acceso de red para los recursos de aplicacion.",
            "dependencies": ["vpc"],
            "validation_hints": [
                "Comprobar que el security group apunte a la VPC principal.",
                "Evitar reglas excesivamente permisivas en una primera version.",
            ],
        },
        "ec2": {
            "file": "compute.tf",
            "summary": "Provisiona capacidad de computo para la aplicacion.",
            "dependencies": ["subnets", "security_groups"],
            "validation_hints": [
                "Asegurar que exista AMI y tipo de instancia.",
                "Revisar asociacion con subred y security group.",
            ],
        },
        "s3": {
            "file": "storage.tf",
            "summary": "Provisiona almacenamiento tipo objeto en AWS S3.",
            "dependencies": [],
            "validation_hints": [
                "Validar que el bucket tenga un nombre definido.",
                "Revisar convenciones de nombres y tags.",
            ],
        },
    }

    async def run(self, request_data: Dict[str, Any], plan: Dict[str, Any] = None) -> Dict[str, Any]:
        architecture = request_data.get("architecture", {})
        resources = architecture.get("resources", [])
        resource_context = []
        required_files = set(plan.get("target_files", [])) if isinstance(plan, dict) else set()
        validation_hints: List[str] = []

        for resource in resources:
            metadata = self.RESOURCE_CATALOG.get(resource)
            if not metadata:
                validation_hints.append(
                    f"No existe una plantilla conocida para el recurso '{resource}'."
                )
                continue

            required_files.add(metadata["file"])
            validation_hints.extend(metadata["validation_hints"])
            resource_context.append(
                {
                    "resource": resource,
                    "target_file": metadata["file"],
                    "summary": metadata["summary"],
                    "dependencies": metadata["dependencies"],
                    "validation_hints": metadata["validation_hints"],
                }
            )

        retrieval_summary = self._build_summary(request_data, resource_context, required_files)
        llm_retrieval_guidance = self._generate_llm_guidance(request_data, resource_context, required_files)

        return {
            "cloud_provider": request_data.get("cloud_provider", "aws"),
            "architecture_type": architecture.get("type", "custom"),
            "requested_resources": resources,
            "resource_context": resource_context,
            "required_files": sorted(required_files),
            "validation_hints": self._dedupe(validation_hints),
            "retrieval_summary": retrieval_summary,
            "llm_retrieval_guidance": llm_retrieval_guidance,
        }

    def _build_summary(
        self,
        request_data: Dict[str, Any],
        resource_context: List[Dict[str, Any]],
        required_files,
    ) -> str:
        project_name = request_data.get("project_name", "infra-project")
        resources = ", ".join(item["resource"] for item in resource_context) or "sin recursos reconocidos"
        files = ", ".join(sorted(required_files)) or "sin archivos sugeridos"
        return (
            f"Para el proyecto {project_name} se identificaron recursos Terraform AWS: {resources}. "
            f"Los archivos sugeridos son: {files}."
        )

    def _dedupe(self, items: List[str]) -> List[str]:
        ordered = []
        seen = set()
        for item in items:
            if item not in seen:
                ordered.append(item)
                seen.add(item)
        return ordered

    def _generate_llm_guidance(
        self,
        request_data: Dict[str, Any],
        resource_context: List[Dict[str, Any]],
        required_files,
    ) -> str | None:
        resources = ", ".join(item["resource"] for item in resource_context) or "sin recursos"
        files = ", ".join(sorted(required_files)) or "sin archivos"
        prompt = (
            "Eres un retriever agent para Terraform AWS. "
            "Explica brevemente que artefactos Terraform deben generarse y que dependencias son clave. "
            "Responde en espanol y en maximo 6 lineas.\n"
            f"Proyecto: {request_data.get('project_name', 'infra-project')}\n"
            f"Recursos: {resources}\n"
            f"Archivos: {files}"
        )
        return safe_ask_azure_openai(prompt, max_completion_tokens=220)
