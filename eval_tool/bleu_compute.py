from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

def calculate_bleu_scores(reference_strs, candidate_str):
    if isinstance(reference_strs, str):
        references = [reference_strs.split()]
    elif isinstance(reference_strs, list):
        references = [ref.split() for ref in reference_strs]
    candidate = candidate_str.split()
    bleu_score = sentence_bleu(references, candidate)
    bleu_1gram = sentence_bleu(references, candidate, weights=(1, 0, 0, 0))
    bleu_2gram = sentence_bleu(references, candidate, weights=(0, 1, 0, 0))

    return bleu_score, bleu_1gram, bleu_2gram

# 示例用法
# references = [
#     'this is a great test ?',
#     'there are tests'
# ]
# candidate = 'this is a nice tests'
#
# bleu, bleu_1gram, bleu_2gram = calculate_bleu_scores(references, candidate)
# print(f'BLEU score: {bleu:.4f}')
# print(f'1-gram BLEU score: {bleu_1gram:.4f}')
# print(f'2-gram BLEU score: {bleu_2gram:.4f}')
