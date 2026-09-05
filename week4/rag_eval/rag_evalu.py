# ============================================================
# PART 1 — IMPORTS AND ENVIRONMENT
# ============================================================

import os
import json

from dotenv import load_dotenv

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    PayloadSchemaType,
)

from sentence_transformers import SentenceTransformer

from groq import Groq


# ============================================================
# PART 2 — LOAD ENVIRONMENT
# ============================================================

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ============================================================
# PART 3 — CONNECT TO QDRANT
# ============================================================

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

print("Connected to Qdrant Cloud!")


# ============================================================
# PART 4 — CREATE QDRANT COLLECTION
# ============================================================

COLLECTION_NAME = "rag_eval"
EMBEDDING_SIZE = 384


if client.collection_exists(COLLECTION_NAME):

    print(
        f"Deleting existing collection: {COLLECTION_NAME}"
    )

    client.delete_collection(
        COLLECTION_NAME
    )


client.create_collection(

    collection_name=COLLECTION_NAME,

    vectors_config=VectorParams(

        size=EMBEDDING_SIZE,

        distance=Distance.COSINE
    )
)


print(
    f"Created collection: {COLLECTION_NAME}"
)


# ============================================================
# PART 5 — CREATE CATEGORY INDEX
# ============================================================

client.create_payload_index(

    collection_name=COLLECTION_NAME,

    field_name="category",

    field_schema=PayloadSchemaType.KEYWORD
)


# ============================================================
# PART 6 — LOAD KNOWLEDGE
# ============================================================

with open(
    "knowledge.json",
    "r",
    encoding="utf-8"
) as f:

    documents = json.load(f)


print(
    f"Loaded {len(documents)} knowledge documents."
)


# ============================================================
# PART 7 — CREATE EMBEDDINGS
# ============================================================

print(
    "Loading embedding model..."
)


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


print(
    "Embedding model ready!"
)


texts = [
    document["text"]
    for document in documents
]


embeddings = model.encode(
    texts
)


print(
    f"Generated {len(embeddings)} embeddings."
)

print(
    f"Embedding size: {len(embeddings[0])}"
)


# ============================================================
# PART 8 — CREATE QDRANT POINTS
# ============================================================

points = []


for i in range(len(documents)):

    point = PointStruct(

        id=i + 1,

        vector=embeddings[i].tolist(),

        payload=documents[i]
    )

    points.append(point)


# ============================================================
# PART 9 — UPLOAD KNOWLEDGE TO QDRANT
# ============================================================

client.upsert(

    collection_name=COLLECTION_NAME,

    points=points
)


print(
    f"Uploaded {len(points)} documents to Qdrant!"
)


# ============================================================
# PART 10 — SEARCH QDRANT
# ============================================================

def search(query, top_k=3):

    query_vector = model.encode(
        query
    ).tolist()


    results = client.query_points(

        collection_name=COLLECTION_NAME,

        query=query_vector,

        limit=top_k,

        with_payload=True
    ).points


    return results


# ============================================================
# PART 11 — CONNECT TO GROQ
# ============================================================

groq_client = Groq(

    api_key=GROQ_API_KEY
)


# ============================================================
# PART 12 — ASK THE LLM
# ============================================================

def ask_llm(question, context):

    prompt = f"""
Answer the question using only the information
provided in the context.

Context:
{context}

Question:
{question}

If the answer is not present in the context,
say:

"I don't know based on the provided information."
"""


    response = groq_client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response.choices[0].message.content


# ============================================================
# PART 13 — GOLDEN DATASET
#
# Questions for which we know the correct answer.
# ============================================================

golden_dataset = [

    {
        "id": 1,

        "question":
            "How many vacation days do I get?",

        "ground_truth":
            "Employees in India receive 24 days of paid leave per year.",

        "expected_information":
            "The retrieved context should contain information that employees receive 24 days of paid leave per year."
    },


    {
        "id": 2,

        "question":
            "What is the work from home policy?",

        "ground_truth":
            "Employees work from the office three days every week on Tuesday, Wednesday and Thursday.",

        "expected_information":
            "The retrieved context should contain the hybrid work policy and the three office days: Tuesday, Wednesday and Thursday."
    },


    {
        "id": 3,

        "question":
            "How much internet reimbursement do employees receive?",

        "ground_truth":
            "Employees receive Rs 2000 per month for home internet reimbursement.",

        "expected_information":
            "The retrieved context should contain the Rs 2000 monthly internet reimbursement."
    },


    {
        "id": 4,

        "question":
            "When do promotions happen?",

        "ground_truth":
            "Promotions happen twice every year during March and September.",

        "expected_information":
            "The retrieved context should contain that promotions happen in March and September."
    },


    {
        "id": 5,

        "question":
            "What is the gym benefit?",

        "ground_truth":
            "Employees receive Rs 3000 every month for gym memberships or fitness apps.",

        "expected_information":
            "The retrieved context should contain the Rs 3000 monthly wellness benefit for gym or fitness apps."
    }
]


