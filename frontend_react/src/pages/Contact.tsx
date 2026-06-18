import type { Dispatch, SetStateAction } from "react";
import type { WizardData } from "../App";

type Props = {
  data: WizardData;
  setData: Dispatch<SetStateAction<WizardData>>;
  loading: boolean;
  next: () => void;
};

export default function Contact({ data, setData, loading, next }: Props) {
  const canContinue = data.displayName.trim() !== "" && data.email.includes("@");

  return (
    <section className="panel">
      <h2>Presenter details</h2>
      <label>
        Display name
        <input
          value={data.displayName}
          onChange={(event) => setData((current) => ({ ...current, displayName: event.target.value }))}
          placeholder="Jane Smith"
        />
      </label>
      <label>
        Email
        <input
          type="email"
          value={data.email}
          onChange={(event) => setData((current) => ({ ...current, email: event.target.value }))}
          placeholder="jane@example.com"
        />
      </label>
      <label>
        Phone
        <input
          value={data.phone}
          onChange={(event) => setData((current) => ({ ...current, phone: event.target.value }))}
          placeholder="Optional"
        />
      </label>
      <div className="actions">
        <button disabled={loading || !canContinue} onClick={next}>
          {loading ? "Saving..." : "Save and continue"}
        </button>
      </div>
    </section>
  );
}
