import type { Dispatch, SetStateAction } from "react";
import type { WizardData } from "../App";

type Props = {
  data: WizardData;
  setData: Dispatch<SetStateAction<WizardData>>;
  loading: boolean;
  previous: () => void;
  next: () => void;
};

export default function UploadPDF({ data, setData, loading, previous, next }: Props) {
  return (
    <section className="panel">
      <h2>Upload PDF</h2>
      <label>
        PDF file
        <input
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event) => {
            const file = event.target.files?.[0] ?? null;
            setData((current) => ({ ...current, file }));
          }}
        />
      </label>
      {data.file && <p className="hint">Selected: {data.file.name}</p>}
      <div className="actions">
        <button className="secondary" disabled={loading} onClick={previous}>
          Back
        </button>
        <button disabled={loading || !data.file} onClick={next}>
          {loading ? "Uploading..." : "Upload and continue"}
        </button>
      </div>
    </section>
  );
}
