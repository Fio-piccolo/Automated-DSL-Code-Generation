from codebleu import calc_codebleu

def codebleu_compute(References, Predictions, language = "python", Weights = (0.25, 0.25, 0.25, 0.25), Tokenizer=None):
    print(References)
    print(Predictions)
    result = calc_codebleu([References], [Predictions], lang=language, weights=Weights, tokenizer=Tokenizer)
    return result

prediction = "def add ( a , b ) :\n return a + b"
reference = "def sum ( first , second ) :\n return second + first"
print(codebleu_compute(reference, prediction))
# {
#   'codebleu': 0.5537, 
#   'ngram_match_score': 0.1041, 
#   'weighted_ngram_match_score': 0.1109, 
#   'syntax_match_score': 1.0, 
#   'dataflow_match_score': 1.0
# }