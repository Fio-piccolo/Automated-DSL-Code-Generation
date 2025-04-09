import os
import json
import openai
import time
from tqdm import tqdm
from openai import OpenAI
from argparse import ArgumentParser
from eval_tool.rough_compute import compute_standard_rough
from eval_tool.bleu_compute import calculate_bleu_scores
from eval_tool.codebleu_compute import codebleu_compute


# 导入必要的库
# os: 文件路径操作
# json: JSON数据处理
# time: 时间相关操作
# tqdm: 进度条显示
# openai: OpenAI API接口
# argparse: 命令行参数解析

def parser_args():
    # 定义命令行参数解析函数
    parser = ArgumentParser()
    parser.add_argument("--task", type=str, required=True)  # 任务类型（entity/relation）
    parser.add_argument("--train_dir", type=str, required=True)  # 训练数据路径
    parser.add_argument("--test_dir", type=str, required=True)  # 测试数据路径
    parser.add_argument("--shot_dir", type=str, required=True)  # 示例数据路径
    parser.add_argument("--shot_num", type=int, required=True)  # 示例数量
    parser.add_argument("--prompt_dir", type=str, required=True)  # 提示模板路径
    parser.add_argument("--model", type=str, required=True)  # 使用的模型名称
    parser.add_argument("--moda", type=str, default='greedy')  # 生成模式（默认贪心）
    parser.add_argument("--output_dir", type=str, required=True)  # 输出路径
    return parser.parse_args()

def read_data(args):
    with open(args.train_dir, 'r', encoding='utf-8') as train_file:
        train_data = json.load(train_file)  # 加载训练数据
    with open(args.test_dir, 'r', encoding='utf-8') as test_file:
        test_data = json.load(test_file)  # 加载测试数据
    with open(args.shot_dir, 'r', encoding='utf-8') as shot_file:
        shot_data = json.load(shot_file)  # 加载示例映射数据
    with open(args.prompt_dir, 'r', encoding='utf-8') as prompt_file:
        prompt_templeate = prompt_file.read()  # 加载提示模板
    return train_data["train"], test_data["test"], shot_data["examples"], prompt_templeate


