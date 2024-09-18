import os
import argparse
import ollama
import numpy as np
from tqdm import tqdm
from typing import Optional
import umap
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from pybquiz.db.base import UnifiedTSVDB
from pybquiz.db.base import TriviaTSVDB, TriviaQ
from pybquiz.viz import plot_umap, plot_chord


# def find_ood(z, quantils: Optional[float] = 0.95):
    
#     v_hat = z.min(axis=1)
#     ood_thresh = np.quantile(v_hat, quantils)
    
#     return v_hat > ood_thresh


# def kmean_score(z: np.ndarray, y: np.ndarray, n: Optional[int] = 10000):
    
#     # Estimation of score
#     id_est = np.random.permutation(y.shape[0])[:n]
#     y_est = y[id_est]
#     z_est = z[id_est]
#     k = len(np.unique(y))
    
#     S = []
#     for i in range(k):
#         # Inner similarity
#         z_in = z_est[y_est == i]
#         # Outter similarity
#         z_out = z_est[y_est != i]
#         # Averages
#         a = 1 - np.mean(z_in @ z_in.T - np.eye(z_in.shape[0]), axis=1)
#         b = 1 - np.mean(z_in @ z_out.T, axis=1)
#         s = (b-a) / np.max([a, b], axis=0)
#         S.extend(s)

#     return np.mean(S)


def embed_umap(
    z: np.ndarray, 
    M: Optional[int] = 5000, 
    seed: Optional[int] = 0,
):
    
    # Fit values   
    N = len(z) 
    reducer = umap.UMAP(random_state=seed)      
    rndState = np.random.RandomState(seed=seed)
    idrnd = rndState.permutation(N)[:M]
    
    print("Fit ...")
    reducer.fit(z[idrnd])
    print("Transform ...")
    z_umap = reducer.transform(z)
    return z_umap
    
    
def embed(
    dataset: TriviaTSVDB, 
    id_subset: list[int],
    model_name: Optional[str] = "mxbai-embed-large",
):

    # Get embedding size
    result = ollama.embeddings(model=model_name, prompt="test")
                    
    # Infer new ones
    N_new = len(id_subset)
    F = len(result.get("embedding", []))
    z = np.zeros((N_new, F))
    y = [None]*N_new
    uuid = [None]*N_new
    model = [None]*N_new
    
    for i in tqdm(range(N_new)):
        # Get prompt
        batch = dataset[id_subset[i]]
        result = ollama.embeddings(
            model=model_name,
            prompt=batch.get(TriviaQ.KEY_QUESTION, "error"),
        )
        # Append results
        z[i] = result.get("embedding", [])
        y[i] = batch.get(TriviaQ.KEY_CATEGORY, None)
        uuid[i] = batch.get(TriviaQ.KEY_UUID, None)
        model[i] = batch.get("domain", None)
        
    # Return output
    return z, y, uuid, model


def update_embed(triviadb, path_npz: str):
    
    z, y, uuid, domain = [], [], [], []
    
    if os.path.exists(path_npz):
        print("Load existing data ...")
        data = np.load(path_npz, allow_pickle=True)["data"].item()
        z = data["z"]
        y = data["y"]
        uuid = data["uuid"]
        domain = data["domain"]

    # Infer dummy
    print("Check existing data ...")
    exists = [d in uuid for d in triviadb.db[TriviaQ.KEY_UUID].values]
    id_subset = np.nonzero(np.logical_not(exists))[0]

    # Check if update is needed    
    if len(id_subset) != 0:
        # Get new embedding
        z_new, y_new, uuid_new, domain_new = embed(dataset=triviadb, model_name=args.model, id_subset=id_subset)
        # Append embedding
        z = np.concatenate([z, z_new], axis=0)
        y = np.concatenate([y, y_new], axis=0)
        uuid = np.concatenate([uuid, uuid_new], axis=0)
        domain = np.concatenate([domain, domain_new], axis=0)
        
        # Sanity check
        assert len(z) == len(y) and len(z) == len(uuid) and len(z) == len(domain)
                
        # Save output
        print("Saving ...")
        np.savez_compressed(path_npz, data={"z": z, "y": y, "uuid": uuid, "domain": domain})
    
    return z, y, uuid, domain
    
def o_ask_category(o_context: str, o_cats: str):

    # Get category
    o_question = "To which category does the context belong to? Chose between the following list: {}".format(o_cats)
    # Ask main categorys
    response = ollama.generate(
        model='llama3.1', 
        # prompt='Give me a general category title as well as a short description that mostly suits these questions: \n\n "{}"'.format(query)
        prompt="""
            Use the following pieces of context to answer the question at the end.
            \n\nContext: {}
            \n\nQuestion: {}
        """.format(o_context, o_question),
    )
    return response


def o_ask_link(o_context: str, o_link: str):

    # Get category
    o_question = "Is this context mainly linked to {} culture? Start your answer with \"yes\" or \"no\".".format(o_link)
    # Ask main categorys
    response = ollama.generate(
        model='llama3.1', 
        # prompt='Give me a general category title as well as a short description that mostly suits these questions: \n\n "{}"'.format(query)
        prompt="""
            Use the following pieces of context to answer the question at the end.
            \n\nContext: {}
            \n\nQuestion: {}
        """.format(o_context, o_question),
    )
    return response
        
    
