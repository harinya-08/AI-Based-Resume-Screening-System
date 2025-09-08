import os
from datasets import load_dataset
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "train.csv")

print("CSV path resolved to:", csv_path)
print("File exists?", os.path.exists(csv_path))
dataset = load_dataset("csv", data_files={"train": csv_path})
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def preprocess(examples):
    inputs = ["generate recommendations: " + text for text in examples["ResumeText"]]
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding="max_length")
    labels = tokenizer(examples["Recommendation"], max_length=128, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]

    return model_inputs

tokenized = dataset.map(preprocess, batched=True, remove_columns=dataset["train"].column_names)

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

args = TrainingArguments(
    output_dir="./t5_resume_model",  
    per_device_train_batch_size=2,  
    num_train_epochs=3,            
    save_steps=500,                 
    logging_steps=100               
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    data_collator=data_collator,
)

trainer.train()
trainer.save_model("./t5_resume_model")
print(" Model saved at ./t5_resume_model")
