export type SubmissionStatus =
  | "OPEN"
  | "SUBMITTED"
  | "PROCESSING"
  | "SENT_TO_EXTERNALSYSTEM"
  | "ACCEPTED"
  | "REJECTED";

export type ConversionStatus = "WAITING" | "QUEUED" | "CONVERTED" | "FAILED";

export type FileDetails = {
  form_id: string;
  file_name: string;
  file_size: number;
  original_file_id?: string | null;
  original_s3_key?: string | null;
  converted_file_id?: string | null;
  converted_s3_key?: string | null;
  conversion_status: ConversionStatus;
};

export type Submission = {
  id: string;
  create_at: string;
  last_modified_at: string;
  status: SubmissionStatus;
  presenter: {
    email: string;
    display_name?: string | null;
    phone?: string | null;
  };
  payment_reference?: string | null;
  form: {
    form_type?: string | null;
    file_details: FileDetails[];
  };
};

export type FormOption = {
  id: string;
  name: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorBody.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  createSubmission(displayName: string, email: string, phone: string) {
    return request<Submission>("/bp-api/submission/new", {
      method: "POST",
      body: JSON.stringify({
        presenter: {
          display_name: displayName,
          email,
          phone: phone || null,
        },
      }),
    });
  },

  updatePresenter(submissionId: string, displayName: string, email: string, phone: string) {
    return request<Submission>(`/bp-api/submission/${submissionId}/presenter`, {
      method: "PUT",
      body: JSON.stringify({
        display_name: displayName,
        email,
        phone: phone || null,
      }),
    });
  },

  updatePayment(submissionId: string, paymentReference: string) {
    return request<Submission>(`/bp-api/submission/${submissionId}/payment`, {
      method: "PUT",
      body: JSON.stringify({ payment_reference: paymentReference }),
    });
  },

  updateFormType(submissionId: string, formType: string) {
    return request<Submission>(`/bp-api/submission/${submissionId}/formType`, {
      method: "PUT",
      body: JSON.stringify({ form_type: formType }),
    });
  },

  uploadFile(submissionId: string, file: File) {
    const data = new FormData();
    data.append("file", file, file.name);
    return request<Submission>(`/bp-api/submission/${submissionId}/files`, {
      method: "PUT",
      body: data,
    });
  },

  submit(submissionId: string) {
    return request<Submission>(`/bp-api/submission/${submissionId}`, {
      method: "PUT",
      body: JSON.stringify({ status: "SUBMITTED" }),
    });
  },

  async getForms() {
    const response = await request<{ forms: FormOption[] }>("/bp-api/forms");
    return response.forms;
  },
};
