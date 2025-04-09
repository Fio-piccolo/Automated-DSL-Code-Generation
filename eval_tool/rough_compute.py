from rouge_score import rouge_scorer


def compute_standard_rough(generated_answer, reference_answer):
    generated_answer = ','.join(generated_answer)
    reference_answer = ','.join(reference_answer)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    # 注意：rouge_scorer 的顺序是 (reference, generated)
    rouge_scores = scorer.score(reference_answer, generated_answer)

    rouge1_f1 = rouge_scores["rouge1"].fmeasure
    rouge2_f1 = rouge_scores["rouge2"].fmeasure
    rougeL_f1 = rouge_scores["rougeL"].fmeasure
    return rouge1_f1,rouge2_f1,rougeL_f1