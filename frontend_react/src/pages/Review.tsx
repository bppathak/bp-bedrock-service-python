import type { WizardData } from "../App";
import type { Submission } from "../api";

type Props = {
  data: WizardData;
  submission: Submission | null;
  loading: boolean;
  previous: () => void;
  submit: () => void;
};

export default function Review({ data, submission, loading, previous, submit }: Props) {
  return (
    <section className="panel">
      <h2>Review and submit</h2>
      <dl className="review-list">
        <div>
          <dt>Submission ID</dt>
          <dd>{submission?.id ?? "Not created yet"}</dd>
        </div>
        <div>
          <dt>Presenter</dt>
          <dd>{data.displayName}</dd>
        </div>
        <div>
          <dt>Email</dt>
          <dd>{data.email}</dd>
        </div>
        <div>
          <dt>Payment</dt>
          <dd>{data.paymentReference}</dd>
        </div>
        <div>
          <dt>Form</dt>
          <dd>{data.formType}</dd>
        </div>
        <div>
          <dt>PDF</dt>
          <dd>{submission?.form.file_details.at(-1)?.file_name ?? data.file?.name ?? "No file uploaded"}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{submission?.status ?? "OPEN"}</dd>
        </div>
      </dl>
      <div className="actions">
        <button className="secondary" disabled={loading} onClick={previous}>
          Back
        </button>
        <button disabled={loading || submission?.status === "SUBMITTED"} onClick={submit}>
          {loading ? "Submitting..." : "Submit"}
        </button>
      </div>
    </section>
  );
}
