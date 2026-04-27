"""
Motor Insurance Intent Classifier
===================================
TF-IDF + LinearSVC pipeline (calibrated for probabilities) that classifies
a user query into one of four motor-insurance intents:

  calculation    — IDV / NCB / premium computation queries
  regulatory     — Mandatory law / IRDAI rules / compliance
  coverage       — Policy inclusions, exclusions, add-ons
  claim_process  — Filing, tracking, or settling a claim

Why LinearSVC over LogisticRegression?
  LinearSVC optimises a max-margin boundary (hinge loss), giving sharper
  decision surfaces between classes that share common vocabulary (motor,
  insurance, third-party).  LogisticRegression uses log-loss which softens
  boundaries and is more easily pulled towards the majority class.

Probability calibration:
  LinearSVC does not produce probabilities natively.  It is wrapped with
  CalibratedClassifierCV (cv=3, method='isotonic') so classify_intent()
  returns a calibrated confidence score in [0, 1].

Hyperparameter selection:
  GridSearchCV searches C ∈ {0.1, 0.5, 1.0, 2.0, 5.0, 10.0} by 5-fold
  stratified CV maximising macro-F1.

Dataset  : data/motor_insurance/intent_classifier/dataset.csv  (~130 rows, 4 classes, 5 sources)
Sources  : data/motor_insurance/intent_classifier/sources.txt  (full open-source attribution doc)
Model    : data/motor_insurance/intent_classifier/model.joblib (saved after first training run)

Public datasets used (see motor_intent_SOURCES.txt for full citations):
  - InsuranceQA       (Feng et al., IEEE ASRU 2015)
  - IRDAI Motor FAQs  (Government of India, public domain)
  - BANKING77         (Casanueva et al., ACL 2020, CC BY 4.0)
  - HWU64             (Liu et al., IWSDS 2019, CC BY 4.0)
  - InsureReg docs    (Internal sample documents)
"""

from __future__ import annotations

import csv
import warnings
from pathlib import Path
from typing import Any, Optional, Tuple

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
_HERE       = Path(__file__).resolve().parent
_ROOT       = _HERE.parent.parent.parent   # agents/department_agents/motor_insurance/ → project root
_CSV        = _ROOT / "data" / "motor_insurance" / "intent_classifier" / "dataset.csv"
_MODEL_PATH = _ROOT / "data" / "motor_insurance" / "intent_classifier" / "model.joblib"

# ─── Domain keyword indicator features ───────────────────────────────────────
# Each intent class has a curated list of high-precision trigger words.
# These are domain terms that almost never appear in the wrong class,
# so their presence is near-conclusive evidence for the label.
# At inference, DomainKeywordTransformer returns a sparse binary feature
# vector of length = total keywords, one 1.0 per matched word group.
#
# Explainability: this is "rule-based feature augmentation" — a standard
# NLP technique that injects expert knowledge into the feature space.

_KEYWORD_GROUPS: list[tuple[str, list[str]]] = [
    # calculation — IRDAI numeric concepts; almost never in regulatory/process text
    ("kw_idv",           ["idv", "insured declared value", "declared value"]),
    ("kw_ncb",           ["ncb", "no claim bonus", "no-claim bonus", "claim bonus"]),
    ("kw_depreciation",  ["depreciation", "depreciated", "depreciate"]),
    ("kw_premium_calc",  ["od premium", "own damage premium", "estimate premium",
                          "base premium", "premium amount", "compute premium",
                          "calculate premium", "lakh idv", "percent ncb"]),
    ("kw_gst",           ["gst", "18 percent", "goods and services tax"]),
    ("kw_ex_showroom",   ["ex-showroom", "ex showroom", "showroom price",
                          "manufacturer price"]),
    # regulatory — legal/statutory; almost never in coverage or claims text
    ("kw_law",           ["law", "legal", "statute", "statutory", "legislation",
                          "act 1988", "mva 1988", "motor vehicles act",
                          "section 146", "section146"]),
    ("kw_mandatory",     ["mandatory", "compulsory", "required by law",
                          "legal requirement", "must have", "required under"]),
    ("kw_penalty",       ["penalty", "fine", "offense", "offence", "punishable",
                          "prosecute", "impound", "imprisonment"]),
    ("kw_authority",     ["irdai", "regulator", "authority", "circular",
                          "tariff order", "gazette"]),
    # coverage — policy scope; almost never in claim filing text
    ("kw_covered",       ["covered", "covers", "cover flood", "cover damage",
                          "cover fire", "cover theft", "comprehensive",
                          "policy covers", "included in"]),
    ("kw_excluded",      ["excluded", "exclusion", "not covered", "exception",
                          "perils", "exemption"]),
    ("kw_addon",         ["add-on", "addon", "zero dep", "zero depreciation",
                          "engine protect", "key replace", "tyre protect",
                          "return to invoice", "bumper to bumper"]),
    ("kw_deductible",    ["deductible", "excess", "compulsory excess",
                          "voluntary excess", "voluntary deductible"]),
    # claim_process — process actions; almost never in coverage or calculation text
    ("kw_file_claim",    ["file a claim", "filing a claim", "raise a claim",
                          "claim intimation", "notify insurer", "report accident"]),
    ("kw_cashless",      ["cashless", "network garage", "approved garage",
                          "authorised workshop"]),
    ("kw_surveyor",      ["surveyor", "loss assessor", "survey report",
                          "inspection report", "repair estimate"]),
    ("kw_settlement",    ["settlement", "claim settlement", "settle claim",
                          "settled", "payout", "reimbursement", "reimburse"]),
    ("kw_rejected",      ["rejected claim", "claim rejected", "reject", "appeal",
                          "dispute claim", "grievance"]),
    ("kw_fir",           ["fir", "police report", "first information report",
                          "police complaint"]),
]

