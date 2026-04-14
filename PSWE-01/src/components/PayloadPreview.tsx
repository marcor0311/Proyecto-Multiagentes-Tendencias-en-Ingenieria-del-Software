import styles from '../App.module.scss';

type PayloadPreviewProps = {
  payloadPreview: string;
};

function PayloadPreview({ payloadPreview }: PayloadPreviewProps) {
  return (
    <div className={styles.previewCard}>
      <div className={styles.previewHeader}>
        <span className={styles.previewDot} />
        <p>Payload preview</p>
      </div>
      <pre className={styles.codeBlock}>{payloadPreview}</pre>
    </div>
  );
}

export default PayloadPreview;
