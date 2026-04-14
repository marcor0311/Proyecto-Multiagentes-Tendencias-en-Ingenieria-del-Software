from typing import Any, Dict, List


class GeneratorAgent:

    async def run(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        retrieval_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        files = self._build_files(request_data, plan, retrieval_result)
        file_notes = self._build_file_notes(files)

        return {
            "summary": self._build_summary(request_data, retrieval_result),
            "key_points": [
                "El proyecto se genera para AWS con archivos Terraform separados por responsabilidad.",
                "La estructura considera provider, variables, tfvars, outputs y archivos por dominio.",
                "El contenido puede servir como base para refinar con modelos o plantillas mas avanzadas.",
            ],
            "recommended_actions": [
                "Ejecutar terraform fmt sobre los archivos generados.",
                "Ejecutar terraform validate antes de aplicar.",
                "Revisar manualmente reglas de seguridad y nombres finales.",
            ],
            "terraform_files": files,
            "file_notes": file_notes,
            "draft_response": self._build_draft_response(request_data, retrieval_result, files),
        }

    def _build_files(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        retrieval_result: Dict[str, Any],
    ) -> Dict[str, str]:
        resources = request_data.get("architecture", {}).get("resources", [])
        files = {
            "provider.tf": self._provider_tf(),
            "variables.tf": self._variables_tf(request_data),
            "terraform.tfvars": self._terraform_tfvars(request_data),
            "outputs.tf": self._outputs_tf(resources),
            "README.md": self._readme(request_data, plan, retrieval_result),
            "main.tf": self._main_tf(request_data, plan),
        }

        if "vpc" in resources or "subnets" in resources:
            files["network.tf"] = self._network_tf(request_data)
        if "security_groups" in resources:
            files["security.tf"] = self._security_tf()
        if "ec2" in resources:
            files["compute.tf"] = self._compute_tf()
        if "s3" in resources or request_data.get("storage", {}).get("create_s3_bucket"):
            files["storage.tf"] = self._storage_tf()

        return files

    def _provider_tf(self) -> str:
        return (
            'terraform {\n'
            '  required_version = ">= 1.5.7"\n'
            '  required_providers {\n'
            '    aws = {\n'
            '      source  = "hashicorp/aws"\n'
            '      version = ">= 6.39"\n'
            '    }\n'
            '  }\n'
            '}\n\n'
            'provider "aws" {\n'
            '  region = var.region\n'
            '}\n'
        )

    def _variables_tf(self, request_data: Dict[str, Any]) -> str:
        lines = [
            'variable "project_name" { type = string }',
            'variable "region" { type = string }',
            'variable "environment" { type = string }',
        ]

        if request_data.get("network"):
            lines.extend(
                [
                    'variable "vpc_cidr" { type = string }',
                    'variable "public_subnets" { type = list(string) }',
                    'variable "private_subnets" { type = list(string) }',
                ]
            )

        if request_data.get("compute"):
            lines.extend(
                [
                    'variable "ec2_instance_type" { type = string }',
                    'variable "ec2_count" { type = number }',
                    'variable "ami_id" { type = string }',
                ]
            )

        if request_data.get("storage", {}).get("create_s3_bucket"):
            lines.append('variable "s3_bucket_name" { type = string }')

        return "\n\n".join(lines) + "\n"

    def _terraform_tfvars(self, request_data: Dict[str, Any]) -> str:
        lines = [
            f'project_name = "{request_data.get("project_name", "infra-project")}"',
            f'region = "{request_data.get("region", "us-east-1")}"',
            f'environment = "{request_data.get("environment", "dev")}"',
        ]

        network = request_data.get("network") or {}
        if network:
            lines.append(f'vpc_cidr = "{network.get("vpc_cidr", "10.0.0.0/16")}"')
            lines.append(
                "public_subnets = [" + ", ".join(f'"{value}"' for value in network.get("public_subnets", [])) + "]"
            )
            lines.append(
                "private_subnets = [" + ", ".join(f'"{value}"' for value in network.get("private_subnets", [])) + "]"
            )

        compute = request_data.get("compute") or {}
        if compute:
            if compute.get("ec2_instance_type"):
                lines.append(f'ec2_instance_type = "{compute["ec2_instance_type"]}"')
            lines.append(f'ec2_count = {compute.get("ec2_count", 1)}')
            if compute.get("ami_id"):
                lines.append(f'ami_id = "{compute["ami_id"]}"')

        storage = request_data.get("storage") or {}
        if storage.get("create_s3_bucket") and storage.get("s3_bucket_name"):
            lines.append(f's3_bucket_name = "{storage["s3_bucket_name"]}"')

        return "\n".join(lines) + "\n"

    def _main_tf(self, request_data: Dict[str, Any], plan: Dict[str, Any]) -> str:
        return (
            f'# Terraform base para el proyecto "{request_data.get("project_name", "infra-project")}".\n'
            f'# Tipo de arquitectura: {request_data.get("architecture", {}).get("type", "custom")}.\n'
            f'# Objetivo: {plan.get("objective", "Generar infraestructura")}\n'
        )

    def _network_tf(self, request_data: Dict[str, Any]) -> str:
        network = request_data.get("network") or {}
        public_subnets = network.get("public_subnets", [])
        private_subnets = network.get("private_subnets", [])

        lines = [
            'resource "aws_vpc" "main" {',
            "  cidr_block = var.vpc_cidr",
            "",
            "  tags = {",
            '    Name = "${var.project_name}-${var.environment}-vpc"',
            "  }",
            "}",
        ]

        for index, _ in enumerate(public_subnets):
            lines.extend(
                [
                    "",
                    f'resource "aws_subnet" "public_{index}" {{',
                    "  vpc_id                  = aws_vpc.main.id",
                    f"  cidr_block              = var.public_subnets[{index}]",
                    "  map_public_ip_on_launch = true",
                    "}",
                ]
            )

        for index, _ in enumerate(private_subnets):
            lines.extend(
                [
                    "",
                    f'resource "aws_subnet" "private_{index}" {{',
                    "  vpc_id     = aws_vpc.main.id",
                    f"  cidr_block = var.private_subnets[{index}]",
                    "}",
                ]
            )

        return "\n".join(lines) + "\n"

    def _security_tf(self) -> str:
        return (
            'resource "aws_security_group" "app" {\n'
            '  name        = "${var.project_name}-${var.environment}-sg"\n'
            '  description = "Security group base para la aplicacion"\n'
            '  vpc_id      = aws_vpc.main.id\n'
            '}\n'
        )

    def _compute_tf(self) -> str:
        return (
            'resource "aws_instance" "app" {\n'
            '  count         = var.ec2_count\n'
            '  ami           = var.ami_id\n'
            '  instance_type = var.ec2_instance_type\n'
            '  subnet_id     = aws_subnet.public_0.id\n'
            '  vpc_security_group_ids = [aws_security_group.app.id]\n'
            '}\n'
        )

    def _storage_tf(self) -> str:
        return (
            'module "s3_bucket" {\n'
            '  source = "./modules/aws/s3-bucket"\n\n'
            '  bucket = var.s3_bucket_name\n'
            '  region = var.region\n'
            '}\n'
        )

    def _outputs_tf(self, resources: List[str]) -> str:
        outputs = ['output "project_name" { value = var.project_name }']
        if "vpc" in resources or "subnets" in resources:
            outputs.append('output "vpc_id" { value = aws_vpc.main.id }')
        if "ec2" in resources:
            outputs.append('output "instance_ids" { value = aws_instance.app[*].id }')
        if "s3" in resources:
            outputs.append('output "bucket_name" { value = module.s3_bucket.s3_bucket_id }')
            outputs.append('output "bucket_arn" { value = module.s3_bucket.s3_bucket_arn }')
        return "\n\n".join(outputs) + "\n"

    def _readme(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        retrieval_result: Dict[str, Any],
    ) -> str:
        steps = "\n".join(f"- {step}" for step in plan.get("steps", []))
        hints = "\n".join(f"- {hint}" for hint in retrieval_result.get("validation_hints", []))
        return (
            f"# {request_data.get('project_name', 'infra-project')}\n\n"
            "Proyecto Terraform generado por el sistema multiagente.\n\n"
            f"## Region\n{request_data.get('region', 'us-east-1')}\n\n"
            f"## Recursos\n{', '.join(request_data.get('architecture', {}).get('resources', []))}\n\n"
            "## Implementacion\n"
            "Para S3 se utiliza un modulo local con configuracion corporativa predefinida.\n\n"
            f"## Plan\n{steps}\n\n"
            f"## Pistas de validacion\n{hints}\n"
        )

    def _build_summary(self, request_data: Dict[str, Any], retrieval_result: Dict[str, Any]) -> str:
        return (
            f"Se generaron archivos Terraform para el proyecto {request_data.get('project_name', 'infra-project')} "
            f"con foco en {', '.join(retrieval_result.get('requested_resources', []))}."
        )

    def _build_file_notes(self, files: Dict[str, str]) -> List[Dict[str, Any]]:
        return [
            {"file": file_name, "line_count": content.count("\n") + 1}
            for file_name, content in files.items()
        ]

    def _build_draft_response(
        self,
        request_data: Dict[str, Any],
        retrieval_result: Dict[str, Any],
        files: Dict[str, str],
    ) -> str:
        return (
            f"Proyecto {request_data.get('project_name', 'infra-project')} listo para construccion. "
            f"Se prepararon {len(files)} archivos Terraform para AWS. "
            f"Recursos cubiertos: {', '.join(retrieval_result.get('requested_resources', []))}."
        )
