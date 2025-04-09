# Automated-DSL-Code-Generation

## 🐍 Environment Requirements

- **Python version**: 3.12.2 (recommended)
- **pip**: ≥ 23.0
- OS support: Windows / macOS / Linux

---

## 🔧 Environment Setup

You can install all required dependencies in one of the following ways:

### ✅ Option 1: Using the install script

```bash
python install_env.py
```
### ✅ Option 2: Using requirements.txt
Alternatively, you can install the dependencies using the requirements.txt file:

```bash
pip install -r requirements.txt
```
## 📂 Project Structure

This project contains the following directory and file structure:

```
env_setup.py
new_gpt_inference.py
README.md
requirement.txt

├─dataset
│  ├─data_process.py
│  ├─examples.json
│  ├─test.json
│  └─training.json

├─eval_tool
│  ├─bleu_compute.py
│  ├─codebleu_compute.py
│  └─rough_compute.py

├─reference
│  ├─compute_rough.py
│  ├─cy_old_gpt_inference.py
│  └─gpt_inference（base）.py

├─reminder
│  └─command.txt

├─results
│  └─relation
│      └─gpt-4
│          └─fold_0
│              └─3.json

├─script
│  └─run_inference.sh

└─source
   ├─pre_prompt.txt
   ├─prompt.txt
   └─rules.txt
```

## 💡 Directory Overview

- **env_setup.py**: Script to set up the environment.
- **new_gpt_inference.py**: GPT inference implementation.
- **README.md**: Project documentation.
- **requirement.txt**: Required Python dependencies.

### dataset
Contains the dataset and processing scripts:
- **data_process.py**: Data preprocessing script.
- **examples.json**: Example data for inference.
- **test.json**: Testing data for the model.
- **training.json**: Training data for the model.

### eval_tool
Evaluation tools for model output:
- **bleu_compute.py**: Computes BLEU score for evaluation.
- **codebleu_compute.py**: Computes CodeBLEU score for code generation tasks.
- **rough_compute.py**: Computes rough similarity score.

### reference
Scripts and files related to reference implementation:
- **compute_rough.py**: Computes rough similarity based on reference.
- **cy_old_gpt_inference.py**: Previous GPT inference script.
- **gpt_inference（base）.py**: Base GPT inference implementation.

### reminder
Contains command instructions:
- **command.txt**: File with command instructions or reminders.

### results
Stores results from evaluations:
- **relation**: Folder containing the relation results.
  - **gpt-4**: Folder for GPT-4 related results.
    - **fold_0**: Specific results from fold 0.
      - **3.json**: Result file for fold 0.

### script
- **run_inference.sh**: Shell script to run inference tasks.

### source
Files containing prompts and rules:
- **pre_prompt.txt**: Predefined prompts for the model.
- **prompt.txt**: Main prompt for model inference.
- **rules.txt**: Rules for prompt handling.

---

## 📦 LAST UPDATE
```
**Fio250403**

---
