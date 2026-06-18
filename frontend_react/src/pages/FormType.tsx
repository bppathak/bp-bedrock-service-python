import { useEffect, useState, type Dispatch, type SetStateAction } from "react";
import type { WizardData } from "../App";
import { api, type FormOption } from "../api";

type Props = {
  data: WizardData;
  setData: Dispatch<SetStateAction<WizardData>>;
  loading: boolean;
  previous: () => void;
  next: () => void;
};

export default function FormType({ data, setData, loading, previous, next }: Props) {
  const [forms, setForms] = useState<FormOption[]>([]);

  useEffect(() => {
    void api.getForms().then(setForms).catch(() => {
      setForms([
        { id: "passport", name: "Passport application" },
        { id: "visa", name: "Visa application" },
        { id: "benefits", name: "Benefits claim" },
      ]);
    });
  }, []);

  return (
    <section className="panel">
      <h2>Form type</h2>
      <label>
        Choose the submission form
        <select
          value={data.formType}
          onChange={(event) => setData((current) => ({ ...current, formType: event.target.value }))}
        >
          <option value="">Select a form</option>
          {forms.map((form) => (
            <option key={form.id} value={form.id}>
              {form.name}
            </option>
          ))}
        </select>
      </label>
      <div className="actions">
        <button className="secondary" disabled={loading} onClick={previous}>
          Back
        </button>
        <button disabled={loading || !data.formType} onClick={next}>
          {loading ? "Saving..." : "Save and continue"}
        </button>
      </div>
    </section>
  );
}
