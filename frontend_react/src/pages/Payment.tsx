import type { Dispatch, SetStateAction } from "react";
import type { WizardData } from "../App";

type Props = {
  data: WizardData;
  setData: Dispatch<SetStateAction<WizardData>>;
  loading: boolean;
  previous: () => void;
  next: () => void;
};

export default function Payment({ data, setData, loading, previous, next }: Props) {
  return (
    <section className="panel">
      <h2>Payment reference</h2>
      <label>
        Reference number
        <input
          value={data.paymentReference}
          onChange={(event) => setData((current) => ({ ...current, paymentReference: event.target.value }))}
          placeholder="PAY-12345"
        />
      </label>
      <div className="actions">
        <button className="secondary" disabled={loading} onClick={previous}>
          Back
        </button>
        <button disabled={loading || data.paymentReference.trim() === ""} onClick={next}>
          {loading ? "Saving..." : "Save and continue"}
        </button>
      </div>
    </section>
  );
}
