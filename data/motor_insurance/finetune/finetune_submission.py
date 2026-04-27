"""
InsureReg — Concept 5: Fine-Tuning Submission Script
=====================================================

This script demonstrates the complete OpenAI fine-tuning workflow for creating
a specialised GPT-4o-mini model trained on IRDAI Motor Insurance regulatory
question-answer pairs.

Dataset:  data/finetune/motor_finetune.jsonl
Format:   OpenAI Chat Completion format (system / user / assistant messages)
Size:     20 high-quality IRDAI regulatory Q&A triplets

WHY FINE-TUNE?
--------------
While RAG provides document-grounded answers, fine-tuning improves the model's:
  1. Tone calibration  — the model learns the exact citation + disclaimer style
                         used across all 20 examples without explicit prompting.
  2. Domain vocabulary — motor-specific terms (IDV, NCB, OD, TP, IRDAI circulars,
                         Solatium Fund, etc.) are reinforced in the weights.
  3. Latency           — a fine-tuned model can produce regulatory answers with a
                         shorter system prompt since domain knowledge is internalised.
  4. Consistency       — reduces variance in output formatting and citation quality.

IMPORTANT — COST NOTICE:
--------------------------
Fine-tuning GPT-4o-mini costs approximately:
  • Training:  $0.003 per 1,000 training tokens  (~$0.10 for this 20-example dataset)
  • Inference: $0.0003 input / $0.0012 output per 1,000 tokens (≈3× cheaper than gpt-4o)
Running this script will initiate a real API call and WILL incur charges.
Do NOT run this script unless you intend to fine-tune.

INSTRUCTIONS:
  1. Set the OPENAI_API_KEY environment variable.
  2. Run: python data/finetune/finetune_submission.py --validate
     to validate the JSONL file format without submitting.
  3. Run: python data/finetune/finetune_submission.py --submit
     to upload and start the fine-tuning job.
  4. Run: python data/finetune/finetune_submission.py --status <job_id>
     to check the status of a submitted job.
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
DATASET_PATH  = Path(__file__).parent / "motor_finetune.jsonl"
BASE_MODEL    = "gpt-4o-mini-2024-07-18"   # smallest, cheapest fine-tunable model
SUFFIX        = "insure-reg-motor"          # model name suffix (visible in API response)
N_EPOCHS      = 3                           # IRDAI dataset is small; 3 epochs is standard


# ── Step 1: Validate JSONL format ─────────────────────────────────────────────

def validate_dataset(path: Path) -> bool:
    """
    Validate that every line in the JSONL file conforms to the OpenAI
    Chat Fine-Tuning format before uploading.
    """
    print(f"Validating dataset: {path}")
    errors  = []
    records = []

    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"  Line {i}: JSON parse error — {e}")
                continue

            if "messages" not in record:
                errors.append(f"  Line {i}: missing 'messages' key")
                continue

            msgs = record["messages"]
            roles = [m.get("role") for m in msgs]
            if roles[0] != "system":
                errors.append(f"  Line {i}: first message must have role='system'")
            if "user" not in roles:
                errors.append(f"  Line {i}: no 'user' message found")
            if "assistant" not in roles:
                errors.append(f"  Line {i}: no 'assistant' message found")

            records.append(record)

    if errors:
        print("❌  Validation FAILED:")
        for e in errors:
            print(e)
        return False

    # Token count estimate (very rough: 4 chars ≈ 1 token)
    total_chars = sum(
        sum(len(m.get("content", "")) for m in r["messages"])
        for r in records
    )
    approx_tokens = total_chars // 4
    cost_estimate = (approx_tokens / 1000) * 0.003 * N_EPOCHS

    print(f"✅  Validation PASSED")
    print(f"   Records     : {len(records)}")
    print(f"   Approx tokens: ~{approx_tokens:,}")
    print(f"   Training epochs: {N_EPOCHS}")
    print(f"   Estimated cost: ~${cost_estimate:.4f} USD")
    return True


# ── Step 2: Upload the file and start fine-tuning ─────────────────────────────

def submit_finetune_job(path: Path) -> str:
    """
    Upload the JSONL file to OpenAI and start a fine-tuning job.
    Returns the job ID.

    NOTE: This performs REAL API calls and will incur charges.
    """
    try:
        from openai import OpenAI
    except ImportError:
        print("openai package not installed. Run: pip install openai")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Step 2a: Upload the training file
    print("Uploading training file to OpenAI...")
    with open(path, "rb") as f:
        upload_response = client.files.create(file=f, purpose="fine-tune")
    file_id = upload_response.id
    print(f"  File uploaded: {file_id}")

    # Step 2b: Create the fine-tuning job
    print(f"Creating fine-tuning job (base model: {BASE_MODEL}, epochs: {N_EPOCHS})...")
    job_response = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=BASE_MODEL,
        suffix=SUFFIX,
        hyperparameters={"n_epochs": N_EPOCHS},
    )
    job_id = job_response.id
    print(f"  Fine-tuning job created: {job_id}")
    print(f"  Status: {job_response.status}")
    print(f"\nTo check status: python {__file__} --status {job_id}")
    print(
        "\nOnce the job completes, the fine-tuned model ID will appear in the "
        "API response (e.g., 'ft:gpt-4o-mini-2024-07-18:insure-reg-motor:xxxxxx').\n"
        "Update config/settings.py → LLM_MODEL to use the fine-tuned model for "
        "the Motor Insurance agent."
    )
    return job_id


# ── Step 3: Check job status ──────────────────────────────────────────────────

def check_job_status(job_id: str) -> None:
    """Retrieve and display the current status of a fine-tuning job."""
    try:
        from openai import OpenAI
    except ImportError:
        print("openai package not installed.")
        sys.exit(1)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    job    = client.fine_tuning.jobs.retrieve(job_id)

    print(f"Job ID        : {job.id}")
    print(f"Base model    : {job.model}")
    print(f"Status        : {job.status}")
    print(f"Created at    : {job.created_at}")
    if job.finished_at:
        print(f"Finished at   : {job.finished_at}")
    if job.fine_tuned_model:
        print(f"Fine-tuned model: {job.fine_tuned_model}")
        print(
            "\n✅  Fine-tuning complete!\n"
            f"   Update config/settings.py → LLM_MODEL = '{job.fine_tuned_model}'"
        )
    if job.error:
        print(f"Error         : {job.error}")


# ── How to use the fine-tuned model in InsureReg ──────────────────────────────

def show_usage_example() -> None:
    """Print a code snippet showing how to plug the fine-tuned model back in."""
    example = """
