import os
import json
import time
from tqdm import tqdm
from openai import OpenAI
from argparse import ArgumentParser

def parser_args():
    parser = ArgumentParser()
    parser.add_argument("--task",type=str,required=True)
    parser.add_argument("--train_dir",type=str,required=True)
    parser.add_argument("--test_dir",type=str,required=True)
    parser.add_argument("--shot_dir",type=str,required=True)
    parser.add_argument("--shot_num",type=int,required=True)
    parser.add_argument("--prompt_dir",type=str,required=True)
    parser.add_argument("--model",type=str,required=True)
    parser.add_argument("--moda",type=str,default='greedy')
    parser.add_argument("--output_dir",type=str,required=True)
    return parser.parse_args()

def get_completion(model, prompt, id = ""):
    client = OpenAI(
        api_key = "sk-sR8RiK6YYrtk8Rss1b29047069804d108211285c7a25356c", # 填写上api-key
        base_url="https://api.yesapikey.com/v1"
    )
    client.base_url="https://api.yesapikey.com/v1"
    flag = False
    while not flag:
        try:
            response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model,
                    temperature=0
            )
            flag=True
        except Exception as e:
            print(e)
            time.sleep(0.5)
    return response.choices[0].message.content


def get_ner_shot_prompt(i, train_data, shot_data, shot_num):
    prompt = "\n## Examples\n"
    few_shots = shot_data[i]["id"][:shot_num]
    for shot_id in few_shots:
        shot_input = train_data[shot_id]["text"]
        shot_answer = train_data[shot_id]["entity"]
        prompt += f"Input:{shot_input}\n"
        prompt += f"Answer:{shot_answer}\n"
    return prompt


def get_ner_prompt(args):
    with open(args.train_dir,'r',encoding='utf-8') as train_file:
        train_data = json.load(train_file)
    with open(args.test_dir,'r',encoding='utf-8') as test_file:
        test_data = json.load(test_file)
    with open(args.shot_dir,'r',encoding='utf-8') as shot_file:
        shot_data = json.load(shot_file)
    with open(args.prompt_dir,'r',encoding='utf-8') as prompt_file:
        prompt_templeate = prompt_file.read()
    prompt_list = []
    if args.shot_num==0:
        for test_item in test_data:
            input_req = test_item["text"]
            prompt = prompt_templeate.format(examples="",input_req=input_req)
            prompt_list.append(prompt)
        return prompt_list
    else:
        shot_num = args.shot_num
        for i,test_item in enumerate(test_data):
            input_req = test_item["text"]
            shot_prompt = get_ner_shot_prompt(i,train_data,shot_data,shot_num)
            prompt = prompt_templeate.format(examples=shot_prompt,input_req=input_req)
            prompt_list.append(prompt)
        return prompt_list

def get_rel_shot_prompt(i,train_data,shot_data,shot_num):
    prompt = "\n## Examples\n"
    few_shots = shot_data[i]["id"][:shot_num]
    for shot_id in few_shots:
        shot_input = train_data[shot_id]["text"]
        shot_entity = train_data[shot_id]["entity"]
        shot_answer = train_data[shot_id]["relation"]
        prompt += f"Input:{shot_input}\n"
        prompt += f"Entities:{shot_entity}\n"
        prompt += f"Answer:{shot_answer}\n"
    return prompt

def get_rel_prompt(args):
    with open(args.train_dir,'r',encoding='utf-8') as train_file:
        train_data = json.load(train_file)
    with open(args.test_dir,'r',encoding='utf-8') as test_file:
        test_data = json.load(test_file)
    with open(args.shot_dir,'r',encoding='utf-8') as shot_file:
        shot_data = json.load(shot_file)
    with open(args.prompt_dir,'r',encoding='utf-8') as prompt_file:
        prompt_templeate = prompt_file.read()
    prompt_list = []
    if args.shot_num==0:
        for test_item in test_data:
            input_req = test_item["text"]
            entities = test_item["entity"]
            prompt = prompt_templeate.format(examples="",input_req=input_req,entity_list=entities)
            prompt_list.append(prompt)
        return prompt_list
    else:
        shot_num = args.shot_num
        for i,test_item in enumerate(test_data):
            input_req = test_item["text"]
            entities = test_item["entity"]
            shot_prompt = get_rel_shot_prompt(i,train_data,shot_data,shot_num)
            prompt = prompt_templeate.format(examples=shot_prompt,input_req=input_req,entity_list=entities)
            # print(prompt)
            prompt_list.append(prompt)
        return prompt_list

