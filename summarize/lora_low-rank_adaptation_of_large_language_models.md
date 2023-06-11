# LoRA: Low-Rank Adaptation of Large Language Models
## 1 Introduction
LoRA is introduced as a way to adapt large, pre-trained language models to downstream applications by training some dense layers indirectly through optimizing rank decomposition matrices of the dense layers' change during adaptation, while keeping pre-trained weights frozen. This method allows sharing of pre-trained models and switching between tasks using small LoRA modules, reducing storage requirements and task-switching overhead. LoRA lowers the hardware entry barrier up to three times using adaptive optimizers and introduces no inference latency when deployed. Additionally, LoRA can be combined with many prior methods and is orthogonal to them.

Key takeaways:
* LoRA optimizes rank decomposition matrices of dense layers during adaptation, keeping pre-trained weights frozen.
* Sharing pre-trained models and switching between tasks is possible with LoRA using small modules.
* LoRA lowers hardware entry barriers and introduces no inference latency when deployed.

## 2 Problem Statement
The authors propose a more parameter-efficient approach compared to full fine-tuning for downstream tasks using pre-trained language models. Full fine-tuning method learns a different set of parameters for each task, making it difficult to store and deploy independent instances of fine-tuned models. To replace the task-specific parameter increment, a low-rank representation is introduced which is further encoded by a smaller-sized set of parameters to make it more compute- and memory-efficient. The proposed method works well for large pretrained models like GPT-3 with only 0.01% of trainable parameters using the full fine-tuning. 

Key takeaways:
* Full fine-tuning method learns a different set of parameters for each task
* Low-rank representation is proposed to replace task-specific parameter increment
* Proposed method is more parameter-efficient, compute- and memory-efficient, and works well for large pre-trained models

## 3 Aren’t Existing Solutions Good Enough?
The paper discusses the limitations of existing strategies for adapting language models, focusing on the inefficiencies of adding adapter layers and optimizing input layer activations. Adapter layers are often too slow for real-time production scenarios and can become extremely inefficient with high model sharding, while direct prompt optimization is difficult and hinders downstream task performance. As a solution, the paper proposes a low-rank adaptation approach.

Key takeaways:
* Existing adaptation strategies, such as adapter layers and input layer optimization, have limitations that make them inefficient for real-time production scenarios.
* The paper proposes a low-rank adaptation approach as a solution to these limitations.

## 4 Our Method
LoRA significantly reduces memory usage and storage requirements when adapting pre-trained large language models. By using low-rank decomposition factors during training and quickly swapping out adaptations during prediction, LoRA offers faster training times and cost-effective switching between tasks. However, the inability to batch inputs with different trainable parameters in a single forward pass is a limitation.
 
Key takeaways:
* LoRA reduces memory and storage usage, and offers faster training times and cost-effective switching between tasks
* Low-rank decomposition factors are used during training and adaptations are quickly swapped during prediction
* One limitation is that inputs with different trainable parameters cannot be batched in a single forward pass.

## 5 Empirical Experiments
The LoRA approach is evaluated on various large language models including RoBERTa and GPT-2. Performance on tasks including conversational summarization and generation is compared against several baselines including FT, BitFit, PreEmbed, PreLayer, Adapter tuning and LoRA. For RoBERTa base model, LoRA showed improved performance on Task Transfer and NLU while reaching state-of-the-art accuracy for conversational summarization while for RoBERTa large model, LoRA obtains similar performance on downstream tasks to current adapter-based methods while reducing the number of trainable parameters.

Key takeaways:
* LoRA performs better than prior approaches and the fine-tuning baseline on RoBERTa models
* LoRA obtains similar performance on RoBERTa large model to current adapter-based methods while reducing the number of trainable parameters
* The paper evaluates the performance of different efficient adaptation approaches on pre-trained RoBERTa models and compares against several baselines.

## 6 Related Works
The paper "LoRA: Low-Rank Adaptation of Large Language Models" examines related works, including Transformer language models that are dominant in NLP, and prompt engineering and fine-tuning. Prior works include inserting adapter layers and optimizing input word embeddings, but LoRA differs by merging learned weights with main weights during inference without any latency. Low-rank structure is common in machine learning and useful for adversarial training, but the proposed low-rank adaptation has not been explored for adaptation to downstream tasks.

Key takeaways:
* Transformer language models have dominated NLP since their development in 2017.
* Prompt engineering seeks to maximize model performance on a given task through composing and formatting prompts.
* LoRA differs from other methods as learned weights can be merged with main weights during inference without any latency.

## 7 Understanding the Low-Rank Updates
The study explores low-rank adaptation of pre-trained large scale language models and its impact on downstream tasks. The authors determine that LoRA outperforms traditional fine-tuning in terms of parameter efficiency and maintained performances even with a small rank. The size of ΔW is smaller than W and increasing rank does not cover a more meaningful subspace. The low-rank structure does not adversely affect performances, and it potentially amplifies important features for specific downstream tasks. However, the study only covers the 48th layer of GPT-3, limiting its generalizability. 

Key takeaways:
* LoRA outperforms traditional fine-tuning in terms of parameter efficiency and maintained performance.
* Low-rank structure does not adversely affect performances and potentially amplifies important features for specific downstream tasks.
* The size of ΔW is smaller than W and increasing rank does not cover a more meaningful subspace.

## 8 Conclusion and Future Work
LoRA enables efficient fine-tuning of large language models without sacrificing quality or adding inference latency. Parameter sharing allows for quick task-switching, and the principles of LoRA are applicable to neural networks with dense layers. Future work may investigate combining LoRA with other efficient adaptation methods, refining weight matrix selection, understanding fine-tuning mechanisms, and exploring ΔW matrix rank-deficiency.

Key takeaways:
* LoRA permits efficient fine-tuning of large language models with no loss of quality or inference latency increases.
* LoRA principles are broadly applicable to neural networks with dense layers.
* Future research could combine LoRA with other efficient adaptation methods, refine weight matrix selection, improve understanding of fine-tuning mechanisms, and examine ΔW matrix singularity.

## Summary
LoRA is a more parameter- and compute-efficient method for adapting pre-trained language models to downstream tasks. It optimizes rank decomposition matrices of dense layers during adaptation while keeping pre-trained weights frozen, which reduces storage requirements and allows task-switching with small LoRA modules. The low-rank representation replaces task-specific parameter increment and achieves state-of-the-art accuracy in various RoBERTa and GPT-2 models for different tasks, including conversational summarization and generation.

Key takeaways:
* LoRA optimizes rank decomposition matrices of dense layers during adaptation while keeping pre-trained weights frozen.
* The low-rank representation reduces storage requirements and allows task-switching with small LoRA modules.
* LoRA achieves state-of-the-art accuracy in various RoBERTa and GPT-2 models for different tasks.

