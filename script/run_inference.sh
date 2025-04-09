python new_gpt_inference.py `
  --task relation `
  --train_dir dataset/training.json `
  --test_dir dataset/test.json `
  --shot_dir dataset/examples.json `
  --shot_num 3 `
  --prompt_dir cy_source/pre_prompt.txt `
  --model gpt-4 `
  --output_dir results/