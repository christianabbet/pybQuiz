import os
import argparse
import ollama
import numpy as np
from tqdm import tqdm
from typing import Optional
import umap

from pybquiz.db.base import UnifiedTSVDB
from pybquiz.db.base import TriviaTSVDB, TriviaQ
from pybquiz.viz import plot_umap, plot_chord


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

    
def main(args):

    # Get data and loader
    triviadb = UnifiedTSVDB()
    path_npz = os.path.join(args.cache, "embedding_trivia.npz")
    N = len(triviadb)
    
    # Load existing
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

    # Normalize entires
    z = z / np.linalg.norm(z, axis=1, keepdims=True)
    # print("umap ...")
    # z_umap = embed_umap(z=z)
    # plot_umap(z=z_umap, y=y, domain=domain)
    
    # print("Plot Circle")
    # plot_chord(z=z, y=y, domain=domain)
    
    # Fit LDA / KNN

    import numpy as np

    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    
    # Reduction
    pca = PCA(n_components=300)
    z_pca = pca.fit_transform(z)
    total = pca.explained_variance_ratio_.sum()
    print(total)
    
    # Test 
    
    kmeans = KMeans(n_clusters=10, random_state=0, n_init="auto")
    y_hat = kmeans.fit_predict(z_pca)
    
    from sklearn.mixture import GaussianMixture
    gm = GaussianMixture(n_components=10, random_state=0)
    gm.score(z_pca)
    r = gm.fit_predict(z_pca)
    r = gm.predict_proba(z_pca)


        
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
    