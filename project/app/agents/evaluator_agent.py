from app.kernel.kernel import kernel


class EvaluatorAgent:

    async def run(self, evaluation_input):
        kernel_trace = await kernel.invoke("evaluator", "validation")

        if not isinstance(evaluation_input, dict):
            return {
                "status": "invalid_input",
                "score": 0,
                "strengths": [],
                "issues": ["El evaluador requiere un diccionario con el estado del flujo."],
                "suggestions": ["Enviar al evaluador el resultado estructurado del pipeline."],
                "kernel_trace": kernel_trace,
            }

        strengths = []
        issues = []
        suggestions = []
        score = 0

        plan = evaluation_input.get("plan", {})
        retrieval = evaluation_input.get("retrieval", {})
        generation = evaluation_input.get("generation", {})

        plan_steps = plan.get("steps", []) if isinstance(plan, dict) else []
        if plan_steps:
            score += 30
            strengths.append("El plan contiene pasos definidos para resolver la solicitud.")
        else:
            issues.append("El plan no incluye pasos accionables.")
            suggestions.append("Agregar una secuencia clara de trabajo en el PlannerAgent.")

        matched_topics = retrieval.get("matched_topics", []) if isinstance(retrieval, dict) else []
        if matched_topics:
            score += 30
            strengths.append("La recuperacion de contexto encontro temas relacionados con la solicitud.")
        else:
            issues.append("No se recupero contexto tematico relevante.")
            suggestions.append("Ampliar el catalogo o las reglas de deteccion del RetrieverAgent.")

        draft_response = generation.get("draft_response", "") if isinstance(generation, dict) else ""
        if draft_response:
            score += 25
            strengths.append("La generacion produjo un borrador de respuesta para el usuario.")
        else:
            issues.append("La salida generada no contiene un borrador de respuesta.")
            suggestions.append("Construir una salida final mas completa dentro del GeneratorAgent.")

        recommended_actions = generation.get("recommended_actions", []) if isinstance(generation, dict) else []
        if recommended_actions:
            score += 15
            strengths.append("La respuesta incluye acciones recomendadas.")
        else:
            issues.append("La respuesta no sugiere acciones concretas.")
            suggestions.append("Incluir proximos pasos accionables en la generacion.")

        if not suggestions:
            suggestions.append("Conectar los agentes a una fuente real de conocimiento y a un modelo de lenguaje.")

        status = self._determine_status(score)

        return {
            "status": status,
            "score": score,
            "strengths": strengths,
            "issues": issues,
            "suggestions": suggestions,
            "kernel_trace": kernel_trace,
        }

    def _determine_status(self, score):
        if score >= 85:
            return "approved"
        if score >= 60:
            return "needs_minor_improvements"
        return "needs_revision"