def o_parse_categories(text: str, cats: list[str]):
    
    # Check occurence of text
    is_present = [c.lower() in text.lower() for c in cats]
    # Check if any
    if any(is_present):
        return "|".join(np.array(cats)[is_present].tolist())
    else:
        return None
    

def o_parse_link(text: str):
    
    if text.lower().startswith("no"):
        return 0
    elif text.lower().startswith("yes"):
        return 1
    else:
        return -1
    

def categorize(triviadb):
    
        
    # Predefined categories
    CATS = [
        "authors and literature", 
        "geography", 
        "history", 
        "music and arts", 
        "food and drink", 
        "science and technology", 
        "animals and nature", 
        "film and television", 
        "sports and leisure", 
        "video games",
        "traditions and culture", 
        "miscellaneous",
    ]
    n_chunks = 100
    txt_cats = ", ".join(CATS)

    # Get data and loader
    N = len(triviadb)
    
    for i, data in enumerate(tqdm(triviadb, desc="Parsing ...")):
        
        # Check existing infos
        id_loc = triviadb.db.index[i]
        # Get info
        o_context = data.get(TriviaQ.KEY_QUESTION, "")
        
        # All values should be finite
        o_is_category = triviadb.db.loc[id_loc, ["o_category"]].notnull().item()
        o_is_uk = triviadb.db.loc[id_loc, ["o_is_uk"]].notnull().item()
        o_is_usa = triviadb.db.loc[id_loc, ["o_is_usa"]].notnull().item()

        if not o_is_category:    
            # Parse answer
            response_cat = o_ask_category(o_context=o_context, o_cats=txt_cats)
            o_category = o_parse_categories(text = response_cat["response"], cats = CATS)
            triviadb.db.loc[id_loc, "o_category"] = o_category
        
        # Get link culture
        if not o_is_uk:    
            response_uk = o_ask_link(o_context=o_context, o_link="British")
            triviadb.db.loc[id_loc, "o_is_uk"] = o_parse_link(text=response_uk["response"])
            
        # Get link culture
        if not o_is_usa:    
            response_usa = o_ask_link(o_context=o_context, o_link="US American")
            triviadb.db.loc[id_loc, "o_is_usa"] = o_parse_link(text=response_usa["response"])       

        # Save update
        if (i%n_chunks) == 0:
            triviadb.save()

    # Clean wrong more than two cats
    n_cats = np.array([len(v) for v in triviadb.db["o_category"].fillna("").str.split("|").values])
    triviadb.db.loc[(n_cats > 2), "o_category"] = None
    
    # Clean language detections
    triviadb.db.loc[triviadb.db["o_is_uk"] == -1, "o_is_uk"] = None
    triviadb.db.loc[triviadb.db["o_is_usa"] == -1, "o_is_usa"] = None
    
    # Save output
    triviadb.save()
    

def main(args):

    
    triviadb = UnifiedTSVDB()
    
    # Get categories from database 
    # categorize(triviadb=triviadb)
    
    # Load existing
    path_npz = os.path.join(args.cache, "embedding_trivia.npz")
    z, y, uuid, domain = update_embed(triviadb=triviadb, path_npz=path_npz)

    # Normalize entires
    z = z / np.linalg.norm(z, axis=1, keepdims=True)
    
    print("umap ...")
    z_umap = embed_umap(z=z)
    plot_umap(z=z_umap, y=y, domain=domain)
    
#     # print("Plot Circle")
#     # plot_chord(z=z, y=y, domain=domain)
    y_hats = triviadb.db.set_index("uuid").loc[uuid]
    y_hat_cat = y_hats["o_category"].fillna("error").str.split("|").str[0].values
    y_hat_ukusa = y_hats["o_is_uk"].fillna(0.0) + 10*y_hats["o_is_usa"].fillna(0.0)
    # Define ood cluster
    # y_hat_label = np.array(["C{}".format(c) for c in y_hat])
    plot_umap(
        z=z_umap, 
        y=y_hat_cat, 
        domain=np.array(["Unique"]*len(domain)), 
        path="viz_embedding_ollama.png"
    )

    plot_umap(
        z=z_umap, 
        y=y_hat_ukusa.replace({0: "None", 1: "UK", 10: "USA", 11: "Both"}), 
        domain=np.array(["Unique"]*len(domain)), 
        path="viz_embedding_ukusa.png"
    )
    

        
if __name__ == '__main__':
    
    # Create parser
    parser = argparse.ArgumentParser(
        prog='Text embedding',
        description='Embed text for feature description',
    )
    parser.add_argument('--model', default="mxbai-embed-large",
                        choices=['mxbai-embed-large', 'nomic-embed-text', 'all-minilm'],
                        help='Default embedding model (https://ollama.com/blog/embedding-models).')
    parser.add_argument('--cache', default=".cache",
                        help='Reference file for trianing.')    
    args = parser.parse_args()
    
    main(args=args)
    