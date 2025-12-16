# Unthought-Of Physics: A Collaborative Learning Space

## About This Repository

This repository is dedicated to **real science only**. We focus on real mathematics and physics that are **APPROVED by academic rules as of today**. Remember that academic standards evolve day by day, and we strive to keep pace with these changes.

## Our Mission

We are independent mathematicians and physics learners. Our goal is to:
- Learn new physics concepts together
- Teach what we try to understand
- Advance our understanding of terrestrial physics
- Discover better ways to approach physics problems

**No fiction. No metaphors. No embellishing.**

This is a classroom where facts, evidence, and academic rigor are paramount.

## Philosophy

This is a unique learning environment where the distinction between student and teacher is blurred. Mr. Cline sits with the students, and we learn together. This collaborative approach emphasizes:
- Mutual respect for the learning process
- Academic honesty and rigor
- Evidence-based reasoning
- Peer-to-peer knowledge sharing

## What We Do

- Study and understand established physics principles
- Explore areas of physics that may need updates or better methodologies
- Share discoveries grounded in scientific method
- Apply approved mathematical frameworks to physics problems

## How This Repository Works (Living Experiment Ledger)

- **Raw data first**: CSV/JSON captures live in `raw_csv/` and `raw_radio/` as witness records.
- **Audit trails**: Capsule logs in `capsules/` document what happened, when, and with which thresholds.
- **Reproducibility scripts**: Python helpers (for example `reproduce_chi_ceiling_plot.py`) make plots and checks repeatable.
- **Open ledger**: Everything is versioned in Git so math and methods can be corrected when data demands it.

### Example: χ-ceiling data that forces a formula check
1. Install the plotting deps if needed: `pip install pandas matplotlib`.
2. Run `python reproduce_chi_ceiling_plot.py` (uses `raw_csv/cme_heartbeat_log_2025_12.csv`).
3. The plot highlights χ amplitudes hitting the 0.15 ceiling during storm phases—an explicit spot where the math needs scrutiny and updates.

## What We Don't Do

- Create or promote speculative fiction
- Use metaphors or embellishments in place of rigorous explanation
- Deviate from academically approved methods without proper justification
- Present unverified claims as fact

## Getting Started

To contribute to this learning space, please review our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

---

*"I want to learn. Not create fiction."* - Mr. Cline
