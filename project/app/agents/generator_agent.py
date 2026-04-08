class GeneratorAgent:

    async def run(self, input_text, plan, retrieval_result):
        matched_topics = retrieval_result.get("matched_topics", [])
        topic_names = [topic["name"] for topic in matched_topics]
        key_points = [topic["summary"] for topic in matched_topics]
        recommended_actions = self._collect_actions(matched_topics)

        if topic_names:
            summary = "La solicitud se orienta principalmente a " + ", ".join(topic_names) + "."
        else:
            summary = (
                "La solicitud requiere una respuesta general basada en tendencias de ingenieria del software."
            )

        draft_response = self._build_draft_response(
            input_text,
            plan,
            retrieval_result.get("retrieval_summary", ""),
            matched_topics,
            recommended_actions,
        )

        return {
            "summary": summary,
            "key_points": key_points,
            "recommended_actions": recommended_actions,
            "draft_response": draft_response,
        }

    def _collect_actions(self, matched_topics):
        collected_actions = []

        for topic in matched_topics:
            for action in topic.get("recommended_actions", []):
                if action not in collected_actions:
                    collected_actions.append(action)

        return collected_actions[:5]

    def _build_draft_response(
        self,
        input_text,
        plan,
        retrieval_summary,
        matched_topics,
        recommended_actions,
    ):
        plan_description = self._format_plan(plan)
        response_lines = [
            f"Solicitud original: {input_text}",
            f"Plan preliminar: {plan_description}",
            f"Contexto recuperado: {retrieval_summary}",
            "",
            "Hallazgos clave:",
        ]

        if matched_topics:
            for topic in matched_topics:
                response_lines.append(f"- {topic['name']}: {topic['summary']}")
        else:
            response_lines.append(
                "- No se encontraron temas especificos, por lo que conviene responder con una vista general del dominio."
            )

        response_lines.append("")
        response_lines.append("Acciones recomendadas:")

        if recommended_actions:
            for action in recommended_actions:
                response_lines.append(f"- {action}")
        else:
            response_lines.append(
                "- Refinar la solicitud para identificar tendencias o dominios concretos."
            )

        return "\n".join(response_lines)

    def _format_plan(self, plan):
        if not isinstance(plan, dict):
            return str(plan)

        task_type = plan.get("task_type", "general_analysis")
        expected_output = plan.get("expected_output", "respuesta estructurada")
        steps = plan.get("steps", [])
        first_steps = "; ".join(steps[:3]) if steps else "sin pasos definidos"

        return (
            f"tipo={task_type}, salida={expected_output}, pasos iniciales={first_steps}"
        )
