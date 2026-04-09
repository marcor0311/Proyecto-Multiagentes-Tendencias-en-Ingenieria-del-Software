from pathlib import Path
from typing import Any, Dict
from zipfile import ZIP_DEFLATED, ZipFile


class BuilderAgent:

    async def run(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        generation: Dict[str, Any],
    ) -> Dict[str, Any]:
        project_name = self._sanitize_name(request_data.get("project_name", "infra-project"))
        output_root = Path(__file__).resolve().parents[2] / "generated"
        project_dir = output_root / project_name
        zip_path = output_root / f"{project_name}.zip"

        files = generation.get("terraform_files") or self._build_files(request_data, plan, generation)
        project_dir.mkdir(parents=True, exist_ok=True)

        for file_name, content in files.items():
            (project_dir / file_name).write_text(content, encoding="utf-8")

        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            for file_name in files:
                archive.write(project_dir / file_name, arcname=file_name)

        return {
            "project_name": project_name,
            "output_dir": str(project_dir),
            "zip_path": str(zip_path),
            "files_created": list(files.keys()),
            "status": "success",
        }

    def _build_files(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        generation: Dict[str, Any],
    ) -> Dict[str, str]:
        resources = request_data.get("architecture", {}).get("resources", [])
        files = {
            "provider.tf": self._provider_tf(request_data),
            "variables.tf": self._variables_tf(request_data),
            "terraform.tfvars": self._terraform_tfvars(request_data),
            "outputs.tf": self._outputs_tf(resources),
            "README.md": self._project_readme(request_data, plan, generation),
            "main.tf": self._main_tf(request_data),
        }

        if "vpc" in resources or "subnets" in resources:
            files["network.tf"] = self._network_tf(request_data)
        if "security_groups" in resources:
            files["security.tf"] = self._security_tf()
        if "ec2" in resources:
            files["compute.tf"] = self._compute_tf(request_data)
        if "s3" in resources or request_data.get("storage", {}).get("create_s3_bucket"):
            files["storage.tf"] = self._storage_tf(request_data)

        return files

    def _provider_tf(self, request_data: Dict[str, Any]) -> str:
        return (
            'terraform {\n'
            '  required_version = ">= 1.5.0"\n'
            '  required_providers {\n'
            '    aws = {\n'
            '      source  = "hashicorp/aws"\n'
            '      version = "~> 5.0"\n'
            '    }\n'
            '  }\n'
            '}\n\n'
            'provider "aws" {\n'
            '  region = var.region\n'
            '}\n'
        )

    def _variables_tf(self, request_data: Dict[str, Any]) -> str:
        base = [
            'variable "project_name" { type = string }',
            'variable "region" { type = string }',
            'variable "environment" { type = string }',
        ]

        if request_data.get("network"):
            base.extend(
                [
                    'variable "vpc_cidr" { type = string }',
                    'variable "public_subnets" { type = list(string) }',
                    'variable "private_subnets" { type = list(string) }',
                ]
            )

        if request_data.get("compute"):
            base.extend(
                [
                    'variable "ec2_instance_type" { type = string }',
                    'variable "ec2_count" { type = number }',
                    'variable "ami_id" { type = string }',
                ]
            )

        if request_data.get("storage", {}).get("create_s3_bucket"):
            base.append('variable "s3_bucket_name" { type = string }')

        return "\n\n".join(base) + "\n"

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
                "public_subnets = [" + ", ".join(f'"{item}"' for item in network.get("public_subnets", [])) + "]"
            )
            lines.append(
                "private_subnets = [" + ", ".join(f'"{item}"' for item in network.get("private_subnets", [])) + "]"
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

    def _main_tf(self, request_data: Dict[str, Any]) -> str:
        architecture_type = request_data.get("architecture", {}).get("type", "custom")
        return (
            f'# Proyecto Terraform base para una arquitectura tipo "{architecture_type}".\n'
            '# Este archivo puede servir como punto de entrada para modulos o recursos compartidos.\n'
        )

    def _network_tf(self, request_data: Dict[str, Any]) -> str:
        return (
            'resource "aws_vpc" "main" {\n'
            '  cidr_block = var.vpc_cidr\n\n'
            '  tags = {\n'
            '    Name = "${var.project_name}-${var.environment}-vpc"\n'
            '  }\n'
            '}\n'
        )

    def _security_tf(self) -> str:
        return (
            'resource "aws_security_group" "web" {\n'
            '  name        = "${var.project_name}-${var.environment}-sg"\n'
            '  description = "Security group base para la aplicacion"\n'
            '  vpc_id      = aws_vpc.main.id\n'
            '}\n'
        )

    def _compute_tf(self, request_data: Dict[str, Any]) -> str:
        return (
            'resource "aws_instance" "app" {\n'
            '  count         = var.ec2_count\n'
            '  ami           = var.ami_id\n'
            '  instance_type = var.ec2_instance_type\n\n'
            '  tags = {\n'
            '    Name = "${var.project_name}-${var.environment}-ec2-${count.index}"\n'
            '  }\n'
            '}\n'
        )

    def _storage_tf(self, request_data: Dict[str, Any]) -> str:
        return (
            'resource "aws_s3_bucket" "artifacts" {\n'
            '  bucket = var.s3_bucket_name\n\n'
            '  tags = {\n'
            '    Name = "${var.project_name}-${var.environment}-bucket"\n'
            '  }\n'
            '}\n'
        )

    def _outputs_tf(self, resources) -> str:
        blocks = ['output "project_name" { value = var.project_name }']
        if "vpc" in resources or "subnets" in resources:
            blocks.append('output "vpc_id" { value = aws_vpc.main.id }')
        if "ec2" in resources:
            blocks.append('output "instance_ids" { value = aws_instance.app[*].id }')
        if "s3" in resources:
            blocks.append('output "s3_bucket_name" { value = aws_s3_bucket.artifacts.bucket }')
        return "\n\n".join(blocks) + "\n"

    def _project_readme(
        self,
        request_data: Dict[str, Any],
        plan: Dict[str, Any],
        generation: Dict[str, Any],
    ) -> str:
        resources = ", ".join(request_data.get("architecture", {}).get("resources", []))
        steps = "\n".join(f"- {step}" for step in plan.get("steps", []))
        return (
            f"# {request_data.get('project_name', 'infra-project')}\n\n"
            "Proyecto Terraform generado por el sistema multiagente.\n\n"
            f"## Region\n{request_data.get('region', 'us-east-1')}\n\n"
            f"## Recursos solicitados\n{resources}\n\n"
            f"## Plan del PlannerAgent\n{steps}\n\n"
            "## Borrador del GeneratorAgent\n"
            f"{generation.get('draft_response', 'Sin borrador disponible.')}\n"
        )

    def _sanitize_name(self, name: str) -> str:
        return "".join(char if char.isalnum() or char in ("-", "_") else "-" for char in name)