def get_completion(args, prompt, idx):
    client = OpenAI(
        api_key="sk-sR8RiK6YYrtk8Rss1b29047069804d108211285c7a25356c",  # 填写上api-key
        base_url="https://api.yesapikey.com/v1"
    )
    client.base_url = "https://api.yesapikey.com/v1"
    max_retries = 10
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=args.model,
                temperature=0
            )
            return response.choices[0].message.content
        except openai.OpenAIError as e:
            print(f"ID: {idx} Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避策略
            else:
                raise


def get_ner_shot_prompt(i, train_data, shot_data, shot_num):
    # 构建NER任务的示例提示
    prompt = "\n## Examples\n"
    few_shots = shot_data[i]["id"][:shot_num]  # 获取当前测试样本对应的示例ID列表
    for shot_id in few_shots:
        shot_input = train_data[shot_id]["text"]  # 示例输入文本
        shot_answer = train_data[shot_id]["entity"]  # 示例实体标注结果
        prompt += f"Input:{shot_input}\n"
        prompt += f"Answer:{shot_answer}\n"
    return prompt


def get_ner_prompt(args):
    # 生成NER任务的完整提示列表
    train_data, test_data, shot_data, prompt_templeate = read_data(args)
    prompt_list = []
    if args.shot_num == 0:
        # 零样本情况
        for test_item in test_data:
            input_req = test_item["text"]
            prompt = prompt_templeate.format(examples="", input_req=input_req)
            prompt_list.append(prompt)
    else:
        # 少样本情况
        for i, test_item in enumerate(test_data):
            input_req = test_item["text"]
            shot_prompt = get_ner_shot_prompt(i, train_data, shot_data, args.shot_num)
            prompt = prompt_templeate.format(examples=shot_prompt, input_req=input_req)
            prompt_list.append(prompt)
    return prompt_list


def get_rel_shot_prompt(i, train_data, shot_data, shot_num):
    # 构建REL任务的示例提示
    prompt = "\n## Examples\n"
    # few_shots = shot_data[i][:shot_num]
    for shot_id in (0, shot_num):
        shot_input = train_data[shot_id]["text"]
        # shot_entity = train_data[shot_id]["entity"]  # 示例实体标注
        shot_entity = "待填充"

        shot_answer = train_data[shot_id]["label"]  # 示例关系标注
        prompt += f"x:\n{shot_input}\n"
        prompt += f"G(x):\n{shot_entity}\n"
        prompt += f"y:\n{shot_answer}\n"
        prompt += "\n"
    return prompt


def get_rel_prompt(args, testnum = 1):
    # 生成REL任务的完整提示列表
    train_data, test_data, shot_data, prompt_templeate = read_data(args)
    content_str = construct_pre_prompt()
    prompt_list = []
    train_lable = []
    if args.shot_num == 0:
        # 零样本情况
        for test_item in test_data:
            input_req = test_item["text"]
            entities = test_item["label"]
            prompt = prompt_templeate.format(examples="", input_req=input_req, entity_list=entities)
            prompt_list.append(prompt)
    else:
        # 少样本情况
        for i, test_item in enumerate(test_data):
            if i >= testnum:
                break
            input_req = test_item["text"]
            # entities = test_item["entities"]
            shot_prompt = get_rel_shot_prompt(i, train_data, shot_data, args.shot_num)
            # print(f"Prompt template: {prompt_templeate}")
            # print(f"Examples: {shot_prompt}")
            # print(f"Input request: {input_req}")
            # print(f"Entity list: ")
            prompt = prompt_templeate.format(pre_content = content_str, examples = shot_prompt, input_x = input_req + "\n", ans_y = "")
            print(f"✅Single prompt example:\n{prompt}")
            prompt_list.append(prompt)
            train_lable.append(test_item["label"])
    return prompt_list, train_lable


def gpt_inference(args):
    # 主推理函数
    prompt_list, dist_label= get_rel_prompt(args)
    predict_list = []
    idx = -1
    for prompt in tqdm(prompt_list, desc='generate answer'):
        idx += 1
        predict = get_completion(args, prompt, idx)  # 获取模型预测结果
        print(f"\n📝GPT predicted answer :\n{predict}")
        print(f"\n📄original_answer:\n{dist_label[idx]}")
        predict_dict = {"predict": predict}
        rouge1_f1,rouge2_f1,rougeL_f1 = compute_standard_rough(predict, dist_label[idx])
        bleu_score, bleu_1gram, bleu_2gram = calculate_bleu_scores(dist_label[idx], predict)
        codebleu_res = codebleu_compute(dist_label[idx], predict)
        # 打印 ROUGE 分数
        print("ROUGE 分数:")
        print(f"{'ROUGE-1 F1:':<8} {rouge1_f1:.4f}")
        print(f"{'ROUGE-2 F1:':<8} {rouge2_f1:.4f}")
        print(f"{'ROUGE-L F1:':<8} {rougeL_f1:.4f}")
        print()
        # 打印 BLEU 分数
        print("BLEU 分数:")
        print(f"{'BLEU:':<8} {bleu_score:.4f}")
        print(f"{'1-gram BLEU:':<8} {bleu_1gram:.4f}")
        print(f"{'2-gram BLEU:':<8} {bleu_2gram:.4f}")
        print()
        print("CODEBLEU 结果:")
        formatted_dict = json.dumps(codebleu_res, indent=4)
        print(f"{'CODEBLEU:':<8} {formatted_dict}")
        predict_list.append(predict_dict)
        time.sleep(0.5)  # 添加延迟防止API调用超限

    # 构建输出路径
    output_dir = os.path.join(args.output_dir, f"{args.task}/{args.model}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.join(output_dir, "fold_0")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f"{args.shot_num}.json")

    # 保存结果
    json_data = json.dumps(predict_list, ensure_ascii=False, indent=2)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json_data)

def construct_pre_prompt():
    prompt = "You are an expert on Domain Specific Language Generation, and you need to write formal requirements with a domain-specific language for the given natural language requirements. First, you should write a grammar that contains all the necessary BNF rules. Then, you should write formal requirements that conform to your predicted rules."
    with open("source/rules.txt", "r", encoding="utf-8") as file:
        file_content = file.read()
    return prompt + "\n" + "G(x):" + "\n" + file_content


if __name__ == "__main__":
    args = parser_args()  # 解析命令行参数
    # print(args.shot_num)
    # print(args.model)
    gpt_inference(args)  # 执行推理任务