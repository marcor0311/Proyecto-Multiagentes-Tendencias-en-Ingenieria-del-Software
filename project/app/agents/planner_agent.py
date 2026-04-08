import re

from app.kernel.kernel import kernel


class PlannerAgent:
    TASK_PATTERNS = (
        ("comparative_analysis", {"comparar", "comparacion", "comparative", "versus", "vs"}),
        ("implementation_plan", {"implementar", "implementation", "integrar", "construir"}),
        ("trend_analysis", {"tendencia", "tendencias", "trend", "trends", "analiza", "analisis"}),
        ("recommendation", {"recomendar", "recomendacion", "sugerir", "mejor"}),
    )

    PRIORITY_KEYWORDS = {
        "ai": "Evaluar oportunidades de automatizacion asistida por IA.",
        "devsecops": "Integrar seguridad dentro del ciclo de entrega.",
        "observabilidad": "Definir metricas y trazabilidad operativa.",
        "platform": "Mejorar la experiencia del desarrollador con capacidades internas.",
        "calidad": "Asegurar mecanismos de validacion temprana.",
        "pruebas": "Cubrir rutas criticas mediante automatizacion.",
    }

    async def run(self, input_text):
        normalized_text = self._normalize(input_text)
        tokens = normalized_text.split()
        task_type = self._detect_task_type(tokens)
        focus_areas = self._extract_focus_areas(tokens)
        steps = self._build_steps(task_type, focus_areas)
        kernel_trace = await kernel.invoke("planner", input_text)

        return {
            "objective": input_text,
            "task_type": task_type,
            "focus_areas": focus_areas,
            "steps": steps,
            "expected_output": self._build_expected_output(task_type),
            "kernel_trace": kernel_trace,
        }

    def _normalize(self, text):
        normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return re.sub(r"\s+", " ", normalized).strip()

    def _detect_task_type(self, tokens):
        token_set = set(tokens)

        for task_type, keywords in self.TASK_PATTERNS:
            if token_set.intersection(keywords):
                return task_type

        return "general_analysis"

    def _extract_focus_areas(self, tokens):
        focus_areas = []
        token_set = set(tokens)

        for keyword, description in self.PRIORITY_KEYWORDS.items():
            if keyword in token_set:
                focus_areas.append(description)

        if not focus_areas:
            focus_areas.append("Identificar tendencias y oportunidades relevantes para la solicitud.")

        return focus_areas[:4]

    def _build_steps(self, task_type, focus_areas):
        steps = [
            "Aclarar el objetivo principal de la solicitud.",
            "Identificar los temas o dominios mas relevantes.",
            "Recuperar contexto util para sustentar la respuesta.",
        ]

        if task_type == "comparative_analysis":
            steps.append("Comparar alternativas usando criterios consistentes.")
        elif task_type == "implementation_plan":
            steps.append("Traducir los hallazgos en un plan de implementacion incremental.")
        elif task_type == "recommendation":
            steps.append("Priorizar recomendaciones segun impacto y esfuerzo.")
        else:
            steps.append("Sintetizar las tendencias clave y su impacto esperado.")

        steps.append("Generar una respuesta clara para el usuario.")
        steps.extend(focus_areas)

        # Remove duplicates while preserving order.
        ordered_steps = []
        seen = set()
        for step in steps:
            if step not in seen:
                ordered_steps.append(step)
                seen.add(step)

        return ordered_steps

    def _build_expected_output(self, task_type):
        if task_type == "comparative_analysis":
            return "Comparacion estructurada con criterios, ventajas, riesgos y conclusion."
        if task_type == "implementation_plan":
            return "Plan por etapas con prioridades, dependencias y proximos pasos."
        if task_type == "recommendation":
            return "Lista priorizada de recomendaciones con justificacion."
        if task_type == "trend_analysis":
            return "Resumen de tendencias con implicaciones practicas."
        return "Respuesta sintetica, estructurada y accionable."