_KW_NAMES = [name for name, _ in _KEYWORD_GROUPS]


class DomainKeywordTransformer:
    """
    Rule-based feature augmentation transformer (sklearn-compatible).

    For each input text, produces a dense binary vector of length
    = len(_KEYWORD_GROUPS).  Position i is 1.0 if any keyword in group i
    appears in the lowercased text, else 0.0.

    Rationale: high-precision IRDAI terminology (IDV, NCB, Section 146,
    'file a claim') is class-discriminative but rare in a small corpus —
    TF-IDF may under-weight it.  Explicit binary indicators guarantee the
    signal is always present at full weight regardless of document frequency.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        import numpy as np
        result = np.zeros((len(X), len(_KEYWORD_GROUPS)), dtype=float)
        for i, text in enumerate(X):
            lower = text.lower()
            for j, (_, keywords) in enumerate(_KEYWORD_GROUPS):
                if any(kw in lower for kw in keywords):
                    result[i, j] = 1.0
        return result

    def get_feature_names_out(self):
        return _KW_NAMES


# ─── Lazy sklearn imports ─────────────────────────────────────────────────────
def _sklearn_imports():
    from sklearn.pipeline                import Pipeline, FeatureUnion
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm                     import LinearSVC
    from sklearn.calibration             import CalibratedClassifierCV
    from sklearn.model_selection         import (
        train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
    )
    from sklearn.metrics                 import (
        classification_report, accuracy_score, confusion_matrix
    )
    import joblib, numpy as np
    return (Pipeline, FeatureUnion, TfidfVectorizer,
            LinearSVC, CalibratedClassifierCV, train_test_split, StratifiedKFold,
            GridSearchCV, cross_val_score, classification_report,
            accuracy_score, confusion_matrix, joblib, np)


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_dataset(csv_path: Path = _CSV) -> Tuple[list, list]:
    """
    Read motor_intent_dataset.csv and return (questions, labels).
    Prints per-source and per-class breakdowns for provenance transparency.
    """
    questions, labels   = [], []
    source_counter: dict = {}
    class_counter:  dict = {}

    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            q      = row["question"].strip()
            intent = row["intent"].strip()
            src    = row["source"].strip()
            if q and intent:
                questions.append(q)
                labels.append(intent)
                source_counter[src]   = source_counter.get(src, 0)   + 1
                class_counter[intent] = class_counter.get(intent, 0) + 1

    print(f"[IntentClassifier] Loaded {len(questions)} samples from {csv_path.name}")
    print("  Sources:")
    for src, n in sorted(source_counter.items()):
        print(f"    {src:30s}: {n} rows")
    print("  Class distribution:")
    for cls, n in sorted(class_counter.items()):
        print(f"    {cls:16s}: {n} rows")

    return questions, labels


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train(
    csv_path:     Path  = _CSV,
    model_path:   Path  = _MODEL_PATH,
    test_size:    float = 0.20,
    random_state: int   = 42,
) -> dict:
    """
    Build and train TF-IDF + LinearSVC (calibrated) with GridSearchCV.

    Feature engineering:
      FeatureUnion:
        word TF-IDF  — unigrams + bigrams, sublinear TF
                       captures full phrase patterns (e.g. 'claim free years')
        char TF-IDF  — char_wb 3-5grams, sublinear TF
                       captures morphological stems: 'mandator', 'regulat',
                       'calculat', 'claim' that word TF-IDF misses on small data

    Classifier:
      LinearSVC (max-margin) wrapped in CalibratedClassifierCV for probabilities
      class_weight='balanced'  — equal loss contribution per class regardless of size
      GridSearchCV searches C in {0.1, 0.5, 1, 2, 5, 10} on macro-F1 (5-fold)

    Returns training summary dict; saves model to model_path via joblib.
    """
    (Pipeline, FeatureUnion, TfidfVectorizer,
     LinearSVC, CalibratedClassifierCV, train_test_split, StratifiedKFold,
     GridSearchCV, cross_val_score, classification_report,
     accuracy_score, confusion_matrix, joblib, np) = _sklearn_imports()

    X, y = load_dataset(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # ── Feature extraction ──────────────────────────────────────────────────
    word_tfidf = TfidfVectorizer(
        analyzer="word", ngram_range=(1, 2),
        sublinear_tf=True, min_df=1, max_features=6000,
    )
    char_tfidf = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(3, 5),
        sublinear_tf=True, min_df=1, max_features=4000,
    )
    # DomainKeywordTransformer: rule-based binary indicators for IRDAI terms
    # It is a proper sklearn-compatible class so joblib can pickle it directly
    domain_kw = DomainKeywordTransformer()
    # ── Grid-search C for LinearSVC ─────────────────────────────────────────
    base_pipeline = Pipeline([
        ("features", FeatureUnion([  # type: ignore[arg-type]
            ("word",   word_tfidf),
            ("char",   char_tfidf),
            ("domain", domain_kw),   # 20 binary features from IRDAI keyword groups
        ])),
        ("clf", CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", max_iter=2000),
            cv=3, method="isotonic",
        )),
    ])

    param_grid  = {"clf__estimator__C": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]}
    cv_inner    = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    grid_search = GridSearchCV(
        base_pipeline, param_grid,
        cv=cv_inner, scoring="f1_macro", n_jobs=-1, refit=True,
    )
    grid_search.fit(X_train, y_train)

    best_pipeline: Pipeline = grid_search.best_estimator_  # type: ignore[assignment]
    best_C        = grid_search.best_params_["clf__estimator__C"]

    # ── Hold-out evaluation ─────────────────────────────────────────────────
    y_pred  = best_pipeline.predict(X_test)
    acc     = accuracy_score(y_test, y_pred)
    report  = classification_report(y_test, y_pred, zero_division=0)
    classes = sorted(set(y))
    cm      = confusion_matrix(y_test, y_pred, labels=classes)

    # ── 5-fold outer CV on full dataset (unbiased estimate) ─────────────────
    import numpy as np
    X_arr     = np.array(X)
    cv_outer  = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_raw    = cross_val_score(best_pipeline, X_arr, y, cv=cv_outer, scoring="accuracy")
    cv_f1     = cross_val_score(best_pipeline, X_arr, y, cv=cv_outer, scoring="f1_macro")

    print(f"\n[IntentClassifier] === Training Complete ===")
    print(f"  Algorithm      : LinearSVC + CalibratedClassifierCV + DomainKeywordFeatures")
    print(f"  Features       : Word TF-IDF (1-2gram) + Char TF-IDF (3-5gram) + {len(_KEYWORD_GROUPS)} domain keyword indicators")
    print(f"  Best C (grid)  : {best_C}")
    print(f"  Dataset size   : {len(X)} samples")
    print(f"  Train / Test   : {len(X_train)} / {len(X_test)}")
    print(f"  Hold-out acc   : {acc:.4f}")
    print(f"  5-fold CV acc  : {cv_raw.mean():.4f}  (±{cv_raw.std():.4f})")
    print(f"  5-fold CV F1   : {cv_f1.mean():.4f}  (±{cv_f1.std():.4f})")
    print(f"  CV acc / fold  : {[round(float(s), 3) for s in cv_raw]}")
    print(f"\n{report}")

    print("  Confusion matrix (rows=actual, cols=predicted):")
    header = "".join(f"{c:>16}" for c in classes)
    print(f"  {'':16}{header}")
    for i, row_vals in enumerate(cm):
        print(f"  {classes[i]:16}" + "".join(f"{int(v):>16}" for v in row_vals))

    joblib.dump(best_pipeline, model_path)
    print(f"\n[IntentClassifier] Model saved → {model_path}")

    return {
        "accuracy":              float(acc),
        "best_C":               float(best_C),
        "cv_mean_accuracy":      float(cv_raw.mean()),
        "cv_std_accuracy":       float(cv_raw.std()),
        "cv_mean_f1_macro":      float(cv_f1.mean()),
        "cv_std_f1_macro":       float(cv_f1.std()),
        "cv_scores":            [round(float(s), 4) for s in cv_raw],
        "classification_report": report,
        "label_classes":         classes,
        "model_path":            str(model_path),
    }


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

_pipeline_cache: Optional[Any] = None


def _load_pipeline(model_path: Path = _MODEL_PATH) -> Any:
    """Load cached pipeline; auto-train if model file not found."""
    global _pipeline_cache
    if _pipeline_cache is not None:
        return _pipeline_cache

    try:
        import joblib
        _pipeline_cache = joblib.load(model_path)
    except (FileNotFoundError, Exception):
        # First run — train and save automatically
        train(model_path=model_path)
        import joblib
        _pipeline_cache = joblib.load(model_path)

    return _pipeline_cache


def classify_intent(query: str, model_path: Path = _MODEL_PATH) -> Tuple[str, float]:
    """
    Classify a motor insurance query into one of four intents.

    Returns:
        (label, confidence)  — e.g. ("calculation", 0.91)

    Labels:
        "calculation"   — IDV / NCB / premium computation
        "regulatory"    — IRDAI rules, mandatory coverage, legal compliance
        "coverage"      — policy inclusions, exclusions, add-ons
        "claim_process" — claim filing, settlement, documentation
    """
    import numpy as np
    pipeline = _load_pipeline(model_path)
    proba = pipeline.predict_proba([query])[0]
    idx = int(np.argmax(proba))
    label = pipeline.classes_[idx]
    confidence = float(proba[idx])
    return label, confidence


# ---------------------------------------------------------------------------
# CLI entry-point  (python agents/motor_intent_classifier.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--train" in sys.argv or not _MODEL_PATH.exists():
        results = train()
        print(f"\n{'='*55}")
        print(f"  Label classes  : {results['label_classes']}")
        print(f"  Best C         : {results['best_C']}")
        print(f"  5-fold CV acc  : {results['cv_mean_accuracy']:.4f}  "
              f"(±{results['cv_std_accuracy']:.4f})")
        print(f"  5-fold CV F1   : {results['cv_mean_f1_macro']:.4f}  "
              f"(±{results['cv_std_f1_macro']:.4f})")
        print(f"{'='*55}")

    else:
        # 12-query smoke test — 3 per class, including hard boundary cases
        test_queries = [
            # calculation — distinctive tokens: IDV, NCB, depreciation, percent, lakh, GST
            ("calculation",   "What is the IDV for a 3-year-old car worth 8 lakhs?"),
            ("calculation",   "How much NCB discount after 5 consecutive claim-free years?"),
            ("calculation",   "Compute OD premium for IDV 4 lakh with 35 percent NCB"),
            # regulatory — distinctive: law, mandatory, Section 146, penalty, statute, offense
            ("regulatory",    "Is third-party motor insurance mandatory under Indian law?"),
            ("regulatory",    "What is the legal penalty under MVA 1988 for no insurance?"),
            ("regulatory",    "Which statute makes motor insurance compulsory on public roads?"),
            # coverage — distinctive: comprehensive, add-on, zero dep, covered, excluded
            ("coverage",      "Does my comprehensive policy cover flood damage to the engine?"),
            ("coverage",      "Is zero depreciation add-on worth buying for a new car?"),
            ("coverage",      "What perils are excluded from a standard motor insurance policy?"),
            # claim_process — distinctive: file, cashless, surveyor, settlement, reimbursement
            ("claim_process", "How do I file a cashless claim after an accident?"),
            ("claim_process", "What documents does the surveyor need to assess my claim?"),
            ("claim_process", "Can I get reimbursement if I repair at a non-network garage?"),
        ]

        print("[IntentClassifier] Smoke-test (expected → predicted | confidence):")
        print("-" * 75)
        correct = 0
        for expected, q in test_queries:
            label, conf  = classify_intent(q)
            status       = "✓" if label == expected else "✗"
            correct     += (label == expected)
            flag         = "" if label == expected else f"  ← expected {expected}"
            print(f"  {status} [{label:16s} | {conf:.2f}]  {q[:62]}{flag}")
        print("-" * 75)
        print(f"  Score: {correct}/{len(test_queries)} correct  "
              f"({100*correct//len(test_queries)}%)")
