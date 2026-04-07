import re
from collections import Counter


class RetrieverAgent:
    DEFAULT_TOPIC_NAMES = (
        "AI-assisted development",
        "DevSecOps",
        "Platform engineering",
    )

    STOPWORDS = {
        "a",
        "al",
        "algo",
        "analiza",
        "analizar",
        "and",
        "con",
        "como",
        "cuenta",
        "de",
        "del",
        "el",
        "en",
        "es",
        "for",
        "la",
        "las",
        "los",
        "mas",
        "me",
        "necesito",
        "of",
        "para",
        "por",
        "que",
        "quiero",
        "se",
        "software",
        "sobre",
        "the",
        "to",
        "un",
        "una",
        "y",
    }

    TOPIC_CATALOG = (
        {
            "name": "AI-assisted development",
            "keywords": {
                "ai",
                "asistida",
                "automatizacion",
                "copilot",
                "generativa",
                "ia",
                "llm",
                "modelo",
                "multiagentes",
                "prompt",
            },
            "summary": "Integra asistentes basados en IA para acelerar analisis, generacion de codigo, documentacion y soporte al equipo.",
            "signals": [
                "Uso de LLMs para tareas de desarrollo.",
                "Automatizacion de flujos repetitivos con agentes.",
            ],
            "recommended_actions": [
                "Definir casos de uso concretos para asistentes de IA.",
                "Establecer controles de calidad humana sobre salidas generadas.",
            ],
        },
        {
            "name": "DevSecOps",
            "keywords": {
                "cicd",
                "compliance",
                "devsecops",
                "pipeline",
                "sast",
                "seguridad",
                "supply",
                "vulnerabilidades",
            },
            "summary": "Lleva controles de seguridad al ciclo de entrega continua para detectar riesgos temprano y reducir retrabajo.",
            "signals": [
                "Escaneo automatizado de dependencias y codigo.",
                "Seguridad integrada dentro del pipeline de despliegue.",
            ],
            "recommended_actions": [
                "Agregar escaneos de seguridad al pipeline de CI/CD.",
                "Definir politicas minimas para dependencias y secretos.",
            ],
        },
        {
            "name": "Platform engineering",
            "keywords": {
                "developer",
                "dx",
                "idp",
                "interna",
                "plataforma",
                "platform",
                "productividad",
                "self-service",
            },
            "summary": "Crea plataformas internas para mejorar la experiencia del desarrollador y estandarizar la entrega de software.",
            "signals": [
                "Provisionamiento self-service para equipos.",
                "Estandares compartidos para despliegue y observabilidad.",
            ],
            "recommended_actions": [
                "Identificar cuellos de botella recurrentes para los equipos.",
                "Disenar servicios internos reutilizables y faciles de adoptar.",
            ],
        },
        {
            "name": "Cloud native",
            "keywords": {
                "cloud",
                "contenedores",
                "docker",
                "kubernetes",
                "microservicios",
                "nube",
                "serverless",
            },
            "summary": "Promueve arquitecturas distribuidas y elasticas apoyadas en contenedores, orquestacion y despliegue automatizado.",
            "signals": [
                "Despliegue sobre infraestructura elastica.",
                "Servicios desacoplados y escalables.",
            ],
            "recommended_actions": [
                "Evaluar que componentes realmente necesitan ser distribuidos.",
                "Definir observabilidad y costos desde el diseno inicial.",
            ],
        },
        {
            "name": "Observability and SRE",
            "keywords": {
                "incident",
                "metricas",
                "monitoreo",
                "observabilidad",
                "slo",
                "telemetria",
                "tracing",
            },
            "summary": "Mide el comportamiento del sistema con metricas, logs y trazas para mejorar confiabilidad y tiempo de respuesta.",
            "signals": [
                "Uso de SLIs y SLOs como guias operativas.",
                "Analisis de incidentes y visibilidad de extremo a extremo.",
            ],
            "recommended_actions": [
                "Definir indicadores operativos alineados con el negocio.",
                "Centralizar logs, metricas y trazas en una misma estrategia.",
            ],
        },
        {
            "name": "Quality engineering",
            "keywords": {
                "automatizadas",
                "calidad",
                "pruebas",
                "qa",
                "test",
                "testing",
                "validacion",
            },
            "summary": "Amplia el enfoque de pruebas hacia una disciplina continua de calidad con automatizacion y retroalimentacion temprana.",
            "signals": [
                "Automatizacion de pruebas funcionales y de regresion.",
                "Controles de calidad integrados al flujo de entrega.",
            ],
            "recommended_actions": [
                "Priorizar pruebas sobre rutas criticas del producto.",
                "Combinar pruebas unitarias, integracion y contrato.",
            ],
        },
    )

    async def run(self, input_text, plan=None):
        normalized_text = self._normalize(input_text)
        tokens = normalized_text.split()
        keywords = self._extract_keywords(tokens)
        matched_topics = self._match_topics(tokens, normalized_text)
        retrieval_summary = self._build_summary(input_text, matched_topics, plan)

        return {
            "query": input_text,
            "keywords": keywords,
            "matched_topics": matched_topics,
            "retrieval_summary": retrieval_summary,
        }

    def _normalize(self, text):
        normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _extract_keywords(self, tokens):
        filtered_tokens = [
            token for token in tokens if len(token) > 3 and token not in self.STOPWORDS
        ]
        frequency = Counter(filtered_tokens)
        return [keyword for keyword, _ in frequency.most_common(6)]

    def _match_topics(self, tokens, normalized_text):
        matches = []
        unique_tokens = set(tokens)

        for topic in self.TOPIC_CATALOG:
            keyword_hits = sorted(topic["keywords"].intersection(unique_tokens))
            score = len(keyword_hits)

            if score == 0 and topic["name"].lower() in normalized_text:
                score = 1

            if score > 0:
                matches.append(
                    {
                        "name": topic["name"],
                        "relevance": score,
                        "summary": topic["summary"],
                        "signals": topic["signals"],
                        "recommended_actions": topic["recommended_actions"],
                        "matched_keywords": keyword_hits,
                    }
                )

        if not matches:
            matches = [
                {
                    "name": topic["name"],
                    "relevance": 1,
                    "summary": topic["summary"],
                    "signals": topic["signals"],
                    "recommended_actions": topic["recommended_actions"],
                    "matched_keywords": [],
                }
                for topic in self.TOPIC_CATALOG
                if topic["name"] in self.DEFAULT_TOPIC_NAMES
            ]

        matches.sort(key=lambda item: (-item["relevance"], item["name"]))
        return matches[:3]

    def _build_summary(self, input_text, matched_topics, plan):
        topic_names = ", ".join(topic["name"] for topic in matched_topics)
        plan_reference = ""

        if isinstance(plan, dict):
            plan_type = plan.get("task_type", "general_analysis")
            expected_output = plan.get("expected_output", "respuesta estructurada")
            plan_reference = (
                f" Plan base: tipo {plan_type}, salida esperada {expected_output}."
            )
        elif plan:
            plan_reference = f" Plan base: {plan}."

        return (
            f"Para la solicitud '{input_text}' se identificaron como focos principales: "
            f"{topic_names}.{plan_reference}"
        )