# ============================================================
# PART 14 — LLM AS A JUDGE
# ============================================================

def llm_judge(prompt):

    response = groq_client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_object"
        },

        temperature=0
    )


    return json.loads(
        response.choices[0].message.content
    )


# ============================================================
# PART 15 — CONTEXT PRECISION
#
# For every retrieved chunk, ask:
#
# "Is this chunk relevant to the question?"
#
# Precision =
#
# relevant retrieved chunks
# -------------------------
# total retrieved chunks
# ============================================================

def context_precision(
    question,
    retrieved_docs
):

    relevant_chunks = 0


    for i, doc in enumerate(
        retrieved_docs
    ):

        chunk = doc.payload["text"]


        prompt = f"""
You are evaluating the retrieval quality
of a RAG system.

Question:
{question}

Retrieved chunk:
{chunk}

Is this chunk relevant to answering
the question?

Return ONLY JSON:

{{
    "relevant": true,
    "reason": "short explanation"
}}

Return true if the chunk contains information
that is useful for answering the question.

Return false if it is unrelated.
"""


        result = llm_judge(prompt)


        if result["relevant"]:

            relevant_chunks += 1


    if len(retrieved_docs) == 0:

        return 0.0


    return (
        relevant_chunks
        /
        len(retrieved_docs)
    )


# ============================================================
# PART 16 — CONTEXT RECALL
#
# Did we retrieve the information needed
# to answer the question?
# ============================================================

def context_recall(
    question,
    context,
    ground_truth
):

    prompt = f"""
You are evaluating the retrieval quality
of a RAG system.

Question:
{question}

Ground Truth Answer:
{ground_truth}

Retrieved Context:
{context}

Does the retrieved context contain enough
information to produce the ground truth answer?

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = All important information needed for
      the answer is present.

0.7 = Most important information is present,
      but some details are missing.

0.5 = Some important information is present.

0.0 = The required information is absent.
"""


    result = llm_judge(
        prompt
    )


    return result


# ============================================================
# PART 17 — FAITHFULNESS
#
# Is the generated answer supported by
# the retrieved context?
# ============================================================

def evaluate_faithfulness(
    question,
    context,
    answer
):

    prompt = f"""
You are evaluating a RAG system.

Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{answer}

Determine whether the claims in the
generated answer are supported by
the retrieved context.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = All claims are supported.

0.7 = Mostly supported with minor issues.

0.5 = Some claims are supported.

0.0 = Unsupported or contradictory.
"""


    return llm_judge(
        prompt
    )


# ============================================================
# PART 18 — ANSWER RELEVANCY
# ============================================================

def evaluate_relevancy(
    question,
    answer
):

    prompt = f"""
You are evaluating a RAG system.

Question:
{question}

Generated Answer:
{answer}

Does the generated answer actually
answer the question?

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = Directly answers the question.

0.7 = Mostly answers the question.

0.5 = Partially answers the question.

0.0 = Completely off-topic.
"""


    return llm_judge(
        prompt
    )


# ============================================================
# PART 19 — ANSWER CORRECTNESS
# ============================================================

def evaluate_correctness(
    answer,
    ground_truth
):

    prompt = f"""
You are evaluating a RAG system.

Generated Answer:
{answer}

Ground Truth Answer:
{ground_truth}

Determine whether the generated answer
is factually correct compared with
the ground truth.

Return ONLY JSON:

{{
    "score": 0.0,
    "reason": "short explanation"
}}

Scoring:

1.0 = Completely correct.

0.7 = Mostly correct with minor omissions.

0.5 = Partially correct.

0.0 = Incorrect or contradictory.
"""


    return llm_judge(
        prompt
    )


# ============================================================
# PART 20 — RUN COMPLETE EVALUATION
# ============================================================

