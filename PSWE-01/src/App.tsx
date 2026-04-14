import { Container, Row, Col, Card } from 'react-bootstrap';
import { Formik } from 'formik';
import styles from './App.module.scss';
import HeroPanel from './components/HeroPanel';
import PayloadForm from './components/PayloadForm';
import { useAgentRequest } from './hooks/useAgentRequest';
import { useIacFormConfig } from './hooks/useIacFormConfig';
import type { IaCFormData } from './types/iac';

function App() {
  const { createEmptyResource, initialValues, resourceTypeOptions, validationSchema } =
    useIacFormConfig();
  const { activityLogs, isSubmitting, responseData, submitError, submitPayload } = useAgentRequest();

  return (
    <Formik<IaCFormData>
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={async (values) => {
        await submitPayload(values);
      }}
    >
      {(formik) => {
        const { values } = formik;
        const primaryResource = values.resources[0];
        const payloadPreview = JSON.stringify(values, null, 2);

        return (
          <main className={styles.pageShell}>
            <Container className={styles.pageWrapper}>
              <Row className="justify-content-center">
                <Col xs={12} xxl={11}>
                  <Card className={styles.showcaseCard}>
                    <Card.Body className={styles.showcaseBody}>
                      <div className={styles.brandBadge}>AWS Terraform Request Builder</div>

                      <Row className="g-3 g-xl-4 align-items-stretch">
                        <Col lg={5} className={styles.storyColumn}>
                          <HeroPanel
                            payloadPreview={payloadPreview}
                            primaryResourceType={primaryResource?.type}
                            region={values.region}
                            resourceCount={values.resources.length}
                            resourceTypeOptions={resourceTypeOptions}
                          />
                        </Col>

                        <Col lg={7} className={styles.formColumn}>
                          <PayloadForm
                            createEmptyResource={createEmptyResource}
                            formik={formik}
                            isSubmitting={isSubmitting}
                            resourceTypeOptions={resourceTypeOptions}
                            responseData={responseData}
                            submitError={submitError}
                            activityLogs={activityLogs}
                          />
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Container>
          </main>
        );
      }}
    </Formik>
  );
}

export default App;
