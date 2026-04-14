import { Button, Form } from 'react-bootstrap';
import { FieldArray, getIn, type FormikProps } from 'formik';
import styles from '../App.module.scss';
import type { IaCFormData, ResourceTypeOption } from '../types/iac';

type PayloadFormProps = {
  formik: FormikProps<IaCFormData>;
  createEmptyResource: () => { type: string; name: string };
  isSubmitting: boolean;
  resourceTypeOptions: ResourceTypeOption[];
  responseData: Record<string, unknown> | null;
  submitError: string | null;
};

function PayloadForm({
  formik,
  createEmptyResource,
  isSubmitting,
  resourceTypeOptions,
  responseData,
  submitError
}: PayloadFormProps) {
  const { values, errors, touched, handleChange, handleBlur, handleSubmit } = formik;
  const resourcesError =
    touched.resources && typeof errors.resources === 'string' ? errors.resources : null;
  const responsePreview = responseData ? JSON.stringify(responseData, null, 2) : null;

  return (
    <div className={styles.formPanel}>
      <div className={styles.formHeader}>
        <p className={styles.formIntro}>Request estructurado</p>
        <h2>Configura el payload AWS</h2>
        <p className={styles.formText}>
          Define datos globales del proyecto y luego agrega uno o más recursos para construir una
          solicitud Terraform mucho más completa.
        </p>
      </div>

      <Form noValidate onSubmit={handleSubmit} className={styles.formSection}>
        <div className={styles.gridTwo}>
          <Form.Group className={styles.fieldGroup} controlId="project_name">
            <Form.Label className={styles.fieldLabel}>Nombre del proyecto</Form.Label>
            <Form.Control
              className={styles.inputControl}
              type="text"
              name="project_name"
              placeholder="demo-s3-module"
              value={values.project_name}
              onChange={handleChange}
              onBlur={handleBlur}
              isInvalid={Boolean(touched.project_name && errors.project_name)}
            />
            <Form.Control.Feedback type="invalid" className={styles.errorText}>
              {errors.project_name}
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className={styles.fieldGroup} controlId="cloud_provider">
            <Form.Label className={styles.fieldLabel}>Cloud provider</Form.Label>
            <Form.Select
              className={styles.inputControl}
              name="cloud_provider"
              value={values.cloud_provider}
              onChange={handleChange}
              onBlur={handleBlur}
              isInvalid={Boolean(touched.cloud_provider && errors.cloud_provider)}
            >
              <option value="aws">AWS</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid" className={styles.errorText}>
              {errors.cloud_provider}
            </Form.Control.Feedback>
          </Form.Group>
        </div>

        <div className={styles.gridThree}>
          <Form.Group className={styles.fieldGroup} controlId="region">
            <Form.Label className={styles.fieldLabel}>Región AWS</Form.Label>
            <Form.Select
              className={styles.inputControl}
              name="region"
              value={values.region}
              onChange={handleChange}
              onBlur={handleBlur}
              isInvalid={Boolean(touched.region && errors.region)}
            >
              <option value="us-east-1">us-east-1</option>
              <option value="us-east-2">us-east-2</option>
              <option value="us-west-2">us-west-2</option>
              <option value="eu-west-1">eu-west-1</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid" className={styles.errorText}>
              {errors.region}
            </Form.Control.Feedback>
          </Form.Group>

          <Form.Group className={styles.fieldGroup} controlId="environment">
            <Form.Label className={styles.fieldLabel}>Ambiente</Form.Label>
            <Form.Select
              className={styles.inputControl}
              name="environment"
              value={values.environment}
              onChange={handleChange}
              onBlur={handleBlur}
              isInvalid={Boolean(touched.environment && errors.environment)}
            >
              <option value="dev">dev</option>
              <option value="qa">qa</option>
              <option value="prod">prod</option>
            </Form.Select>
            <Form.Control.Feedback type="invalid" className={styles.errorText}>
              {errors.environment}
            </Form.Control.Feedback>
          </Form.Group>

          <div className={styles.metaCard}>
            <span>Formato</span>
            <strong>{values.resources.length} recurso(s)</strong>
          </div>
        </div>

        <FieldArray name="resources">
          {({ push, remove }) => (
            <div className={styles.resourcesSection}>
              <div className={styles.sectionHeader}>
                <div>
                  <p className={styles.resourceEyebrow}>Recursos</p>
                  <h3 className={styles.sectionTitle}>Lista de recursos AWS</h3>
                </div>
                <Button
                  type="button"
                  className={styles.secondaryButton}
                  onClick={() => push(createEmptyResource())}
                >
                  Agregar recurso
                </Button>
              </div>

              {resourcesError ? <div className={styles.arrayError}>{resourcesError}</div> : null}

              <div className={styles.resourceList}>
                {values.resources.map((resource, index) => {
                  const typePath = `resources.${index}.type`;
                  const namePath = `resources.${index}.name`;
                  const typeError = getIn(errors, typePath);
                  const nameError = getIn(errors, namePath);
                  const typeTouched = getIn(touched, typePath);
                  const nameTouched = getIn(touched, namePath);

                  return (
                    <div key={`${resource.type}-${index}`} className={styles.resourceCard}>
                      <div className={styles.resourceHeader}>
                        <div>
                          <p className={styles.resourceEyebrow}>
                            Recurso {String(index + 1).padStart(2, '0')}
                          </p>
                          <h3>Definición del recurso</h3>
                        </div>
                        <div className={styles.resourceActions}>
                          <span className={styles.resourcePill}>AWS</span>
                          {values.resources.length > 1 ? (
                            <button
                              type="button"
                              className={styles.removeButton}
                              onClick={() => remove(index)}
                            >
                              Quitar
                            </button>
                          ) : null}
                        </div>
                      </div>

                      <div className={styles.gridTwo}>
                        <Form.Group className={styles.fieldGroup} controlId={`resource_type_${index}`}>
                          <Form.Label className={styles.fieldLabel}>Tipo de recurso</Form.Label>
                          <Form.Select
                            className={styles.inputControl}
                            name={typePath}
                            value={resource.type}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            isInvalid={Boolean(typeTouched && typeError)}
                          >
                            {resourceTypeOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </Form.Select>
                          <Form.Control.Feedback type="invalid" className={styles.errorText}>
                            {typeError}
                          </Form.Control.Feedback>
                        </Form.Group>

                        <Form.Group className={styles.fieldGroup} controlId={`resource_name_${index}`}>
                          <Form.Label className={styles.fieldLabel}>Nombre del recurso</Form.Label>
                          <Form.Control
                            className={styles.inputControl}
                            type="text"
                            name={namePath}
                            placeholder="tendencias-bucket"
                            value={resource.name}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            isInvalid={Boolean(nameTouched && nameError)}
                          />
                          <Form.Control.Feedback type="invalid" className={styles.errorText}>
                            {nameError}
                          </Form.Control.Feedback>
                        </Form.Group>
                      </div>

                      <p className={styles.resourceHint}>
                        `type` representa el servicio AWS y `name` define el identificador lógico
                        del recurso en la solicitud.
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </FieldArray>

        <div className={styles.formFooter}>
          <Button className={styles.primaryButton} type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Enviando solicitud...' : 'Generar solicitud Terraform'}
          </Button>
          <p className={styles.helperText}>
            Solo necesitas actualizar `VITE_API_BASE_URL` en el `.env` para apuntar al backend
            real.
          </p>
        </div>

        {submitError ? <div className={styles.arrayError}>{submitError}</div> : null}

        {responsePreview ? (
          <div className={styles.responseCard}>
            <div className={styles.previewHeader}>
              <span className={styles.previewDot} />
              <p>Response preview</p>
            </div>
            <pre className={styles.codeBlock}>{responsePreview}</pre>
          </div>
        ) : null}
      </Form>
    </div>
  );
}

export default PayloadForm;
