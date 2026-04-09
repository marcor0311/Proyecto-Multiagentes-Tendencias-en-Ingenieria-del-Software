from typing import Any, Dict, List

from app.kernel.kernel import kernel


class EvaluatorAgent:
    RESOURCE_FILE_RULES = {
        "vpc": "network.tf",
        "subnets": "network.tf",
        "security_groups": "security.tf",
        "ec2": "compute.tf",
        "s3": "storage.tf",
    }

    async def run(self, evaluation_input: Dict[str, Any]) -> Dict[str, Any]:
        kernel_trace = await kernel.invoke("evaluator", "terraform-validation")

        if not isinstance(evaluation_input, dict):
            return {
                "status": "invalid_input",
                "score": 0,
                "strengths": [],
                "issues": ["El evaluador requiere un diccionario con el estado del flujo."],
                "suggestions": ["Enviar plan, retrieval y generation de forma estructurada."],
                "missing_files": [],
                "missing_resource_coverage": [],
                "kernel_trace": kernel_trace,
            }

        request_data = evaluation_input.get("input", {})
        plan = evaluation_input.get("plan", {})
        retrieval = evaluation_input.get("retrieval", {})
        generation = evaluation_input.get("generation", {})

        requested_resources = request_data.get("architecture", {}).get("resources", [])
        expected_files = set(retrieval.get("required_files", []))
        generated_files = generation.get("terraform_files", {})
        generated_file_names = set(generated_files.keys())
        missing_files = sorted(expected_files - generated_file_names)
        missing_resource_coverage = self._find_missing_resource_coverage(
            requested_resources,
            generated_file_names,
        )

        strengths: List[str] = []
        issues: List[str] = []
        suggestions: List[str] = []
        score = 0

        if plan.get("steps"):
            strengths.append("El plan define etapas para generar y empaquetar IaC.")
            score += 25
        else:
            issues.append("El plan no define pasos claros para la generacion Terraform.")
            suggestions.append("Agregar pasos detallados desde el PlannerAgent.")

        if retrieval.get("resource_context"):
            strengths.append("La recuperacion identifica recursos AWS, archivos objetivo y dependencias.")
            score += 25
        else:
            issues.append("RetrieverAgent no devolvio contexto util para Terraform/AWS.")
            suggestions.append("Mapear recursos AWS a archivos y dependencias en el RetrieverAgent.")

        if generated_files:
            strengths.append("GeneratorAgent produjo archivos Terraform listos para construccion.")
            score += 25
        else:
            issues.append("GeneratorAgent no produjo contenido Terraform.")
            suggestions.append("Generar un diccionario terraform_files con el contenido de cada archivo.")

        if not missing_files and not missing_resource_coverage:
            strengths.append("La cobertura de archivos y recursos es consistente con la solicitud.")
            score += 25
        else:
            if missing_files:
                issues.append(
                    "Faltan archivos Terraform esperados: " + ", ".join(missing_files) + "."
                )
            if missing_resource_coverage:
                issues.append(
                    "No hay cobertura completa para recursos solicitados: "
                    + ", ".join(missing_resource_coverage)
                    + "."
                )
            suggestions.append("Alinear terraform_files con required_files y recursos solicitados.")

        if not suggestions:
            suggestions.append("Ejecutar terraform fmt y terraform validate sobre el zip generado.")

        return {
            "status": self._determine_status(score, missing_files, missing_resource_coverage),
            "score": score,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "missing_files": missing_files,
            "missing_resource_coverage": missing_resource_coverage,
            "kernel_trace": kernel_trace,
        }

    def _find_missing_resource_coverage(
        self,
        requested_resources: List[str],
        generated_file_names,
    ) -> List[str]:
        missing = []
        for resource in requested_resources:
            expected_file = self.RESOURCE_FILE_RULES.get(resource)
            if expected_file and expected_file not in generated_file_names:
                missing.append(resource)
        return missing

    def _determine_status(self, score: int, missing_files: List[str], missing_resource_coverage: List[str]) -> str:
        if missing_files or missing_resource_coverage:
            return "needs_revision"
        if score >= 85:
            return "approved"
        if score >= 60:
            return "needs_minor_improvements"
        return "needs_revision"
