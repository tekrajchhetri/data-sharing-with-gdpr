# 📘 Data Sharing with GDPR  
**A Guide to Building Secure, Ethical, and Legally Compliant Systems**

Welcome to the official GitHub repository for the book *Data Sharing with GDPR*. This repository includes code snippets, chapter-wise examples, and supplementary materials discussed throughout the book.

---

## 🧑‍💻 Authors

- **Tek Raj Chhetri**  
  Postdoctoral Associate, Massachusetts Institute of Technology (MIT), USA
  Founder, Center for Artificial Intelligence Research Nepal (CAIR-Nepal), Nepal

- **Semih Yumusak**  
  Researcher, University of Southampton, United Kingdom  

- **Luis-Daniel Ibáñez**  
  Lecturer, University of Southampton, United Kingdom  

- **Anna Fensel**  
  Professor, Wageningen University & Research, Netherlands  

- **George Konstantinidis**  
  Professor, University of Southampton, United Kingdom  

---

## 📖 Book Overview

*Data Sharing with GDPR* offers practical guidance for designing systems that handle personal data responsibly—balancing legal compliance, ethical responsibility, and technical interoperability.

### 📚 Chapter Summaries

<details>
<summary><strong>Chapter 1: Introduction</strong></summary>

- Introduces the concepts of privacy and data protection  
- Differentiates privacy from data protection  
- Discusses the importance of privacy in data sharing  
- Briefly introduces GDPR and its role in the data ecosystem  
</details>

<details>
<summary><strong>Chapter 2: Foundations of GDPR</strong></summary>

- Provides a foundational understanding of GDPR and its legal bases  
- Explains the scope and applicability of GDPR  
- Highlights its impact on data sharing and economy, including fines and violations  
</details>

<details>
<summary><strong>Chapter 3: Data Sharing and the Data Economy</strong></summary>

- Explores the concepts of data sharing, trust, quality, and interoperability  
- Introduces the data economy and its relation to sharing practices  
- Highlights applications in sectors like healthcare  
</details>

<details>
<summary><strong>Chapter 4: Ethical Considerations in Data Sharing</strong></summary>

- Focuses on ethical principles like data minimization and transparency  
- Discusses what to avoid to prevent unethical data practices  
</details>

<details>
<summary><strong>Chapter 5: Ensuring GDPR Compliance</strong></summary>

- Discusses compliance strategies and the principle of accountability  
- Provides technical and organizational measures to remain compliant  
</details>

<details>
<summary><strong>Chapter 6: Building Secure and Interoperable Data Sharing Systems</strong></summary>

- Covers data quality, interoperability, and trust from a system design perspective  
- Introduces decentralized systems (e.g., IPFS)  
- Shares best practices and common pitfalls  
</details>

<details>
<summary><strong>Chapter 7: Case Studies</strong></summary>

- Analyzes real-world applications and failure points  
- Includes examples like hospital patient monitoring systems  
</details>

<details>
<summary><strong>Chapter 8: Trends and Considerations</strong></summary>

- Discusses global data protection trends and regional regulations  
- Examples include China's PIPL and the European AI Act  
</details>

<details>
<summary><strong>Chapter 9: Conclusion</strong></summary>

- Recaps key takeaways from the book  
</details>

---

## 📂 Repository Structure

```
data-sharing-with-gdpr/
├── ch2/                      Chapter 2: Foundations of GDPR
│   └── data_analysis/        GDPR fines analysis notebook, data, and figures
├── ch6/                      Chapter 6: Secure and interoperable systems
│   ├── hybrid_encryption/    Hybrid encryption implementation and examples
│   └── interoperability/     Technical interoperability notebook
├── figures/                  Source diagrams (draw.io)
├── website/                  Companion website (datasharingbook.org)
└── .github/workflows/        Website build and deployment
```

Each chapter folder has its own `readme.md`.

---

## 🚀 Getting Started

```bash
git clone https://github.com/tekrajchhetri/data-sharing-with-gdpr.git
cd data-sharing-with-gdpr
python -m venv venv
source venv/bin/activate  # or use venv\Scripts\activate on Windows
pip install -r ch6/hybrid_encryption/requirements.txt
```

The notebooks in `ch2/data_analysis/` and `ch6/interoperability/` open in Jupyter.

---

## 🌐 Companion Website

The website source is in [`website/`](website/). Preview it locally:

```bash
python3 website/build.py
python3 -m http.server 4186 --directory website/_site
```

Pushing changes under `website/` to `master` deploys the site to GitHub Pages automatically. See [`website/README.md`](website/README.md) for how to add chapters and resources.
