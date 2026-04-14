import styles from '../App.module.scss';
import PayloadPreview from './PayloadPreview';
import type { IaCFormData, ResourceTypeOption } from '../types/iac';

type HeroPanelProps = {
  payloadPreview: string;
  primaryResourceType?: string;
  resourceCount: number;
  region: string;
  resourceTypeOptions: ResourceTypeOption[];
};

function HeroPanel({
  payloadPreview,
  primaryResourceType,
  region,
  resourceCount,
  resourceTypeOptions
}: HeroPanelProps) {
  const primaryResourceLabel =
    resourceTypeOptions.find((option) => option.value === primaryResourceType)?.label ?? 'Sin definir';

  return (
    <div className={styles.storyPanel}>
      <p className={styles.eyebrow}>Generacion multiagente</p>
      <h1 className={styles.title}>Payloads IaC AWS.</h1>
      <p className={styles.subtitle}>
        La interfaz ahora está pensada para escalar mejor: capturas contexto global del proyecto y
        después defines una lista de recursos AWS con su tipo e identificador lógico.
      </p>

      <div className={styles.insightCard}>
        <span className={styles.insightLabel}>Recurso principal</span>
        <strong>{primaryResourceLabel}</strong>
        <p>
          `type` describe el servicio AWS y `name` representa el nombre del recurso solicitado
          dentro del payload.
        </p>
      </div>

      <div className={styles.featureList}>
        <article className={styles.featureItem}>
          <span className={styles.featureKicker}>01</span>
          <div>
            <h2>Múltiples recursos</h2>
            <p>
              Puedes componer una solicitud más realista agregando varios recursos dentro del
              arreglo `resources`.
            </p>
          </div>
        </article>

        <article className={styles.featureItem}>
          <span className={styles.featureKicker}>02</span>
          <div>
            <h2>Validación clara</h2>
            <p>
              Formik y Yup ayudan a mantener el JSON consistente antes de enviarlo al backend
              generador de Terraform.
            </p>
          </div>
        </article>
      </div>

      <div className={styles.statsRow}>
        <div className={styles.statCard}>
          <strong>{resourceCount}</strong>
          <span>recursos configurados</span>
        </div>
        <div className={styles.statCard}>
          <strong>{region}</strong>
          <span>región objetivo</span>
        </div>
      </div>

      <PayloadPreview payloadPreview={payloadPreview} />
    </div>
  );
}

export default HeroPanel;
