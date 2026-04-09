from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, constr


NonEmptyStr = constr(strip_whitespace=True, min_length=1)


class ArchitectureModel(BaseModel):
    type: Literal["web_app", "api", "batch", "static_site", "custom"]
    resources: List[NonEmptyStr] = Field(min_items=1)


class NetworkModel(BaseModel):
    vpc_cidr: NonEmptyStr
    public_subnets: List[NonEmptyStr] = Field(default_factory=list)
    private_subnets: List[NonEmptyStr] = Field(default_factory=list)


class ComputeModel(BaseModel):
    ec2_instance_type: Optional[NonEmptyStr] = None
    ec2_count: int = Field(default=1, ge=1, le=20)
    ami_id: Optional[NonEmptyStr] = None


class StorageModel(BaseModel):
    create_s3_bucket: bool = False
    s3_bucket_name: Optional[NonEmptyStr] = None


class RequestModel(BaseModel):
    project_name: constr(strip_whitespace=True, min_length=3, max_length=100)
    cloud_provider: Literal["aws"]
    region: NonEmptyStr
    environment: Literal["dev", "qa", "staging", "prod"]
    architecture: ArchitectureModel
    network: Optional[NetworkModel] = None
    compute: Optional[ComputeModel] = None
    storage: Optional[StorageModel] = None
    tags: Dict[NonEmptyStr, NonEmptyStr] = Field(default_factory=dict)

    def to_summary_prompt(self) -> str:
        resources = ", ".join(self.architecture.resources)
        return (
            f"Proyecto {self.project_name} para {self.cloud_provider} en {self.region}, "
            f"ambiente {self.environment}, arquitectura {self.architecture.type}, "
            f"recursos solicitados: {resources}."
        )
