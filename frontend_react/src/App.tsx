import { useState } from "react";
import "./App.css";
import { api, type Submission } from "./api";
import Contact from "./pages/Contact";
import Payment from "./pages/Payment";
import Review from "./pages/Review";
import UploadPDF from "./pages/UploadPDF";
import FormType from "./pages/FormType";

export type WizardData = {
  displayName: string;
  email: string;
  phone: string;
  paymentReference: string;
  formType: string;
  file: File | null;
};

const initialData: WizardData = {
  displayName: "",
  email: "",
  phone: "",
  paymentReference: "",
  formType: "",
  file: null,
};

export default function App() {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<WizardData>(initialData);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(action: () => Promise<Submission>, nextStep?: number) {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await action();
      setSubmission(updated);
      if (nextStep) {
        setStep(nextStep);
      }
      return true;
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong");
      return false;
    } finally {
      setLoading(false);
    }
  }

  const createOrUpdatePresenter = () =>
    run(
      () =>
        submission
          ? api.updatePresenter(submission.id, data.displayName, data.email, data.phone)
          : api.createSubmission(data.displayName, data.email, data.phone),
      2,
    );

  const savePayment = () =>
    run(() => api.updatePayment(requireSubmissionId(submission), data.paymentReference), 3);

  const saveFormType = () => run(() => api.updateFormType(requireSubmissionId(submission), data.formType), 4);

  const uploadFile = () => {
    const selectedFile = data.file;
    if (!selectedFile) {
      setError("Choose a PDF before continuing.");
      return;
    }
    void run(() => api.uploadFile(requireSubmissionId(submission), selectedFile), 5);
  };

  const submit = async () => {
    const succeeded = await run(() => api.submit(requireSubmissionId(submission)));
    if (succeeded) {
      setMessage("Submission sent. The PDF has been queued for TIFF conversion.");
    }
  };

  return (
    <main className="app-shell">
      <header className="app-header">
        <p className="eyebrow">AWS Bedrock submission MVP</p>
        <h1>Submission journey</h1>
        <p>Complete each step. Your progress is saved to the backend as you go.</p>
      </header>

      <nav className="stepper" aria-label="Submission progress">
        {["Contact", "Payment", "Form", "PDF", "Review"].map((label, index) => (
          <span key={label} className={step === index + 1 ? "active" : ""}>
            {index + 1}. {label}
          </span>
        ))}
      </nav>

      {error && <p className="alert error">{error}</p>}
      {message && <p className="alert success">{message}</p>}

      {step === 1 && (
        <Contact data={data} setData={setData} loading={loading} next={createOrUpdatePresenter} />
      )}
      {step === 2 && (
        <Payment
          data={data}
          setData={setData}
          loading={loading}
          previous={() => setStep(1)}
          next={savePayment}
        />
      )}
      {step === 3 && (
        <FormType
          data={data}
          setData={setData}
          loading={loading}
          previous={() => setStep(2)}
          next={saveFormType}
        />
      )}
      {step === 4 && (
        <UploadPDF
          data={data}
          setData={setData}
          loading={loading}
          previous={() => setStep(3)}
          next={uploadFile}
        />
      )}
      {step === 5 && (
        <Review
          data={data}
          submission={submission}
          loading={loading}
          previous={() => setStep(4)}
          submit={submit}
        />
      )}
    </main>
  );
}

function requireSubmissionId(submission: Submission | null) {
  if (!submission) {
    throw new Error("Start the submission before continuing.");
  }
  return submission.id;
}