def run_evaluation():

    print("\n")

    print("=" * 70)

    print(
        "                    RAG EVALUATION"
    )

    print("=" * 70)


    all_scores = {

        "precision": [],

        "recall": [],

        "faithfulness": [],

        "relevancy": [],

        "correctness": []
    }


    # ========================================================
    # RUN EVERY GOLDEN QUESTION THROUGH THE REAL RAG
    # ========================================================

    for test in golden_dataset:

        question = test["question"]


        print("\n")

        print("-" * 70)

        print(
            f"QUESTION: {question}"
        )


        # ----------------------------------------------------
        # RETRIEVAL
        # ----------------------------------------------------

        results = search(
            question,
            top_k=3
        )


        # ----------------------------------------------------
        # DISPLAY RETRIEVED DOCUMENTS
        # ----------------------------------------------------

        print("\nRetrieved Documents:")


        for i, result in enumerate(
            results
        ):

            print(
                f"\nChunk {i + 1}"
            )

            print(
                f"Score: {result.score:.3f}"
            )

            print(
                result.payload["text"]
            )


        # ----------------------------------------------------
        # CREATE CONTEXT
        # ----------------------------------------------------

        context = "\n".join(

            result.payload["text"]

            for result in results
        )


        # ----------------------------------------------------
        # GENERATE ANSWER
        # ----------------------------------------------------

        answer = ask_llm(
            question,
            context
        )


        print("\nGenerated Answer:")

        print(answer)


        # ====================================================
        # METRIC 1 — CONTEXT PRECISION
        # ====================================================

        precision = context_precision(

            question,

            results
        )


        # ====================================================
        # METRIC 2 — CONTEXT RECALL
        # ====================================================

        recall_result = context_recall(

            question,

            context,

            test["ground_truth"]
        )


        recall = float(
            recall_result["score"]
        )


        # ====================================================
        # METRIC 3 — FAITHFULNESS
        # ====================================================

        faithfulness_result = (
            evaluate_faithfulness(

                question,

                context,

                answer
            )
        )


        faithfulness = float(
            faithfulness_result["score"]
        )


        # ====================================================
        # METRIC 4 — ANSWER RELEVANCY
        # ====================================================

        relevancy_result = evaluate_relevancy(

            question,

            answer
        )


        relevancy = float(
            relevancy_result["score"]
        )


        # ====================================================
        # METRIC 5 — ANSWER CORRECTNESS
        # ====================================================

        correctness_result = (
            evaluate_correctness(

                answer,

                test["ground_truth"]
            )
        )


        correctness = float(
            correctness_result["score"]
        )


        # ====================================================
        # SAVE SCORES
        # ====================================================

        all_scores["precision"].append(
            precision
        )

        all_scores["recall"].append(
            recall
        )

        all_scores["faithfulness"].append(
            faithfulness
        )

        all_scores["relevancy"].append(
            relevancy
        )

        all_scores["correctness"].append(
            correctness
        )


        # ====================================================
        # PRINT SCORES
        # ====================================================

        print("\nScores")

        print(
            f"Context Precision : {precision:.2f}"
        )

        print(
            f"Context Recall    : {recall:.2f}"
        )

        print(
            f"Faithfulness      : {faithfulness:.2f}"
        )

        print(
            f"Answer Relevancy  : {relevancy:.2f}"
        )

        print(
            f"Answer Correctness: {correctness:.2f}"
        )


        # ====================================================
        # DIAGNOSIS
        # ====================================================

        print("\nDiagnosis")


        if precision < 0.7:

            print(
                "❌ Retrieval is returning irrelevant chunks."
            )


        if recall < 0.7:

            print(
                "❌ Retrieval is missing important information."
            )


        if faithfulness < 0.7:

            print(
                "❌ Answer is not properly grounded."
            )


        if relevancy < 0.7:

            print(
                "❌ Answer is not sufficiently relevant."
            )


        if correctness < 0.7:

            print(
                "❌ Answer is not sufficiently correct."
            )


        if (
            precision >= 0.7
            and recall >= 0.7
            and faithfulness >= 0.7
            and relevancy >= 0.7
            and correctness >= 0.7
        ):

            print(
                "✅ Good RAG response."
            )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n")

    print("=" * 70)

    print(
        "                    FINAL SUMMARY"
    )

    print("=" * 70)


    for metric, values in all_scores.items():

        average = (
            sum(values)
            /
            len(values)
        )


        print(
            f"{metric.capitalize():20}: {average:.2f}"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_evaluation()