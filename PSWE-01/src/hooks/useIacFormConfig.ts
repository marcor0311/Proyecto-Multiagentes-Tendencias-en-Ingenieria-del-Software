import * as Yup from 'yup';
import type { IaCFormData, ResourceConfig, ResourceTypeOption } from '../types/iac';

export const resourceTypeOptions: ResourceTypeOption[] = [
  { value: 's3', label: 'S3 Bucket' },
  { value: 'cloudfront', label: 'CloudFront Distribution' },
  { value: 'ec2', label: 'EC2 Instance' },
  { value: 'lambda', label: 'Lambda Function' },
  { value: 'dynamodb', label: 'DynamoDB Table' }
];

export const createEmptyResource = (): ResourceConfig => ({
  type: 's3',
  name: ''
});

export const initialValues: IaCFormData = {
  project_name: 'demo-s3-module',
  cloud_provider: 'aws',
  region: 'us-east-1',
  environment: 'dev',
  resources: [
    {
      type: 's3',
      name: 'tendencias-bucket'
    }
  ]
};

export const validationSchema = Yup.object({
  project_name: Yup.string().trim().min(3, 'Usa al menos 3 caracteres.').required('Este campo es obligatorio.'),
  cloud_provider: Yup.string().oneOf(['aws']).required('Selecciona un proveedor.'),
  region: Yup.string().required('Selecciona una región.'),
  environment: Yup.string().required('Selecciona un ambiente.'),
  resources: Yup.array()
    .of(
      Yup.object({
        type: Yup.string().required('Selecciona un tipo de recurso.'),
        name: Yup.string()
          .trim()
          .matches(/^[a-z0-9-]+$/, 'Usa minúsculas, números y guiones.')
          .min(3, 'Usa al menos 3 caracteres.')
          .required('Ingresa un nombre para el recurso.')
      })
    )
    .min(1, 'Debes agregar al menos un recurso.')
    .required()
});

export function useIacFormConfig() {
  return {
    createEmptyResource,
    initialValues,
    resourceTypeOptions,
    validationSchema
  };
}
