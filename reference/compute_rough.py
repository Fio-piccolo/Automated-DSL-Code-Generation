import os
import json
from argparse import ArgumentParser
from rouge_score import rouge_scorer

def get_parser_args():
    parser = ArgumentParser()
    parser.add_argument("--input_dir",type=str,default="output/ml/hmm")
    parser.add_argument("--split",type=str,default=1) # 第几个划分
    parser.add_argument("--output_dir",type=str,default="metric/ml/hmm")
    return parser.parse_args()

def compute_standard_rough(generated_answer,reference_answer):
    generated_answer = ','.join(generated_answer)
    reference_answer = ','.join(reference_answer)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    # 注意：rouge_scorer 的顺序是 (reference, generated)
    rouge_scores = scorer.score(reference_answer, generated_answer)

    rouge1_f1 = rouge_scores["rouge1"].fmeasure
    rouge2_f1 = rouge_scores["rouge2"].fmeasure
    rougeL_f1 = rouge_scores["rougeL"].fmeasure
    return rouge1_f1,rouge2_f1,rougeL_f1

def compute_rough(predict_path,human_path):
    rough_result = {
        "Software System":[0,0,0],
        "Physical Device":[0,0,0],
        "Environment Object":[0,0,0],
        "External System":[0,0,0],
        "System Requirements":[0,0,0],
        "Shared Phenomena":[0,0,0]
    }
    predict_model = {
        "Software System":None,
        "Physical Device":None,
        "Environment Object":None,
        "External System":None,
        "System Requirements":None,
        "Shared Phenomena":None
    }
    ground_model = {
        "Software System":None,
        "Physical Device":None,
        "Environment Object":None,
        "External System":None,
        "System Requirements":None,
        "Shared Phenomena":None
    }
    with open(predict_path,'r',encoding='utf-8') as file:
        predict_data = json.load(file)
    with open(human_path,'r',encoding='utf-8') as file:
        human_data = json.load(file)
    for key in rough_result:
        flat_predict = []
        flat_ground = []
        for i,predict in enumerate(predict_data):
            if key not in predict['entity']:
                continue
            predict = predict['entity'][key]
            ground = human_data[i]['entity'][key]
            for item in predict:
                if item not in flat_predict:
                    flat_predict.append(item)
            for item in ground:
                if item not in flat_ground:
                    flat_ground.append(item)
        # 将flat_predict中的字符串进行排序
        flat_predict = sorted(flat_predict)
        flat_ground = sorted(flat_ground)
        predict_model[key] = flat_predict
        ground_model[key] = flat_ground
        rouge1_f1,rouge2_f1,rougeL_f1 = compute_standard_rough(flat_predict,flat_ground)
        rough_result[key] = [rouge1_f1,rouge2_f1,rougeL_f1]
    return rough_result

if __name__=="__main__":
    args = get_parser_args()
    predict_path = os.path.join(args.input_dir,f"{args.split}.json")
    ground_path = os.path.join(f"data/split_v1/split_{args.split}","test.json")
    rough_result = compute_rough(predict_path,ground_path)
    print(rough_result)
    rough_result_dir = f"{args.output_dir}/rough"
    if not os.path.exists(rough_result_dir):
        os.makedirs(rough_result_dir)
    output_file = f"{rough_result_dir}/{args.split}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rough_result, f, ensure_ascii=False, indent=4)