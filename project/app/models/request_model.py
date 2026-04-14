from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, constr


NonEmptyStr = constr(strip_whitespace=True, min_length=1)


class ResourceItemModel(BaseModel):
    type: NonEmptyStr
    name: NonEmptyStr


class RequestModel(BaseModel):
    project_name: constr(strip_whitespace=True, min_length=3, max_length=100)
    cloud_provider: Literal["aws"]
    region: NonEmptyStr
    environment: Literal["dev", "qa", "staging", "prod"]
    resources: List[ResourceItemModel] = Field(min_items=1)

    class Config:
        extra = "forbid"

    def to_agent_payload(self) -> Dict[str, object]:
        resource_types = self._unique_resource_types()
        s3_bucket_name = self._first_resource_name("s3")
        ec2_count = self._count_resources("ec2")

        payload: Dict[str, object] = {
            "project_name": self.project_name,
            "cloud_provider": self.cloud_provider,
            "region": self.region,
            "environment": self.environment,
            "resources": [resource.dict() for resource in self.resources],
            "architecture": {
                "type": self._infer_architecture_type(resource_types),
                "resources": resource_types,
            },
            "network": None,
            "compute": None,
            "storage": None,
            "tags": {},
        }

        if ec2_count:
            payload["compute"] = {
                "ec2_instance_type": "t3.micro",
                "ec2_count": ec2_count,
            }

        if s3_bucket_name:
            payload["storage"] = {
                "create_s3_bucket": True,
                "s3_bucket_name": s3_bucket_name,
            }

        return payload

    def to_summary_prompt(self) -> str:
        resource_types = ", ".join(self._unique_resource_types())
        return (
            f"Proyecto {self.project_name} para {self.cloud_provider} en {self.region}, "
            f"ambiente {self.environment}, recursos solicitados: {resource_types}."
        )

    def _unique_resource_types(self) -> List[str]:
        ordered: List[str] = []
        seen = set()

        for resource in self.resources:
            if resource.type not in seen:
                ordered.append(resource.type)
                seen.add(resource.type)

        return ordered

    def _first_resource_name(self, resource_type: str) -> Optional[str]:
        for resource in self.resources:
            if resource.type == resource_type:
                return resource.name
        return None

    def _count_resources(self, resource_type: str) -> int:
        return sum(1 for resource in self.resources if resource.type == resource_type)

    def _infer_architecture_type(self, resource_types: List[str]) -> str:
        if len(resource_types) == 1 and resource_types[0] == "s3":
            return "static_site"
        if "ec2" in resource_types:
            return "web_app"
        if "lambda" in resource_types:
            return "api"
        return "custom"
