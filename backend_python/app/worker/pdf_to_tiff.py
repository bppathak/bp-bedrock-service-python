import json
from pathlib import Path
from typing import Any

from app.models.submission import ConversionStatus, ConvertedFileUpdate
from app.services import submission_service
from app.services.aws_service import LOCAL_FILE_DIR

try:
    import pypdfium2 as pdfium
except ImportError:  # pragma: no cover - optional runtime dependency
    pdfium = None


def convert_pdf_to_tiff(source_path: Path, target_path: Path) -> None:
    if pdfium is None:
        raise RuntimeError("pypdfium2 is not installed; cannot convert PDF to TIFF")

    pdf = pdfium.PdfDocument(str(source_path))
    page = pdf[0]
    bitmap = page.render(scale=2).to_pil()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    bitmap.save(target_path, format="TIFF")


def process_message(message: dict[str, Any]) -> dict[str, str]:
    submission_id = message["submission_id"]
    file_id = message["file_id"]
    source_key = message["source_s3_key"]
    target_key = message["target_s3_key"]
    source_path = LOCAL_FILE_DIR / source_key
    target_path = LOCAL_FILE_DIR / target_key

    try:
        convert_pdf_to_tiff(source_path, target_path)
        submission_service.update_file_conversion(
            submission_id,
            file_id,
            ConvertedFileUpdate(
                converted_file_id=file_id,
                converted_s3_key=target_key,
                conversion_status=ConversionStatus.CONVERTED,
            ),
        )
        return {"status": "CONVERTED", "file_id": file_id}
    except Exception:
        submission_service.update_file_conversion(
            submission_id,
            file_id,
            ConvertedFileUpdate(
                converted_file_id=file_id,
                converted_s3_key=target_key,
                conversion_status=ConversionStatus.FAILED,
            ),
        )
        raise


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    results = []
    for record in event.get("Records", []):
        results.append(process_message(json.loads(record["body"])))
    return {"results": results}