def gpt_inference(args):
    if args.task=="entity":
        prompt_list = get_ner_prompt(args)
    elif args.task=="relation":
        prompt_list = get_rel_prompt(args)
    predict_list = []
    id = -1
    # prompt_list = prompt_list[:2]
    for prompt in tqdm(prompt_list, desc='generate answer'):
        id +=1
        predict = get_completion(args,prompt,id)
        predict_dict = {
            "predict":predict
        }
        predict_list.append(predict_dict)
        time.sleep(0.5)
    output_dir = os.path.join(args.output_dir,f"{args.task}/{args.model}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.join(output_dir,"fold_0")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir,f"{args.shot_num}.json")
    print(output_path)
    json_data = json.dumps(predict_list,ensure_ascii=False,indent=2)
    with open(output_path,'w',encoding='utf-8') as output_file:
        output_file.write(json_data)

def generate_instruction():
    prompt_header = "You are an expert on Domain Specific Language Generation, and you need to write formal requirements with a domain-specific language for the given natural language requirements. First, you should write a grammar that contains all the necessary BNF rules. Then, you should write formal requirements that conform to your predicted rules."
    prompt_header += "\n"
    prompt_header += "\n[BEGIN RULES]\n"
    with open('../cy_source/rules.txt', 'r', encoding='utf-8') as file:
        prompt_header += file.read()
    prompt_header += "[END RULES]\n"
    return prompt_header

def copy_into_roll(x, mid, y, hint_x = "query:", hint_mid = "BNF grammar rules:", hint_y = "program based on the BNF grammar rules:\n"):
    return rf"{hint_x} {x}" + "\n" + rf"{hint_mid} {mid}" + "\n" + rf"{hint_y} {y}" + "\n"

def getx_y(file_name, num=10):
    # 构建完整的文件路径
    records = ""
    full_path = "dataset" + '\\' + file_name + ".json"
    try:
        with open(full_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # print(type(data[file_name]))
            for item in data[file_name][:num]:
                # print(type(item))
                x = item["text"]
                mid = "需要填充"
                y = item["label"]
                # print(x,mid,y)
                one_record = ""
                one_record += "============================================================START============================================================"
                one_record += "\n"
                one_record += copy_into_roll(x, mid, y)
                one_record += "\n"
                one_record += "=============================================================END============================================================="
                records += one_record + "\n"
                # print(one_record)
                # break

    except FileNotFoundError:
        print(f"文件 {full_path} 未找到。")
    except json.JSONDecodeError:
        print(f"文件 {full_path} 不是有效的 JSON 格式。")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
    return records

def construct():
    file_names = ["examples", "training", "validation"]
    prompt = generate_instruction() + getx_y(file_names[0], 4)
    with open("dataset" + '\\' + file_names[1] + ".json", 'r', encoding='utf-8') as file:
        train_data = json.load(file)
    # print(type(train_data["train"][0]))
    # print(str(train_data["train"]))
    # print(train_data["train"][0]["text"])
    prompt += "query:" + train_data["train"][1]["text"] + "\n"
    # prompt += "待填充\n"
    prompt += "program based on the BNF grammar rules:\n"
    print(prompt)
    with open('ask_gpt.txt', 'w', encoding='utf-8') as file:
        file.write(prompt)
    return prompt
def main():
    # args = parser_args()
    one_prompt = construct()
    # print(one_prompt)
    print("✅response from gpt-4:\n" + get_completion("gpt-4",one_prompt))
    # print(args.shot_num)
    # print(args.model)
    # gpt_inference(args)

if __name__=="__main__":
    main()