# config/settings.py — after fine-tuning completes:
LLM_MODEL = "ft:gpt-4o-mini-2024-07-18:insure-reg-motor:xxxxxxxx"

# The motor insurance agent will automatically use the fine-tuned weights
# because MotorInsuranceAgent reads LLM_MODEL from config/settings.py.
# All other settings (temperature, tools, LangGraph graph) remain unchanged.

# To test the fine-tuned model in isolation:
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:insure-reg-motor:xxxxxxxx",
    messages=[
        {"role": "system", "content": "You are an expert IRDAI motor insurance assistant."},
        {"role": "user",   "content": "What is the IDV of a 3-year-old car with ex-showroom price 8 lakh?"},
    ]
)
print(response.choices[0].message.content)
"""
    print(example)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="InsureReg Fine-Tuning Submission Script (Concept 5)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--validate", action="store_true",
        help="Validate the JSONL dataset without submitting (safe, no API calls).",
    )
    group.add_argument(
        "--submit", action="store_true",
        help="Upload dataset and start a fine-tuning job (WILL incur costs).",
    )
    group.add_argument(
        "--status", metavar="JOB_ID",
        help="Check the status of an existing fine-tuning job.",
    )
    group.add_argument(
        "--usage", action="store_true",
        help="Show how to integrate the fine-tuned model into InsureReg.",
    )
    args = parser.parse_args()

    if args.validate:
        success = validate_dataset(DATASET_PATH)
        sys.exit(0 if success else 1)

    elif args.submit:
        print("⚠️  WARNING: --submit will perform real API calls and incur charges.")
        confirm = input("Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)
        if not validate_dataset(DATASET_PATH):
            sys.exit(1)
        submit_finetune_job(DATASET_PATH)

    elif args.status:
        check_job_status(args.status)

    elif args.usage:
        show_usage_example()


if __name__ == "__main__":
    main()
