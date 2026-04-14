export type ResourceConfig = {
  type: string;
  name: string;
};

export type IaCFormData = {
  project_name: string;
  cloud_provider: string;
  region: string;
  environment: string;
  resources: ResourceConfig[];
};

export type ResourceTypeOption = {
  value: string;
  label: string;
};
